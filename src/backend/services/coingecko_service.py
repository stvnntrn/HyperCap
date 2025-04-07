import asyncio
import logging
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


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


async def append_supply_data(db: Session, binance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Append CoinGecko supply data to Binance ticker data for unique coin_abbrs."""
    # Get unique coin_abbrs from binance_data
    unique_abbrs = list({coin["coin_abbr"] for coin in binance_data})
    logger.debug(f"Fetching supply data for {len(unique_abbrs)} unique coin_abbrs")

    # Fetch supply data for these coins
    coingecko_data = await fetch_coingecko_supply_data(db, unique_abbrs)

    # Append to binance_data
    for coin in binance_data:
        cg_data = coingecko_data.get(coin["coin_abbr"], {})
        coin["coin_name"] = cg_data.get("coin_name", coin.get("coin_name"))
        coin["circulating_supply"] = cg_data.get("circulating_supply", coin.get("circulating_supply"))
        coin["total_supply"] = cg_data.get("total_supply", coin.get("total_supply"))
        coin["max_supply"] = cg_data.get("max_supply", coin.get("max_supply"))
        coin["market_cap"] = (
            coin["price_usdt"] * coin["circulating_supply"]
            if coin.get("price_usdt") and coin.get("circulating_supply")
            else coin.get("market_cap")
        )

    logger.info(f"Appended supply data to {len(binance_data)} Binance pairs")
    return binance_data
