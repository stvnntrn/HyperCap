from datetime import UTC, datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
