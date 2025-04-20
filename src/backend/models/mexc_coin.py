from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Column, Float, String

from ..database import Base


class MexCCoinData(Base):
    __tablename__ = "mexc_coin_data"

    pair = Column(String, primary_key=True)  # "BTCUSDT"
    coin_name = Column(String, nullable=True)  # NULL now, "Bitcoin" later
    coin_abbr = Column(String, index=True)  # "BTC"
    quote_currency = Column(String, index=True)  # "USDT"
    price = Column(Float)  # Raw price (e.g., 50000)
    price_usdt = Column(Float)  # Converted to USDT (e.g., 50000)
    price_change = Column(Float)  # 24hr price change
    price_change_percent = Column(Float)  # 24hr % change
    high_24h = Column(Float)  # 24hr high
    low_24h = Column(Float)  # 24hr low
    open_price_24h = Column(Float)  # 24hr open
    close_price_24h = Column(Float)  # 24hr close
    volume_24h = Column(Float)  # 24hr volume
    quote_volume_24h = Column(Float)  # 24hr quote volume
    weighted_avg_price = Column(Float)  # 24hr weighted avg
    market_cap = Column(Float, nullable=True)  # NULL now, price_usdt * circulating_supply later
    circulating_supply = Column(Float, nullable=True)  # NULL now, from CoinGecko later
    total_supply = Column(Float, nullable=True)  # NULL now, from CoinGecko later
    max_supply = Column(Float, nullable=True)  # NULL now, from CoinGecko later
    last_updated = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
