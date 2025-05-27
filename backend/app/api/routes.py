from datetime import UTC, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.coin import CoinResponse, MarketCapResponse
from app.schemas.common import APIResponse, HealthResponse, PaginatedResponse
from app.schemas.price_history import PriceChartResponse, PricePoint
from app.services.coin_service import CoinService
from app.services.coingecko_service import CoinGeckoService
from app.services.exchange_service import ExchangeService
from app.services.price_service import PriceService

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


# ==================== MARKET DATA ENDPOINTS ====================


@router.get("/market-cap", response_model=PaginatedResponse[MarketCapResponse])
async def get_market_cap_rankings(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=500, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get market cap rankings"""
    coin_service = CoinService(db)

    skip = (page - 1) * size

    try:
        coins = coin_service.get_top_coins_by_market_cap(limit=skip + size)

        # Slice for pagination
        paginated_coins = coins[skip : skip + size]

        # Convert to market cap response format
        market_cap_responses = []
        for coin in paginated_coins:
            if coin.market_cap:
                market_cap_responses.append(
                    MarketCapResponse(
                        rank=coin.market_cap_rank or 0,
                        symbol=coin.symbol,
                        name=coin.name or coin.symbol,
                        price_usd=coin.price_usd or 0,
                        price_change_24h=coin.price_change_24h,
                        market_cap=coin.market_cap,
                        volume_24h_usd=coin.volume_24h_usd,
                    )
                )

        total_pages = (len(coins) + size - 1) // size

        return PaginatedResponse(
            items=market_cap_responses,
            total=len(coins),
            page=page,
            size=size,
            pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market cap data: {str(e)}")


@router.get("/trending", response_model=APIResponse[List[CoinResponse]])
async def get_trending_coins(
    limit: int = Query(10, ge=1, le=50, description="Number of trending coins"), db: Session = Depends(get_db)
):
    """Get trending coins by volume"""
    coin_service = CoinService(db)

    try:
        trending_coins = coin_service.get_trending_coins(limit=limit)

        coin_responses = []
        for coin in trending_coins:
            coin_dict = coin_service.get_coin_with_exchange_pairs(coin.symbol)
            if coin_dict:
                coin_responses.append(CoinResponse(**coin_dict))

        return APIResponse(success=True, data=coin_responses, message=f"Retrieved {len(coin_responses)} trending coins")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending coins: {str(e)}")


@router.get("/gainers", response_model=APIResponse[List[CoinResponse]])
async def get_biggest_gainers(
    limit: int = Query(10, ge=1, le=50, description="Number of gainers"), db: Session = Depends(get_db)
):
    """Get biggest price gainers in 24h"""
    coin_service = CoinService(db)

    try:
        gainers = coin_service.get_biggest_gainers(limit=limit)

        coin_responses = []
        for coin in gainers:
            coin_dict = coin_service.get_coin_with_exchange_pairs(coin.symbol)
            if coin_dict:
                coin_responses.append(CoinResponse(**coin_dict))

        return APIResponse(
            success=True, data=coin_responses, message=f"Retrieved {len(coin_responses)} biggest gainers"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching gainers: {str(e)}")


@router.get("/losers", response_model=APIResponse[List[CoinResponse]])
async def get_biggest_losers(
    limit: int = Query(10, ge=1, le=50, description="Number of losers"), db: Session = Depends(get_db)
):
    """Get biggest price losers in 24h"""
    coin_service = CoinService(db)

    try:
        losers = coin_service.get_biggest_losers(limit=limit)

        coin_responses = []
        for coin in losers:
            coin_dict = coin_service.get_coin_with_exchange_pairs(coin.symbol)
            if coin_dict:
                coin_responses.append(CoinResponse(**coin_dict))

        return APIResponse(success=True, data=coin_responses, message=f"Retrieved {len(coin_responses)} biggest losers")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching losers: {str(e)}")


# ==================== PRICE HISTORY ENDPOINTS ====================


@router.get("/coins/{symbol}/chart", response_model=APIResponse[PriceChartResponse])
async def get_price_chart(
    symbol: str,
    timeframe: str = Query("7d", description="Timeframe: 1h, 24h, 7d, 30d, 1y"),
    db: Session = Depends(get_db),
):
    """Get price chart data for a coin"""
    try:
        # Calculate time range
        now = datetime.now(UTC)
        if timeframe == "1h":
            start_time = now - timedelta(hours=1)
        elif timeframe == "24h":
            start_time = now - timedelta(days=1)
        elif timeframe == "7d":
            start_time = now - timedelta(days=7)
        elif timeframe == "30d":
            start_time = now - timedelta(days=30)
        elif timeframe == "1y":
            start_time = now - timedelta(days=365)
        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe")

        # Query price history
        from app.models.price_history import PriceHistory

        price_data = (
            db.query(PriceHistory)
            .filter(
                PriceHistory.symbol == symbol.upper(),
                PriceHistory.exchange == "average",
                PriceHistory.timestamp >= start_time,
            )
            .order_by(PriceHistory.timestamp.asc())
            .all()
        )

        if not price_data:
            raise HTTPException(status_code=404, detail=f"No price history found for {symbol.upper()}")

        # Convert to chart format
        chart_data = []
        for price_point in price_data:
            chart_data.append(
                PricePoint(
                    timestamp=price_point.timestamp,
                    price=float(price_point.price_usd),
                    volume=float(price_point.volume_24h_usd) if price_point.volume_24h_usd else None,
                )
            )

        chart_response = PriceChartResponse(
            symbol=symbol.upper(), exchange="average", timeframe=timeframe, data=chart_data
        )

        return APIResponse(
            success=True, data=chart_response, message=f"Retrieved {len(chart_data)} price points for {symbol.upper()}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")


# ==================== REAL-TIME PRICE ENDPOINTS ====================


@router.get("/price/{exchange}/{symbol}")
async def get_real_time_price(exchange: str, symbol: str, db: Session = Depends(get_db)):
    """Get real-time price from specific exchange"""
    exchange_service = ExchangeService(db)

    try:
        price = await exchange_service.get_single_price(exchange.lower(), symbol.upper())

        if price is None:
            raise HTTPException(status_code=404, detail=f"Price not found for {symbol.upper()} on {exchange.lower()}")

        return {
            "success": True,
            "exchange": exchange.lower(),
            "symbol": symbol.upper(),
            "price": price,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price: {str(e)}")


# ==================== DATA UPDATE ENDPOINTS ====================


@router.post("/update/prices")
async def update_prices(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger price data update"""
    try:
        exchange_service = ExchangeService(db)
        price_service = PriceService(db)

        # Run in background
        background_tasks.add_task(update_prices_task, exchange_service, price_service)

        return {
            "success": True,
            "message": "Price update started in background",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting price update: {str(e)}")


@router.post("/update/metadata")
async def update_metadata(
    background_tasks: BackgroundTasks,
    new_coins_only: bool = Query(True, description="Only update new coins (faster)"),
    db: Session = Depends(get_db),
):
    """Trigger metadata update"""
    try:
        coingecko_service = CoinGeckoService(db)

        # Run in background
        if new_coins_only:
            background_tasks.add_task(coingecko_service.enrich_new_coins_only)
            message = "New coins metadata update started"
        else:
            background_tasks.add_task(coingecko_service.fetch_all_metadata, False)  # No categories
            message = "Full metadata update started (no categories)"

        return {"success": True, "message": message, "timestamp": datetime.now(UTC).isoformat()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting metadata update: {str(e)}")


@router.get("/stats/metadata")
async def get_metadata_stats(db: Session = Depends(get_db)):
    """Get metadata completion statistics"""
    try:
        coingecko_service = CoinGeckoService(db)
        stats = coingecko_service.get_metadata_stats()

        return APIResponse(success=True, data=stats, message="Metadata statistics retrieved")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata stats: {str(e)}")

    # ==================== BACKGROUND TASKS ====================


async def update_prices_task(exchange_service: ExchangeService, price_service: PriceService):
    """Background task for updating prices"""
    try:
        # Fetch from all exchanges
        exchange_data = await exchange_service.fetch_all_exchange_data()

        # Process and store
        results = price_service.process_exchange_data(exchange_data)

        print(f"Price update completed: {results}")

    except Exception as e:
        print(f"Error in price update task: {e}")


# ==================== SEARCH ENDPOINTS ====================


@router.get("/search", response_model=APIResponse[List[CoinResponse]])
async def search_coins(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Search coins by name or symbol"""
    coin_service = CoinService(db)

    try:
        coins = coin_service.search_coins(q, limit=limit)

        coin_responses = []
        for coin in coins:
            coin_dict = coin_service.get_coin_with_exchange_pairs(coin.symbol)
            if coin_dict:
                coin_responses.append(CoinResponse(**coin_dict))

        return APIResponse(
            success=True, data=coin_responses, message=f"Found {len(coin_responses)} coins matching '{q}'"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coins: {str(e)}")
