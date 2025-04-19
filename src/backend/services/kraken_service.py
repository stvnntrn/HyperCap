import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import KRAKEN_API_URL
from ..models.kraken_coin import KrakenCoinData

logger = logging.getLogger(__name__)


async def fetch_kraken_ticker_data(db: Session) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                # Fetch asset pairs
                pairs_response = await client.get(f"{KRAKEN_API_URL}/0/public/AssetPairs")
                pairs_response.raise_for_status()
                pairs_data = pairs_response.json().get("result", {})
                pair_names = ",".join(pairs_data.keys())  # e.g., "XXBTZUSD,XETHZUSD"

                # Fetch ticker data
                ticker_response = await client.get(f"{KRAKEN_API_URL}/0/public/Ticker", params={"pair": pair_names})
                ticker_response.raise_for_status()
                ticker_data = ticker_response.json().get("result", {})

                if not ticker_data:
                    logger.warning("Kraken returned empty ticker data")
                    return []

                logger.info(f"Fetched {len(ticker_data)} pairs from Kraken")
                return await process_ticker_data(db, ticker_data, pairs_data)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = 2**attempt
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Kraken API error: {str(e)}")
                    raise HTTPException(status_code=e.response.status_code, detail="Kraken API issue")
        logger.error("Max retries exceeded for Kraken API")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


async def process_ticker_data(
    db: Session, ticker_data: Dict[str, Any], pairs_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    # Build reference prices for USD conversion
    reference_prices = {}
    for pair, data in ticker_data.items():
        if pair.endswith("ZUSD") or pair.endswith("USD"):
            try:
                base = pairs_data.get(pair, {}).get("base", pair[:-4]).lstrip("X")
                price = float(data.get("c", [0])[0])  # Last close price
                reference_prices[base] = price
            except (ValueError, TypeError):
                logger.warning(f"Invalid USD price for {pair}")

    processed_pairs = []
    for pair, data in ticker_data.items():
        pair_info = pairs_data.get(pair, {})
        abbr = pair_info.get("base", pair[:-4]).lstrip("X")  # e.g., "XBT" -> "BTC"
        quote = pair_info.get("quote", pair[-4:]).lstrip("Z")  # e.g., "ZUSD" -> "USD"

        try:
            price = float(data.get("c", [0])[0])  # Last close price
            price_usdt = (
                price
                if quote in ["USD", "ZUSD"]
                else (price * reference_prices.get(quote, 0) if quote in reference_prices else None)
            )

            # Volume is base asset volume
            volume_24h = float(data.get("v", [0])[1])  # 24hr volume
            # Quote volume = volume * weighted average price
            weighted_avg_price = float(data.get("p", [0])[1])  # 24hr vwap
            quote_volume_24h = volume_24h * weighted_avg_price if volume_24h and weighted_avg_price else 0

            # Price change: (close - open) / open * 100
            open_price = float(data.get("o", 0))
            price_change = price - open_price if open_price else 0
            price_change_percent = (price_change / open_price * 100) if open_price and price_change else 0

            # Query existing supply data for market cap
            existing_coin = db.query(KrakenCoinData).filter(KrakenCoinData.pair == pair).first()
            circulating_supply = existing_coin.circulating_supply if existing_coin else None
            total_supply = existing_coin.total_supply if existing_coin else None

            market_cap = None
            if price_usdt:
                if circulating_supply is not None and circulating_supply > 0:
                    market_cap = price_usdt * circulating_supply
                elif total_supply is not None and total_supply > 0:
                    market_cap = price_usdt * total_supply
                    logger.debug(f"Used total_supply for market_cap of {pair}")

            pair_data = {
                "pair": pair,
                "coin_name": existing_coin.coin_name if existing_coin else None,
                "coin_abbr": abbr,
                "quote_currency": quote,
                "price": price,
                "price_usdt": price_usdt,
                "price_change": price_change,
                "price_change_percent": price_change_percent,
                "high_24h": float(data.get("h", [0])[1]),  # 24hr high
                "low_24h": float(data.get("l", [0])[1]),  # 24hr low
                "open_price_24h": open_price,
                "close_price_24h": price,  # Kraken’s "c" is last close
                "volume_24h": volume_24h,
                "quote_volume_24h": quote_volume_24h,
                "weighted_avg_price": weighted_avg_price,
                "market_cap": market_cap,
                "circulating_supply": circulating_supply,
                "total_supply": total_supply,
                "max_supply": existing_coin.max_supply if existing_coin else None,
                "last_updated": datetime.now(UTC),
            }
            processed_pairs.append(pair_data)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid data for {pair}: {str(e)}")

    logger.info(f"Processed {len(processed_pairs)} pairs from Kraken")
    return processed_pairs


async def get_kraken_price(pair: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{KRAKEN_API_URL}/0/public/Ticker", params={"pair": pair.upper()})
            response.raise_for_status()
            data = response.json().get("result", {})
            if not data:
                raise HTTPException(status_code=404, detail=f"No data for pair {pair}")
            pair_data = data.get(pair.upper())
            if not pair_data:
                raise HTTPException(status_code=404, detail=f"Pair {pair} not found")
            price = float(pair_data["c"][0])
            logger.info(f"Fetched real-time price for {pair}: {price}")
            return {"status": "success", "pair": pair, "price": price}
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching price for {pair}: {str(e)}")
            raise HTTPException(status_code=e.response.status_code, detail="Kraken API error")
