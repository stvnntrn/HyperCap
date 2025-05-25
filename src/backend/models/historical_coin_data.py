from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, Integer, String

from ..database import Base


class HistoricalCoinData(Base):
    __tablename__ = "historical_coin_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(255), index=True)  # CoinGecko ID (e.g., "bitcoin")
    exchange = Column(String(50), index=True)  # "binance", "kraken", "mexc", "coingecko"
    price_usdt = Column(Float)
    timestamp = Column(TIMESTAMP, index=True, default=lambda: datetime.now(UTC))
