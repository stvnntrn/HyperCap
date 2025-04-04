import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import BINANCE_24HR_URL, BINANCE_API_URL
from ..crud.coin import bulk_upsert_coins
from ..database import get_db

logger = logging.getLogger(__name__)


async def fetch_all_ticker_data() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.get(BINANCE_24HR_URL)
                response.raise_for_status()
                data = response.json()
                if not data:
                    logger.warning("Binance returned empty ticker data")
                    return []
                return data
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = 2**attempt
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Binance API error: {str(e)}")
                    raise HTTPException(status_code=e.response.status_code, detail="Binance API issue")
        logger.error("Max retries exceeded for Binance API")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


def process_ticker_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Step 1: Collect reference prices for conversion (USDT-based pairs)
    reference_prices = {}
    for item in data:
        symbol = item["symbol"]
        if symbol.endswith("USDT"):
            try:
                base = symbol[:-4]
                price = item.get("lastPrice")
                if price is not None:
                    reference_prices[base] = float(price)
                else:
                    logger.warning(f"Missing lastPrice for {symbol}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid price data for {symbol}: {str(e)}")

    # Step 2: Process pairs
    processed_coins = {}
    seen_bases = set()

    for item in data:
        symbol = item["symbol"]
        quote = symbol[-3:] if len(symbol) <= 6 else symbol[-4:]
        base = symbol[: -len(quote)]

        if base in seen_bases:
            continue

        try:
            price = float(item.get("lastPrice", 0))
            coin_data = {
                "symbol": symbol,
                "coin_name": base,
                "price_usdt": price,
                "price_change": float(item.get("priceChange", 0)),
                "price_change_percent": float(item.get("priceChangePercent", 0)),
                "high_24h": float(item.get("highPrice", 0)),
                "low_24h": float(item.get("lowPrice", 0)),
                "open_price_24h": float(item.get("openPrice", 0)),
                "close_price_24h": float(item.get("prevClosePrice", 0)),
                "volume_24h": float(item.get("volume", 0)),
                "quote_volume_24h": float(item.get("quoteVolume", 0)),
                "weighted_avg_price": float(item.get("weightedAvgPrice", 0)),
                "market_cap": 0.0,
                "circulating_supply": 0.0,
                "total_supply": 0.0,
                "max_supply": 0.0,
                "last_updated": datetime.now(UTC),
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid data for {symbol}: {str(e)}")
            continue

        # Priority: Direct stablecoin pairs
        if quote in ["USDT", "USDC", "FDUSD"]:
            processed_coins[base] = coin_data
            seen_bases.add(base)
        elif quote in reference_prices and base not in seen_bases:
            conversion_rate = reference_prices[quote]
            coin_data["price_usdt"] = price * conversion_rate
            coin_data["price_change"] = coin_data["price_change"] * conversion_rate
            coin_data["high_24h"] = coin_data["high_24h"] * conversion_rate
            coin_data["low_24h"] = coin_data["low_24h"] * conversion_rate
            coin_data["open_price_24h"] = coin_data["open_price_24h"] * conversion_rate
            coin_data["close_price_24h"] = coin_data["close_price_24h"] * conversion_rate
            coin_data["quote_volume_24h"] = coin_data["quote_volume_24h"] * conversion_rate
            coin_data["weighted_avg_price"] = coin_data["weighted_avg_price"] * conversion_rate
            processed_coins[base] = coin_data
            seen_bases.add(base)
        else:
            logger.debug(f"Skipping {symbol} - no stablecoin pair or reference price")

    return list(processed_coins.values())


async def fetch_and_store_ticker_data(db: Session = Depends(get_db)):
    try:
        ticker_data = await fetch_all_ticker_data()
        if not ticker_data:
            logger.info("No data to process")
            return
        processed_data = process_ticker_data(ticker_data)
        await bulk_upsert_coins(db, processed_data)  # Using await since it’s async in crud
        logger.info("Ticker data fetched and stored successfully")
    except Exception as e:
        logger.error(f"Error fetching and storing ticker data: {str(e)}")
        raise


async def get_crypto_price(symbol: str) -> Dict[str, Any]:
    symbol = symbol.upper()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BINANCE_API_URL, params={"symbol": symbol})
            response.raise_for_status()
            data = response.json()
            return {
                "status": "success",
                "symbol": data["symbol"],
                "price": float(data["price"]),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch {symbol}: {str(e)}")
            raise HTTPException(status_code=404, detail="Invalid symbol or Binance API issue")
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
