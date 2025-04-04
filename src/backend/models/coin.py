from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Float, String
from sqlalchemy.ext.declarative import declarative_base

from ..database import Base


class CoinData(Base):
    __tablename__ = "coin_data"

    symbol = Column(String, primary_key=True)
    coin_name = Column(String)
    price_usdt = Column(Float)
    price_change = Column(Float)
    price_change_percent = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    open_price_24h = Column(Float)
    close_price_24h = Column(Float)
    volume_24h = Column(Float)
    quote_volume_24h = Column(Float)
    weighted_avg_price = Column(Float)
    market_cap = Column(Float)
    circulating_supply = Column(Float)
    total_supply = Column(Float)
    max_supply = Column(Float)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)
