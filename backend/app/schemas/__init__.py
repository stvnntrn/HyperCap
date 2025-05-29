"""
Schemas package initialization
"""

from .coin import CoinBase, CoinCreate, CoinResponse, CoinUpdate, ExchangePairInfo, MarketCapResponse
from .common import APIResponse, ErrorResponse, HealthResponse, PaginatedResponse
from .price_history import (
    PriceChangeResponse,
    PriceChartResponse,
    PriceHistoryBase,
    PriceHistoryCreate,
    PriceHistoryResponse,
    PricePoint,
)

__all__ = [
    # Coin schemas
    "CoinBase",
    "CoinCreate",
    "CoinUpdate",
    "CoinResponse",
    "ExchangePairInfo",
    "MarketCapResponse",
    # Common schemas
    "APIResponse",
    "PaginatedResponse",
    "HealthResponse",
    "ErrorResponse",
    # Price history schemas
    "PriceHistoryBase",
    "PriceHistoryCreate",
    "PriceHistoryResponse",
    "PricePoint",
    "PriceChartResponse",
    "PriceChangeResponse",
]
