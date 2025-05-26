import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import COINGECKO_API_URL

logger = logging.getLogger(__name__)

# Rate limiter for CoinGecko (50 requests/minute)
_REQUESTS_PER_MINUTE = 50
_RATE_LIMIT_SEMAPHORE = asyncio.Semaphore(_REQUESTS_PER_MINUTE)


async def rate_limited_request(client: httpx.AsyncClient, url: str, params: Dict = None) -> Dict:
    async with _RATE_LIMIT_SEMAPHORE:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            await asyncio.sleep(60 / _REQUESTS_PER_MINUTE)  # Spread requests over a minute
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"CoinGecko API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail="CoinGecko API error")


async def fetch_coingecko_coin_list() -> Dict[str, str]:
    """Fetch CoinGecko coin list to map symbol to id."""
    async with httpx.AsyncClient() as client:
        data = await rate_limited_request(client, f"{COINGECKO_API_URL}/coins/list")
        symbol_to_id = {coin["symbol"].upper(): coin["id"] for coin in data}
        logger.info(f"Fetched {len(symbol_to_id)} coin mappings from CoinGecko")
        return symbol_to_id


async def fetch_coingecko_metadata(coin_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch metadata (name, supply, categories) for given coin IDs."""
    chunk_size = 100  # Reduced to stay within rate limits
    all_coins = {}
    async with httpx.AsyncClient() as client:
        for i in range(0, len(coin_ids), chunk_size):
            chunk = coin_ids[i : i + chunk_size]
            params = {
                "vs_currency": "usd",
                "ids": ",".join(chunk),
                "order": "market_cap_desc",
                "per_page": chunk_size,
                "page": 1,
                "sparkline": False,
            }
            try:
                data = await rate_limited_request(client, f"{COINGECKO_API_URL}/coins/markets", params)
                for coin in data:
                    symbol = coin["symbol"].upper()
                    all_coins[symbol] = {
                        "coin_name": coin["name"],
                        "circulating_supply": coin["circulating_supply"],
                        "total_supply": coin["total_supply"],
                        "max_supply": coin["max_supply"],
                        "categories": [cat for cat in coin.get("categories", []) if cat],
                    }
                logger.debug(f"Fetched metadata for {len(chunk)} coins")
            except HTTPException as e:
                logger.warning(f"Error fetching metadata for chunk {i // chunk_size + 1}: {str(e)}")
        return all_coins


async def fetch_coingecko_historical_data(db: Session, coin_id: str, days: str = "max") -> List[Dict[str, Any]]:
    """Fetch historical price data for a coin if missing in database."""
    async with httpx.AsyncClient() as client:
        try:
            latest = (
                db.query(HistoricalCoinData)
                .filter(HistoricalCoinData.coin_id == coin_id, HistoricalCoinData.exchange == "coingecko")
                .order_by(HistoricalCoinData.timestamp.desc())
                .first()
            )

            days_to_fetch = days
            if latest:
                time_diff = (datetime.now(UTC) - latest.timestamp).days
                days_to_fetch = str(max(1, time_diff))  # Fetch only missing days

            data = await rate_limited_request(
                client,
                f"{COINGECKO_API_URL}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days_to_fetch, "interval": "daily"},
            )
            historical_data = [
                {
                    "coin_id": coin_id,
                    "exchange": "coingecko",
                    "price_usdt": float(price[1]),
                    "timestamp": datetime.fromtimestamp(price[0] / 1000, UTC),
                }
                for price in data.get("prices", [])
            ]
            logger.info(f"Fetched {len(historical_data)} historical prices for {coin_id}")
            return historical_data
        except HTTPException as e:
            logger.warning(f"Error fetching historical data for {coin_id}: {str(e)}")
            return []
