from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class CoinBase(BaseModel):
    pair: str
    coin_name: Optional[str] = None
    coin_abbr: str
    quote_currency: str
    price: Optional[float] = None  # Optional for average_coin_data
    price_usdt: Optional[float] = None
    price_change: Optional[float] = None  # Optional for average_coin_data
    price_change_percent: Optional[float] = None
    high_24h: Optional[float] = None  # Optional for average_coin_data
    low_24h: Optional[float] = None  # Optional for average_coin_data
    open_price_24h: Optional[float] = None  # Optional for average_coin_data
    close_price_24h: Optional[float] = None  # Optional for average_coin_data
    volume_24h: Optional[float] = None
    quote_volume_24h: Optional[float] = None
    weighted_avg_price: Optional[float] = None  # Optional for average_coin_data
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    exchange_count: Optional[int] = None  # For average_coin_data
    last_updated: Optional[datetime] = None


class CoinCreate(CoinBase):
    pass


class CoinUpdate(CoinBase):
    pass


class CoinInDB(CoinBase):
    exchange_details: Optional[Dict[str, Dict[str, Optional[float]]]] = None  # For /marketcap/

    class Config:
        from_attributes = True
