from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CoinBase(BaseModel):
    symbol: str
    coin_name: Optional[str] = None
    price_usdt: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    open_price_24h: Optional[float] = None
    close_price_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    quote_volume_24h: Optional[float] = None
    weighted_avg_price: Optional[float] = None
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    last_updated: Optional[datetime] = None


class CoinCreate(CoinBase):
    pass


class CoinUpdate(CoinBase):
    pass


class CoinInDB(CoinBase):
    class Config:
        from_attributes = True
