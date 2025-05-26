from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class CoinBase(BaseModel):
    pair: str
    coin_name: Optional[str] = None
    coin_abbr: str
    quote_currency: str
    price_usdt: Optional[float] = None
    change_1h: Optional[float] = None
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None
    volume_24h: Optional[float] = None
    quote_volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    categories: Optional[List[str]] = None
    exchange_count: Optional[int] = None
    last_updated: Optional[datetime] = None


class CoinCreate(CoinBase):
    pass


class CoinUpdate(CoinBase):
    pass


class CoinInDB(CoinBase):
    exchange_details: Optional[Dict[str, Dict[str, Optional[float]]]] = None  # For /marketcap/

    class Config:
        from_attributes = True
