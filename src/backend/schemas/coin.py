from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CoinBase(BaseModel):
    pair: str
    coin_name: Optional[str] = None
    coin_abbr: str
    quote_currency: str
    price: float
    price_usdt: Optional[float] = None
    price_change: float
    price_change_percent: float
    high_24h: float
    low_24h: float
    open_price_24h: float
    close_price_24h: float
    volume_24h: float
    quote_volume_24h: float
    weighted_avg_price: float
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
