from datetime import UTC, datetime

from sqlalchemy import JSON, TIMESTAMP, Column, Float, Integer, String

from ..database import Base


class CoinData(Base):
    __tablename__ = "coin_data"

    pair = Column(String, primary_key=True)  # e.g., "BTC/USDT"
    coin_name = Column(String, nullable=True)  # e.g., "Bitcoin"
    coin_abbr = Column(String, index=True)  # e.g., "BTC"
    quote_currency = Column(String, index=True)  # e.g., "USDT"
    price_usdt = Column(Float)  # Average price across exchanges
    change_1h = Column(Float, nullable=True)  # 1-hour price change %
    change_24h = Column(Float, nullable=True)  # 24-hour price change %
    change_7d = Column(Float, nullable=True)  # 7-day price change %
    volume_24h = Column(Float)  # Sum of 24hr volume
    quote_volume_24h = Column(Float)  # Sum of 24hr quote volume
    market_cap = Column(Float, nullable=True)  # price_usdt * circulating_supply
    circulating_supply = Column(Float, nullable=True)  # From CoinGecko
    total_supply = Column(Float, nullable=True)  # From CoinGecko
    max_supply = Column(Float, nullable=True)  # From CoinGecko
    categories = Column(JSON, nullable=True)  # e.g., ["cryptocurrency", "layer-1"]
    exchange_count = Column(Integer, nullable=True)  # Number of exchanges used
    last_updated = Column(TIMESTAMP, index=True, default=lambda: datetime.now(UTC))
