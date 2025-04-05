import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import BINANCE_24HR_URL, BINANCE_API_URL
from ..crud.coin import get_coin  # Add this import

logger = logging.getLogger(__name__)


async def fetch_ticker_data(db: Session) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.get(BINANCE_24HR_URL)
                response.raise_for_status()
                data = response.json()
                if not data:
                    logger.warning("Binance returned empty ticker data")
                    return []
                return process_ticker_data(db, data)  # Pass db to process_ticker_data
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


def process_ticker_data(db: Session, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            # Fetch existing coin data from DB to preserve supply
            existing_coin = get_coin(db, symbol)
            circulating_supply = existing_coin.circulating_supply if existing_coin else 0.0
            total_supply = existing_coin.total_supply if existing_coin else 0.0
            max_supply = existing_coin.max_supply if existing_coin else 0.0

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
                "market_cap": price * circulating_supply if circulating_supply else 0.0,  # Recalculate
                "circulating_supply": circulating_supply,  # Preserve
                "total_supply": total_supply,  # Preserve
                "max_supply": max_supply,  # Preserve
                "last_updated": datetime.utcnow(),
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid data for {symbol}: {str(e)}")
            continue

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
            coin_data["market_cap"] = (
                coin_data["price_usdt"] * circulating_supply if circulating_supply else 0.0
            )  # Recalculate after conversion
            processed_coins[base] = coin_data
            seen_bases.add(base)
        else:
            logger.debug(f"Skipping {symbol} - no stablecoin pair or reference price")

    return list(processed_coins.values())


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
