from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, String

from ..database import Base


class MexCCoinData(Base):
    __tablename__ = "mexc_coin_data"

    pair = Column(String, primary_key=True)  # e.g., "BTCUSDT"
    coin_abbr = Column(String, index=True)  # e.g., "BTC"
    quote_currency = Column(String, index=True)  # e.g., "USDT"
    price_usdt = Column(Float)  # Price in USDT
    volume_24h = Column(Float)  # 24hr volume
    quote_volume_24h = Column(Float)  # 24hr quote volume
    last_updated = Column(TIMESTAMP, index=True, default=lambda: datetime.now(UTC))
