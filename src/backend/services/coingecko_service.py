import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

COINGECKO_API_URL = os.getenv("COINGECKO_API_URL")


async def fetch_coingecko_coin_list() -> Dict[str, str]:
    """Fetch CoinGecko coin list to map symbol to id."""
    async with httpx.AsyncClient() as client:
        try:
            logger.debug("Fetching CoinGecko coin list")
            response = await client.get(f"{COINGECKO_API_URL}/coins/list")
            response.raise_for_status()
            data = response.json()
            # Map symbol (e.g., 'btc') to id (e.g., 'bitcoin')
            # Note: Some symbols may map to multiple IDs; we'll take the first match
            symbol_to_id = {coin["symbol"].upper(): coin["id"] for coin in data}
            logger.info(f"Fetched {len(symbol_to_id)} coin mappings from CoinGecko")
            return symbol_to_id
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching CoinGecko coin list: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail="CoinGecko API error")


async def fetch_coingecko_supply_data(db: Session, coin_abbrs: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch supply data from CoinGecko for specific coin_abbrs."""
    # Get mapping from symbol to CoinGecko id
    symbol_to_id = await fetch_coingecko_coin_list()

    # Convert coin_abbrs to CoinGecko IDs
    ids = [symbol_to_id.get(abbr) for abbr in coin_abbrs if symbol_to_id.get(abbr)]
    if not ids:
        logger.warning("No valid CoinGecko IDs found for provided coin_abbrs")
        return {}

    # Split into chunks of 250 (max per request)
    chunk_size = 250
    all_coins = {}
    async with httpx.AsyncClient() as client:
        for i in range(0, len(ids), chunk_size):
            chunk = ids[i : i + chunk_size]
            params = {
                "vs_currency": "usd",
                "ids": ",".join(chunk),  # e.g., "bitcoin,ethereum,vite"
                "order": "market_cap_desc",
                "per_page": chunk_size,
                "page": 1,
                "sparkline": False,
            }
            try:
                logger.debug(f"Fetching CoinGecko data for {len(chunk)} coins")
                response = await client.get(f"{COINGECKO_API_URL}/coins/markets", params=params)
                response.raise_for_status()
                data = response.json()

                for coin in data:
                    symbol = coin["symbol"].upper()
                    all_coins[symbol] = {
                        "coin_name": coin["name"],
                        "circulating_supply": coin["circulating_supply"],
                        "total_supply": coin["total_supply"],
                        "max_supply": coin["max_supply"],
                    }

                if len(chunk) > 1:  # Avoid delay on single request
                    await asyncio.sleep(1.2)  # ~50 requests/minute safety

            except httpx.HTTPStatusError as e:
                logger.error(f"Error fetching CoinGecko data: {e.response.status_code} - {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail="CoinGecko API error")

        logger.info(f"Fetched supply data for {len(all_coins)} coins from CoinGecko")
        return all_coins


async def fetch_coingecko_historical_data(db: Session, coin_id: str, days: int = 30) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{COINGECKO_API_URL}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days, "interval": "daily"},
            )
            response.raise_for_status()
            data = response.json()
            prices = data.get("prices", [])  # [[timestamp_ms, price], ...]
            historical_data = []
            for price in prices:
                timestamp = datetime.fromtimestamp(price[0] / 1000, UTC)
                historical_data.append(
                    {
                        "coin_id": coin_id,
                        "exchange": "coingecko",
                        "price_usdt": float(price[1]),
                        "timestamp": timestamp,
                    }
                )
            logger.info(f"Fetched {len(historical_data)} historical prices for {coin_id}")
            return historical_data
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e.response.status_code}")
            return []


async def append_supply_data(db: Session, binance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Append CoinGecko supply data to Binance ticker data for unique coin_abbrs."""
    unique_abbrs = list({coin["coin_abbr"] for coin in binance_data})
    logger.debug(f"Fetching supply data for {len(unique_abbrs)} unique coin_abbrs")

    coingecko_data = await fetch_coingecko_supply_data(db, unique_abbrs)

    for coin in binance_data:
        cg_data = coingecko_data.get(coin["coin_abbr"], {})
        coin["coin_name"] = cg_data.get("coin_name", coin.get("coin_name"))
        coin["circulating_supply"] = cg_data.get("circulating_supply", coin.get("circulating_supply"))
        coin["total_supply"] = cg_data.get("total_supply", coin.get("total_supply"))
        coin["max_supply"] = cg_data.get("max_supply", coin.get("max_supply"))

        # Calculate market_cap: prefer circulating_supply, fall back to total_supply
        price_usdt = coin.get("price_usdt")
        circulating_supply = coin["circulating_supply"]
        total_supply = coin["total_supply"]

        if price_usdt:
            if circulating_supply is not None and circulating_supply > 0:
                coin["market_cap"] = price_usdt * circulating_supply
            elif total_supply is not None and total_supply > 0:
                coin["market_cap"] = price_usdt * total_supply
                logger.debug(f"Used total_supply for market_cap of {coin['pair']} due to missing circulating_supply")
            else:
                coin["market_cap"] = None
                logger.warning(f"No supply data for {coin['pair']}, market_cap set to null")
        else:
            coin["market_cap"] = None  # No price_usdt, keep null

    logger.info(f"Appended supply data to {len(binance_data)} Binance pairs")
    return binance_data
