from datetime import UTC, datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, Index, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PriceHistory(Base):
    """
    Historical price data for charts and price change calculations
    """

    __tablename__ = "price_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)  # e.g., "BTC", "ETH"
    exchange = Column(String(20))  # "binance", "kraken", "mexc", "average"

    # Price data
    price_usd = Column(Float, nullable=False)
    volume_24h_usd = Column(Float)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_symbol_timestamp", "symbol", "timestamp"),
        Index("idx_symbol_exchange_timestamp", "symbol", "exchange", "timestamp"),
        Index("idx_timestamp", "timestamp"),
    )
