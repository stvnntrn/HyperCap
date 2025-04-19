import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import BINANCE_24HR_URL, BINANCE_API_URL
from ..models.binance_coin import BinanceCoinData

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
                logger.info(f"Fetched {len(data)} pairs from Binance")
                return await process_ticker_data(db, data)
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


async def fetch_exchange_info():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BINANCE_API_URL}/exchangeInfo")
            response.raise_for_status()
            data = response.json()
            return {s["symbol"]: {"base": s["baseAsset"], "quote": s["quoteAsset"]} for s in data["symbols"]}
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch exchange info: {str(e)}")
        return {}  # Return empty dict as fallback
    except Exception as e:
        logger.error(f"Unexpected error fetching exchange info: {str(e)}")
        return {}


async def process_ticker_data(db: Session, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Fetch exchange info for accurate pair splitting
    exchange_info = await fetch_exchange_info()

    # Build reference prices for USDT conversion
    reference_prices = {}
    for item in data:
        pair = item["symbol"]
        if pair.endswith("USDT"):
            try:
                base = exchange_info.get(pair, {}).get("base", pair[:-4])
                price = float(item.get("lastPrice", 0))
                reference_prices[base] = price
            except (ValueError, TypeError):
                logger.warning(f"Invalid USDT price for {pair}")

    processed_pairs = []
    for item in data:
        pair = item["symbol"]
        # Get base and quote from exchange info
        pair_info = exchange_info.get(pair, {})
        abbr = pair_info.get("base")
        quote = pair_info.get("quote")

        # Fallback if pair not in exchange info (unlikely, but safety net)
        if not abbr or not quote:
            logger.warning(f"Pair {pair} not found in exchange info, using fallback split")
            quote = pair[-4:] if len(pair) > 6 else pair[-3:]
            abbr = pair[: -len(quote)]

        try:
            price = float(item.get("lastPrice", 0))
            price_usdt = (
                price
                if quote == "USDT"
                else (price * reference_prices.get(quote, 0) if quote in reference_prices else None)
            )

            # Query existing circulating_supply from DB
            existing_coin = db.query(BinanceCoinData).filter(BinanceCoinData.pair == pair).first()
            circulating_supply = existing_coin.circulating_supply if existing_coin else None
            market_cap = price_usdt * circulating_supply if price_usdt and circulating_supply else None

            pair_data = {
                "pair": pair,
                "coin_name": existing_coin.coin_name if existing_coin else None,  # Preserve existing
                "coin_abbr": abbr,
                "quote_currency": quote,
                "price": price,
                "price_usdt": price_usdt,
                "price_change": float(item.get("priceChange", 0)),
                "price_change_percent": float(item.get("priceChangePercent", 0)),
                "high_24h": float(item.get("highPrice", 0)),
                "low_24h": float(item.get("lowPrice", 0)),
                "open_price_24h": float(item.get("openPrice", 0)),
                "close_price_24h": float(item.get("prevClosePrice", 0)),
                "volume_24h": float(item.get("volume", 0)),
                "quote_volume_24h": float(item.get("quoteVolume", 0)),
                "weighted_avg_price": float(item.get("weightedAvgPrice", 0)),
                "market_cap": market_cap,  # Recalculated with new price_usdt
                "circulating_supply": circulating_supply,  # Preserve existing
                "total_supply": existing_coin.total_supply if existing_coin else None,  # Preserve
                "max_supply": existing_coin.max_supply if existing_coin else None,  # Preserve
                "last_updated": datetime.now(UTC),
            }
            processed_pairs.append(pair_data)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid data for {pair}: {str(e)}")
    logger.info(f"Processed {len(processed_pairs)} pairs from Binance")
    return processed_pairs


async def get_crypto_price(pair: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BINANCE_API_URL}/ticker/price", params={"symbol": pair.upper()})
            response.raise_for_status()
            data = response.json()
            price = float(data["price"])
            logger.info(f"Fetched real-time price for {pair}: {price}")
            return {"status": "success", "pair": pair, "price": price}
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching price for {pair}: {str(e)}")
            raise HTTPException(status_code=e.response.status_code, detail="Binance API error")
