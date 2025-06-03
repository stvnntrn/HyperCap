import logging
from datetime import UTC, datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PriceHistory1d, PriceHistory1h, PriceHistory1w, PriceHistory5m, PriceHistoryRaw
from app.schemas import (
    APIResponse,
    CoinResponse,
    HealthResponse,
    MarketCapResponse,
    PaginatedResponse,
    PriceChartResponse,
    PricePoint,
)
from app.services import CoinGeckoService, CoinService, ExchangeService, PriceService

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== HEALTH CHECK ====================


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
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
    timeframe: str = Query("7d", description="Timeframe: 5m, 1h, 4h, 1d, 7d, 30d, 1y"),
    exchange: str = Query("average", description="Exchange or 'average'"),
    db: Session = Depends(get_db),
):
    """Get price chart data for a coin using optimized time-series tables"""
    try:
        symbol = symbol.upper()

        # Calculate time range and select appropriate table
        now = datetime.now(UTC)

        if timeframe == "5m":
            # Last 5 minutes using raw data
            start_time = now - timedelta(minutes=5)
            table = PriceHistoryRaw
        elif timeframe == "1h":
            # Last 1 hour using 5-minute data
            start_time = now - timedelta(hours=1)
            table = PriceHistory5m
        elif timeframe == "4h":
            # Last 4 hours using 5-minute data
            start_time = now - timedelta(hours=4)
            table = PriceHistory5m
        elif timeframe == "1d":
            # Last 1 day using 1-hour data
            start_time = now - timedelta(days=1)
            table = PriceHistory1h
        elif timeframe == "7d":
            # Last 7 days using 1-hour data
            start_time = now - timedelta(days=7)
            table = PriceHistory1h
        elif timeframe == "30d":
            # Last 30 days using 1-day data
            start_time = now - timedelta(days=30)
            table = PriceHistory1d
        elif timeframe == "1y":
            # Last 1 year using 1-week data
            start_time = now - timedelta(days=365)
            table = PriceHistory1w
        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe")

        # Query the appropriate table
        if table == PriceHistoryRaw:
            # Raw data - use simple price field
            price_data = (
                db.query(table)
                .filter(
                    table.symbol == symbol,
                    table.exchange == exchange,
                    table.timestamp >= start_time,
                )
                .order_by(table.timestamp.asc())
                .all()
            )

            if not price_data:
                raise HTTPException(status_code=404, detail=f"No price history found for {symbol}")

            # Convert raw data to chart format
            chart_data = []
            for price_point in price_data:
                chart_data.append(
                    PricePoint(
                        timestamp=price_point.timestamp,
                        price=float(price_point.price_usd),
                        volume=float(price_point.volume_24h_usd) if price_point.volume_24h_usd else None,
                    )
                )
        else:
            # OHLC data - use close price for charts
            price_data = (
                db.query(table)
                .filter(
                    table.symbol == symbol,
                    table.exchange == exchange,
                    table.timestamp >= start_time,
                )
                .order_by(table.timestamp.asc())
                .all()
            )

            if not price_data:
                raise HTTPException(status_code=404, detail=f"No price history found for {symbol}")

            # Convert OHLC data to chart format (using close price)
            chart_data = []
            for price_point in price_data:
                chart_data.append(
                    PricePoint(
                        timestamp=price_point.timestamp,
                        price=float(price_point.price_close),
                        volume=float(price_point.volume_sum) if price_point.volume_sum else None,
                    )
                )

        chart_response = PriceChartResponse(symbol=symbol, exchange=exchange, timeframe=timeframe, data=chart_data)

        return APIResponse(
            success=True,
            data=chart_response,
            message=f"Retrieved {len(chart_data)} price points for {symbol} ({timeframe})",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")


@router.get("/coins/{symbol}/ohlc", response_model=APIResponse[List[Dict]])
async def get_ohlc_chart(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe: 5m, 1h, 1d, 1w"),
    exchange: str = Query("average", description="Exchange or 'average'"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles"),
    db: Session = Depends(get_db),
):
    """Get OHLC candlestick data for trading charts"""
    try:
        symbol = symbol.upper()

        # Select appropriate table based on timeframe
        if timeframe == "5m":
            table = PriceHistory5m
            start_time = datetime.now(UTC) - timedelta(hours=8)  # 8 hours of 5m data
        elif timeframe == "1h":
            table = PriceHistory1h
            start_time = datetime.now(UTC) - timedelta(days=4)  # 4 days of 1h data
        elif timeframe == "1d":
            table = PriceHistory1d
            start_time = datetime.now(UTC) - timedelta(days=100)  # 100 days of 1d data
        elif timeframe == "1w":
            table = PriceHistory1w
            start_time = datetime.now(UTC) - timedelta(days=700)  # 700 days of 1w data
        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe for OHLC")

        # Query OHLC data
        ohlc_data = (
            db.query(table)
            .filter(
                table.symbol == symbol,
                table.exchange == exchange,
                table.timestamp >= start_time,
            )
            .order_by(table.timestamp.desc())
            .limit(limit)
            .all()
        )

        if not ohlc_data:
            raise HTTPException(status_code=404, detail=f"No OHLC data found for {symbol}")

        # Convert to chart format (reverse to get chronological order)
        ohlc_data.reverse()

        chart_data = []
        for candle in ohlc_data:
            chart_data.append(
                {
                    "timestamp": candle.timestamp.isoformat(),
                    "open": float(candle.price_open),
                    "high": float(candle.price_high),
                    "low": float(candle.price_low),
                    "close": float(candle.price_close),
                    "volume": float(candle.volume_sum) if candle.volume_sum else 0,
                }
            )

        return APIResponse(
            success=True,
            data=chart_data,
            message=f"Retrieved {len(chart_data)} OHLC candles for {symbol} ({timeframe})",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching OHLC data: {str(e)}")


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


# ==================== ADMIN ENDPOINTS ====================


@router.post("/admin/initialize")
async def initialize_database(
    fetch_prices: bool = Query(True, description="Fetch current prices"),
    fetch_metadata: bool = Query(True, description="Fetch coin metadata"),
    fetch_history: bool = Query(False, description="Fetch historical data (slow)"),
    db: Session = Depends(get_db),
):
    """Complete database initialization (admin only)"""

    try:
        results = {}

        if fetch_prices:
            # 1. Fetch current prices from all exchanges
            exchange_service = ExchangeService(db)
            price_service = PriceService(db)

            logger.info("Fetching prices from all exchanges...")
            exchange_data = await exchange_service.fetch_all_exchange_data()
            results["prices"] = price_service.process_exchange_data(exchange_data)

        if fetch_metadata:
            # 2. Fetch metadata for all coins found
            coingecko_service = CoinGeckoService(db)
            logger.info("Enriching coins with metadata...")
            results["metadata"] = await coingecko_service.enrich_new_coins_only()

        if fetch_history:
            # 3. Historical data (placeholder for now)
            results["history"] = "Historical data fetch not implemented yet"

        return APIResponse(success=True, data=results, message="Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.get("/admin/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Check system initialization and health status"""

    try:
        coin_service = CoinService(db)
        coingecko_service = CoinGeckoService(db)

        # Count data completeness
        total_coins = coin_service.get_total_coins()
        metadata_stats = coingecko_service.get_metadata_stats()

        # Check recent price updates
        from app.models.coin import Coin

        recent_threshold = datetime.now(UTC) - timedelta(hours=1)
        recent_updates = db.query(Coin).filter(Coin.last_updated >= recent_threshold).count()

        # Check price history
        from app.models import PriceHistoryRaw

        total_price_records = db.query(PriceHistoryRaw).count()

        # Determine system health
        is_initialized = total_coins > 0
        has_recent_data = recent_updates > 0
        has_metadata = metadata_stats["names_percentage"] > 50

        if is_initialized and has_recent_data and has_metadata:
            health = "healthy"
        elif is_initialized:
            health = "needs_updates"
        else:
            health = "uninitialized"

        # Generate recommendations
        recommendations = []
        if total_coins == 0:
            recommendations.append("Run /admin/initialize to populate database")
        elif recent_updates == 0:
            recommendations.append("Price data is stale - trigger updates")
        elif metadata_stats["names_percentage"] < 50:
            recommendations.append("Run metadata enrichment")

        status = {
            "system_health": health,
            "database_initialized": is_initialized,
            "total_coins": total_coins,
            "recent_price_updates": recent_updates,
            "total_price_records": total_price_records,
            "metadata_stats": metadata_stats,
            "recommendations": recommendations,
            "last_check": datetime.now(UTC).isoformat(),
        }

        return APIResponse(success=True, data=status, message=f"System status: {health}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")


@router.post("/admin/fetch-all-metadata")
async def fetch_all_metadata(
    include_categories: bool = Query(True, description="Include categories (slow)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Fetch complete metadata for ALL coins (slow operation)"""

    try:
        coingecko_service = CoinGeckoService(db)

        # Run in background for long operations
        background_tasks.add_task(fetch_all_metadata_task, coingecko_service, include_categories)

        return APIResponse(
            success=True,
            data={"status": "started"},
            message=f"Complete metadata fetch started in background (categories: {include_categories})",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting metadata fetch: {str(e)}")


@router.post("/admin/cleanup")
async def cleanup_old_data(
    days_to_keep: int = Query(
        365, ge=30, le=3650, description="Days of price history to keep (WARNING: This deletes historical data!)"
    ),
    confirm: bool = Query(False, description="Must be true to confirm deletion"),
    db: Session = Depends(get_db),
):
    """⚠️ DANGER: Clean up old price history data (affects charts!)"""

    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="This operation deletes historical price data permanently. Set confirm=true if you're sure.",
        )

    try:
        price_service = PriceService(db)
        deleted_count = price_service.cleanup_old_price_history(days_to_keep)

        return APIResponse(
            success=True,
            data={
                "deleted_records": deleted_count,
                "days_kept": days_to_keep,
                "warning": "Historical data has been permanently deleted",
            },
            message=f"⚠️ Deleted {deleted_count} price history records older than {days_to_keep} days",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.get("/admin/aggregation-stats", response_model=APIResponse[Dict])
async def get_aggregation_stats(db: Session = Depends(get_db)):
    """Get statistics about time-series data aggregation"""
    try:
        from app.services.aggregation_service import AggregationService

        aggregation_service = AggregationService(db)
        stats = aggregation_service.get_aggregation_stats()

        return APIResponse(success=True, data=stats, message="Aggregation statistics retrieved successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting aggregation stats: {str(e)}")


@router.post("/admin/historical/detect-gaps")
async def detect_data_gaps(db: Session = Depends(get_db)):
    """
    Scan all coins for missing historical data gaps
    """
    try:
        from app.services.historical_data_service import HistoricalDataService

        historical_service = HistoricalDataService(db)
        gap_analysis = historical_service.detect_data_gaps()

        return APIResponse(
            success=True,
            data=gap_analysis,
            message=f"Gap analysis complete: {gap_analysis['coins_with_gaps']} coins need backfill",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting gaps: {str(e)}")


@router.post("/admin/historical/backfill-all")
async def backfill_all_historical_data(
    days_back: int = Query(365, ge=1, le=2000, description="Days of historical data to fetch"),
    pause_real_time: bool = Query(True, description="Pause real-time fetching during operation"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    ⚠️ BULK OPERATION: Fetch complete historical data for ALL coins
    This will take several hours and pause real-time fetching!
    """
    try:
        from app.services.historical_data_service import HistoricalDataService

        historical_service = HistoricalDataService(db)

        # Run in background due to long execution time
        background_tasks.add_task(bulk_backfill_task, historical_service, days_back, pause_real_time)

        return APIResponse(
            success=True,
            data={
                "operation": "bulk_backfill_started",
                "days_back": days_back,
                "pause_real_time": pause_real_time,
                "estimated_duration_hours": "2-6 hours",
            },
            message=f"⚠️ Bulk historical backfill started for {days_back} days. Check logs for progress.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting bulk backfill: {str(e)}")


@router.post("/admin/historical/fill-gaps")
async def fill_missing_gaps(
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    Intelligently detect and fill only missing data gaps
    Much faster than full backfill - only fetches what's missing
    """
    try:
        from app.services.historical_data_service import HistoricalDataService

        historical_service = HistoricalDataService(db)

        # Run in background
        background_tasks.add_task(gap_fill_task, historical_service)

        return APIResponse(
            success=True,
            data={"operation": "gap_fill_started"},
            message="Smart gap filling started - only missing data will be fetched",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting gap fill: {str(e)}")


# ==================== BACKGROUND TASKS ====================


async def update_prices_task(exchange_service: ExchangeService, price_service: PriceService):
    """Background task for updating prices"""
    try:
        # Fetch from all exchanges
        exchange_data = await exchange_service.fetch_all_exchange_data()

        # Process and store
        results = price_service.process_exchange_data(exchange_data)

        logger.info(f"Price update completed: {results}")

    except Exception as e:
        logger.error(f"Error in price update task: {e}")


async def fetch_all_metadata_task(coingecko_service: CoinGeckoService, include_categories: bool):
    """Background task for fetching all metadata"""
    try:
        logger.info("Starting complete metadata fetch...")
        updated_count = await coingecko_service.fetch_all_metadata(include_categories=include_categories)
        logger.info(f"Metadata fetch completed: {updated_count} coins updated")

    except Exception as e:
        logger.error(f"Error in metadata fetch task: {e}")


# ==================== DATA UPDATE ENDPOINTS (Updated) ====================


@router.post("/update/prices")
async def update_prices(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger price data update"""
    try:
        exchange_service = ExchangeService(db)
        price_service = PriceService(db)

        # Run in background
        background_tasks.add_task(update_prices_task, exchange_service, price_service)

        return APIResponse(success=True, data={"status": "started"}, message="Price update started in background")

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

        return APIResponse(success=True, data={"status": "started"}, message=message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting metadata update: {str(e)}")


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
