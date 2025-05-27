from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.coin import CoinResponse
from app.schemas.common import APIResponse, HealthResponse, PaginatedResponse
from app.services.coin_service import CoinService

router = APIRouter()

# ==================== HEALTH CHECK ====================


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return HealthResponse(status="healthy", timestamp=datetime.now(UTC).isoformat(), database="connected")
    except Exception as e:
        return HealthResponse(status="unhealthy", timestamp=datetime.now(UTC).isoformat(), database=f"error: {str(e)}")

    # ==================== COIN ENDPOINTS ====================


@router.get("/coins", response_model=PaginatedResponse[CoinResponse])
async def get_coins(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("market_cap_rank", description="Sort field"),
    sort_desc: bool = Query(False, description="Sort descending"),
    search: Optional[str] = Query(None, description="Search coins by name or symbol"),
    db: Session = Depends(get_db),
):
    """Get paginated list of coins"""
    coin_service = CoinService(db)

    # Calculate offset
    skip = (page - 1) * size

    try:
        if search:
            # Search functionality
            coins = coin_service.search_coins(search, limit=size)
            total = len(coins)
        else:
            # Regular pagination
            coins = coin_service.get_coins(skip=skip, limit=size, sort_by=sort_by, sort_desc=sort_desc)
            total = coin_service.get_total_coins()

        # Convert to response format
        coin_responses = []
        for coin in coins:
            coin_dict = coin_service.get_coin_with_exchange_pairs(coin.symbol)
            if coin_dict:
                coin_responses.append(CoinResponse(**coin_dict))

        # Calculate pagination info
        total_pages = (total + size - 1) // size
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedResponse(
            items=coin_responses,
            total=total,
            page=page,
            size=size,
            pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coins: {str(e)}")


@router.get("/coins/{symbol}", response_model=APIResponse[CoinResponse])
async def get_coin(symbol: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific coin"""
    coin_service = CoinService(db)

    try:
        coin_data = coin_service.get_coin_with_exchange_pairs(symbol.upper())

        if not coin_data:
            raise HTTPException(status_code=404, detail=f"Coin {symbol.upper()} not found")

        return APIResponse(
            success=True, data=CoinResponse(**coin_data), message=f"Coin {symbol.upper()} retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coin: {str(e)}")
