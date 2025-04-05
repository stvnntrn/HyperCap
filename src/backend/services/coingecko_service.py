import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..crud.coin import get_coin

logger = logging.getLogger(__name__)


async def fetch_supply_data(db: Session) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250&page=1"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if not data:
                logger.warning("CoinGecko returned empty supply data")
                return []

            supply_data = []
            for coin in data:
                symbol = coin["symbol"].upper() + "USDT"
                existing_coin = get_coin(db, symbol)
                if existing_coin:
                    supply_data.append(
                        {
                            "symbol": symbol,
                            "coin_name": coin["symbol"].upper(),
                            "price_usdt": existing_coin.price_usdt,
                            "price_change": existing_coin.price_change,
                            "price_change_percent": existing_coin.price_change_percent,
                            "high_24h": existing_coin.high_24h,
                            "low_24h": existing_coin.low_24h,
                            "open_price_24h": existing_coin.open_price_24h,
                            "close_price_24h": existing_coin.close_price_24h,
                            "volume_24h": existing_coin.volume_24h,
                            "quote_volume_24h": existing_coin.quote_volume_24h,
                            "weighted_avg_price": existing_coin.weighted_avg_price,
                            "market_cap": (existing_coin.price_usdt or 0) * (coin["circulating_supply"] or 0),
                            "circulating_supply": coin["circulating_supply"] or 0,
                            "total_supply": coin["total_supply"] or 0,
                            "max_supply": coin["max_supply"] or 0,
                            "last_updated": datetime.utcnow(),
                        }
                    )
            return supply_data
        except Exception as e:
            logger.error(f"CoinGecko API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"CoinGecko API issue: {str(e)}")
