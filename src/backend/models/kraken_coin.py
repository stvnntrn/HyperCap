from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, String

from ..database import Base


class KrakenCoinData(Base):
    __tablename__ = "kraken_coin_data"

    pair = Column(String, primary_key=True)  # e.g., "XBTUSD"
    coin_abbr = Column(String, index=True)  # e.g., "BTC"
    quote_currency = Column(String, index=True)  # e.g., "USD"
    price_usdt = Column(Float)  # Price in USDT
    volume_24h = Column(Float)  # 24hr volume
    quote_volume_24h = Column(Float)  # 24hr quote volume
    last_updated = Column(TIMESTAMP, index=True, default=lambda: datetime.now(UTC))
