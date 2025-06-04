"""
Schemas package initialization
"""

from .schemas import (
    # Common schemas
    APIResponse,
    BackfillRequest,
    BackfillResponse,
    # Coin schemas
    CoinBase,
    CoinCreate,
    CoinListResponse,
    CoinResponse,
    CoinUpdate,
    ErrorResponse,
    ExchangePairInfo,
    HealthResponse,
    MarketCapResponse,
    MarketUpdate,
    PaginatedResponse,
    PaginationParams,
    PriceChangeResponse,
    PriceChartResponse,
    # Price history schemas
    PriceHistoryBase,
    PriceHistoryCreate,
    PriceHistoryResponse,
    PricePoint,
    # WebSocket schemas
    PriceUpdate,
    # Admin schemas
    SystemStatus,
)

__all__ = [
    # Common
    "APIResponse",
    "PaginationParams",
    "PaginatedResponse",
    "HealthResponse",
    "ErrorResponse",
    # Coins
    "CoinBase",
    "CoinCreate",
    "CoinUpdate",
    "CoinResponse",
    "CoinListResponse",
    "ExchangePairInfo",
    "MarketCapResponse",
    # Price history
    "PriceHistoryBase",
    "PriceHistoryCreate",
    "PriceHistoryResponse",
    "PricePoint",
    "PriceChartResponse",
    "PriceChangeResponse",
    # Admin
    "SystemStatus",
    "BackfillRequest",
    "BackfillResponse",
    # WebSocket
    "PriceUpdate",
    "MarketUpdate",
]
