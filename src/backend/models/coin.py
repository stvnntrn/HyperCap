from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, String

from ..database import Base  # ✅ Import from database.py


class CoinData(Base):
    __tablename__ = "coin_data"

    symbol = Column(String, primary_key=True, index=True)
    coin_name = Column(String, nullable=True)
    price_usdt = Column(Float, nullable=False)
    price_change = Column(Float, nullable=True)
    price_change_percent = Column(Float, nullable=True)
    high_24h = Column(Float, nullable=True)
    low_24h = Column(Float, nullable=True)
    open_price_24h = Column(Float, nullable=True)
    close_price_24h = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    quote_volume_24h = Column(Float, nullable=True)
    weighted_avg_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    circulating_supply = Column(Float, nullable=True)
    total_supply = Column(Float, nullable=True)
    max_supply = Column(Float, nullable=True)
    last_updated = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
