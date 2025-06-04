from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

# ==================== COMMON SCHEMAS ====================


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""

    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""

    page: int = 1
    size: int = 100
    sort_by: str = "market_cap_rank"
    sort_desc: bool = False

    class Config:
        schema_extra = {"example": {"page": 1, "size": 100, "sort_by": "market_cap_rank", "sort_desc": False}}


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_previous: bool


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = "healthy"
    timestamp: str
    database: str = "connected"

    class Config:
        schema_extra = {"example": {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z", "database": "connected"}}


class ErrorResponse(BaseModel):
    """Error response schema"""

    success: bool = False
    error: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "NOT_FOUND",
                "message": "Coin not found",
                "details": {"symbol": "INVALID"},
            }
        }


# ==================== COIN SCHEMAS ====================


class CoinBase(BaseModel):
    """Base coin schema with common fields"""

    symbol: str = Field(..., max_length=20, description="Coin symbol (e.g., BTC)")
    name: Optional[str] = Field(None, max_length=100, description="Coin name (e.g., Bitcoin)")
    price_usd: Optional[Decimal] = Field(None, description="Current price in USD")
    price_24h_high: Optional[Decimal] = Field(None, description="24h highest price")
    price_24h_low: Optional[Decimal] = Field(None, description="24h lowest price")
    price_change_1h: Optional[Decimal] = Field(None, description="1h price change %")
    price_change_24h: Optional[Decimal] = Field(None, description="24h price change %")
    price_change_7d: Optional[Decimal] = Field(None, description="7d price change %")
    volume_24h_usd: Optional[Decimal] = Field(None, description="24h volume in USD")
    volume_24h_base: Optional[Decimal] = Field(None, description="24h base volume")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    total_supply: Optional[Decimal] = Field(None, description="Total supply")
    max_supply: Optional[Decimal] = Field(None, description="Maximum supply")
    categories: Optional[List[str]] = Field(None, description="Coin categories")
    market_cap_rank: Optional[int] = Field(None, description="Market cap ranking")
    exchange_count: Optional[int] = Field(None, description="Number of exchanges")


class CoinCreate(CoinBase):
    """Schema for creating a new coin"""

    symbol: str = Field(..., description="Coin symbol is required")


class CoinUpdate(BaseModel):
    """Schema for updating coin data (all fields optional)"""

    name: Optional[str] = None
    price_usd: Optional[Decimal] = None
    price_24h_high: Optional[Decimal] = None
    price_24h_low: Optional[Decimal] = None
    price_change_1h: Optional[Decimal] = None
    price_change_24h: Optional[Decimal] = None
    price_change_7d: Optional[Decimal] = None
    volume_24h_usd: Optional[Decimal] = None
    volume_24h_base: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    circulating_supply: Optional[Decimal] = None
    total_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    categories: Optional[List[str]] = None
    market_cap_rank: Optional[int] = None
    exchange_count: Optional[int] = None


class ExchangePairInfo(BaseModel):
    """Exchange pair information for coin details"""

    exchange: str
    pair: str
    quote_currency: str
    is_active: bool = True


class CoinResponse(CoinBase):
    """Schema for coin API responses"""

    last_updated: Optional[datetime] = None
    exchange_pairs: Optional[List[ExchangePairInfo]] = Field(None, description="Available trading pairs")

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: float(v) if v is not None else None}


class CoinListResponse(BaseModel):
    """Schema for paginated coin list responses"""

    coins: List[CoinResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool


class MarketCapResponse(BaseModel):
    """Schema for market cap rankings"""

    rank: int
    symbol: str
    name: str
    price_usd: Decimal
    price_change_24h: Optional[Decimal]
    market_cap: Decimal
    volume_24h_usd: Optional[Decimal]

    class Config:
        json_encoders = {Decimal: lambda v: float(v) if v is not None else None}


# ==================== PRICE HISTORY SCHEMAS ====================


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


# ==================== ADMIN SCHEMAS ====================


class SystemStatus(BaseModel):
    """System status schema for admin endpoints"""

    system_health: str
    database_initialized: bool
    total_coins: int
    recent_price_updates: int
    total_price_records: int
    metadata_stats: Dict[str, Any]
    recommendations: List[str]
    last_check: str


class BackfillRequest(BaseModel):
    """Request schema for historical data backfill"""

    days_back: str = Field("max", description="'max' for all data or number of days")
    pause_real_time: bool = Field(True, description="Pause real-time fetching during backfill")


class BackfillResponse(BaseModel):
    """Response schema for backfill operations"""

    operation: str
    total_coins: int
    processed: int
    successful: int
    failed: int
    completion_time: str

    # ==================== WEBSOCKET SCHEMAS ====================


class PriceUpdate(BaseModel):
    """Real-time price update for WebSocket"""

    symbol: str
    price: float
    change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MarketUpdate(BaseModel):
    """Market-wide update for WebSocket"""

    total_market_cap: float
    total_volume_24h: float
    top_gainers: List[str]
    top_losers: List[str]
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
