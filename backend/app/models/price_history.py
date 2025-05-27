from datetime import UTC, datetime

from sqlalchemy import DECIMAL, BigInteger, Column, DateTime, Index, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PriceHistoryRaw(Base):
    """
    Raw price data from exchanges (30-second intervals)
    Retention: 24 hours
    """

    __tablename__ = "price_history_raw"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)  # e.g., "BTC", "ETH"
    exchange = Column(String(20), nullable=False)  # "binance", "kraken", "mexc", "average"
    price_usd = Column(DECIMAL(20, 8), nullable=False)
    volume_24h_usd = Column(DECIMAL(20, 2))
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        Index("idx_price_raw_symbol_time", "symbol", "timestamp"),
        Index("idx_price_raw_exchange_time", "symbol", "exchange", "timestamp"),
    )


class PriceHistory5m(Base):
    """
    5-minute OHLC aggregates
    Retention: 1 week
    """

    __tablename__ = "price_history_5m"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    price_open = Column(DECIMAL(20, 8), nullable=False)
    price_close = Column(DECIMAL(20, 8), nullable=False)
    price_high = Column(DECIMAL(20, 8), nullable=False)
    price_low = Column(DECIMAL(20, 8), nullable=False)
    volume_sum = Column(DECIMAL(20, 2))
    timestamp = Column(DateTime, nullable=False)  # Window start time

    __table_args__ = (
        Index("idx_price_5m_symbol_time", "symbol", "timestamp"),
        Index("idx_price_5m_exchange_time", "symbol", "exchange", "timestamp"),
    )


class PriceHistory1h(Base):
    """
    1-hour OHLC aggregates
    Retention: 1 month
    """

    __tablename__ = "price_history_1h"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    price_open = Column(DECIMAL(20, 8), nullable=False)
    price_close = Column(DECIMAL(20, 8), nullable=False)
    price_high = Column(DECIMAL(20, 8), nullable=False)
    price_low = Column(DECIMAL(20, 8), nullable=False)
    volume_sum = Column(DECIMAL(20, 2))
    timestamp = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_price_1h_symbol_time", "symbol", "timestamp"),
        Index("idx_price_1h_exchange_time", "symbol", "exchange", "timestamp"),
    )


class PriceHistory1d(Base):
    """
    1-day OHLC aggregates
    Retention: 1 year
    """

    __tablename__ = "price_history_1d"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    price_open = Column(DECIMAL(20, 8), nullable=False)
    price_close = Column(DECIMAL(20, 8), nullable=False)
    price_high = Column(DECIMAL(20, 8), nullable=False)
    price_low = Column(DECIMAL(20, 8), nullable=False)
    volume_sum = Column(DECIMAL(20, 2))
    timestamp = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_price_1d_symbol_time", "symbol", "timestamp"),
        Index("idx_price_1d_exchange_time", "symbol", "exchange", "timestamp"),
    )


class PriceHistory1w(Base):
    """
    1-week OHLC aggregates
    Retention: Forever
    """

    __tablename__ = "price_history_1w"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    price_open = Column(DECIMAL(20, 8), nullable=False)
    price_close = Column(DECIMAL(20, 8), nullable=False)
    price_high = Column(DECIMAL(20, 8), nullable=False)
    price_low = Column(DECIMAL(20, 8), nullable=False)
    volume_sum = Column(DECIMAL(20, 2))
    timestamp = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_price_1w_symbol_time", "symbol", "timestamp"),
        Index("idx_price_1w_exchange_time", "symbol", "exchange", "timestamp"),
    )


# Keep original model for backward compatibility (will be migrated)
class PriceHistory(Base):
    """
    DEPRECATED: Use PriceHistoryRaw instead
    This will be migrated to the new time-series structure
    """

    __tablename__ = "price_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20))
    price_usd = Column(DECIMAL(20, 8), nullable=False)
    volume_24h_usd = Column(DECIMAL(20, 2))
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        Index("idx_price_history_symbol_timestamp", "symbol", "timestamp"),
        Index("idx_price_history_symbol_exchange_timestamp", "symbol", "exchange", "timestamp"),
    )
