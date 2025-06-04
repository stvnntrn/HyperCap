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


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_previous: bool
