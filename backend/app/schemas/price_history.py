from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class PriceHistoryBase(BaseModel):
    """Base price history schema"""

    symbol: str = Field(..., max_length=20, description="Coin symbol")
    exchange: Optional[str] = Field(None, max_length=20, description="Exchange name or 'average'")
    price_usd: Decimal = Field(..., description="Price in USD")
    volume_24h_usd: Optional[Decimal] = Field(None, description="24h volume in USD")


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating price history entry"""

    pass


class PriceHistoryResponse(PriceHistoryBase):
    """Schema for price history API responses"""

    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: float(v) if v is not None else None}


class PricePoint(BaseModel):
    """Simple price point for charts"""

    timestamp: datetime
    price: float
    volume: Optional[float] = None


class PriceChartResponse(BaseModel):
    """Schema for price chart data"""

    symbol: str
    exchange: str
    timeframe: str  # "1h", "24h", "7d", "30d", "1y"
    data: List[PricePoint]

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PriceChangeResponse(BaseModel):
    """Schema for price change calculations"""

    symbol: str
    current_price: float
    price_change_1h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_7d: Optional[float] = None
    price_change_30d: Optional[float] = None

    class Config:
        json_encoders = {Decimal: lambda v: float(v) if v is not None else None}
