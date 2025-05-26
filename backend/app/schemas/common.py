from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


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
