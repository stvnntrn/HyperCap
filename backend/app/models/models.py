from datetime import UTC, datetime

from sqlalchemy import DECIMAL, JSON, BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String

from app.database import Base


class Coin(Base):
    """
    Main coin table storing aggregated data across exchanges
    """

    __tablename__ = "coins"

    # Primary identification
    symbol = Column(String(20), primary_key=True)  # e.g., "BTC", "ETH"
    name = Column(String(100))  # e.g., "Bitcoin", "Ethereum"

    # Price data (aggregated across exchanges)
    price_usd = Column(Float)  # Current average price in USD
    price_24h_high = Column(Float)  # 24h highest price
    price_24h_low = Column(Float)  # 24h lowest price

    # Price changes
    price_change_1h = Column(Float)  # % change in 1 hour
    price_change_24h = Column(Float)  # % change in 24 hours
    price_change_7d = Column(Float)  # % change in 7 days

    # Volume data (sum across exchanges)
    volume_24h_usd = Column(Float)  # 24h trading volume in USD
    volume_24h_base = Column(Float)  # 24h base asset volume

    # Market data from CoinGecko
    market_cap = Column(Float)  # Market capitalization
    circulating_supply = Column(Float)  # Circulating supply
    total_supply = Column(Float)  # Total supply
    max_supply = Column(Float)  # Maximum supply

    # Metadata
    categories = Column(JSON)  # ["layer-1", "smart-contracts"]
    market_cap_rank = Column(Integer)  # Market cap ranking
    exchange_count = Column(Integer)  # Number of exchanges tracked

    # Timestamps
    last_updated = Column(DateTime, default=lambda: datetime.now(UTC))

    # Indexes for performance
    __table_args__ = (
        Index("idx_market_cap", "market_cap"),
        Index("idx_volume", "volume_24h_usd"),
        Index("idx_last_updated", "last_updated"),
    )


class ExchangePair(Base):
    """
    Track which trading pairs are available on which exchanges
    """

    __tablename__ = "exchange_pairs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("coins.symbol"), nullable=False)  # e.g., "BTC"
    exchange = Column(String(20), nullable=False)  # "binance", "kraken", "mexc"
    pair = Column(String(30), nullable=False)  # "BTC/USDT", "XBTUSD"
    quote_currency = Column(String(10), nullable=False)  # "USDT", "USD", "EUR"
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=lambda: datetime.now(UTC))

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_exchange_pairs_symbol", "symbol"),
        Index("idx_exchange_pairs_exchange", "exchange"),
        Index("idx_exchange_pairs_active", "is_active"),
    )


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
