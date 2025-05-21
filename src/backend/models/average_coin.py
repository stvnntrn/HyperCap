from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, Integer, String

from ..database import Base


class AverageCoinData(Base):
    __tablename__ = "average_coin_data"

    pair = Column(String, primary_key=True)  # e.g., "BTC/USDT"
    coin_name = Column(String, nullable=True)  # e.g., "Bitcoin"
    coin_abbr = Column(String, index=True)  # e.g., "BTC"
    quote_currency = Column(String, index=True)  # e.g., "USDT"
    price_usdt = Column(Float)  # Average price across exchanges
    price_change_percent = Column(Float)  # Average 24hr % change
    volume_24h = Column(Float)  # Sum of 24hr volume
    quote_volume_24h = Column(Float)  # Sum of 24hr quote volume
    market_cap = Column(Float, nullable=True)  # price_usdt * circulating_supply
    circulating_supply = Column(Float, nullable=True)  # From CoinGecko
    total_supply = Column(Float, nullable=True)  # From CoinGecko
    max_supply = Column(Float, nullable=True)  # From CoinGecko
    exchange_count = Column(Integer, nullable=True)  # Number of exchanges used
    last_updated = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
