from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, Integer, String

from ..database import Base


class HistoricalCoinData(Base):
    __tablename__ = "historical_coin_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String, index=True)  # CoinGecko ID (e.g., "bitcoin")
    exchange = Column(String)  # "coingecko" or exchange name
    price_usdt = Column(Float)
    timestamp = Column(TIMESTAMP, index=True, default=lambda: datetime.now(UTC))
