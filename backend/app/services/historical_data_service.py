import asyncio
import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models import Coin, PriceHistoryRaw
from app.services import CoinGeckoService
from app.tasks.scheduler import pause_scheduler, resume_scheduler

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """
    Service for managing historical data with gap detection and backfill
    Handles offline periods and ensures continuous data coverage
    """

    def __init__(self, db: Session):
        self.db = db
        self.coingecko_service = CoinGeckoService(db)
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit_delay = 1.2  # CoinGecko free tier rate limit
        self.timeout = 30.0

    # ==================== GAP DETECTION ====================

    def detect_data_gaps(self) -> Dict[str, Any]:
        """
        Detect gaps in historical data for all coins
        Returns information about missing data periods
        """
        logger.info("Detecting data gaps for all coins...")

        gaps_detected = {}
        now = datetime.now(UTC)

        # Get all coins that should have data
        all_coins = self.db.query(Coin).all()

        for coin in all_coins:
            symbol = coin.symbol

            # Get the latest data point for this coin
            latest_data = (
                self.db.query(PriceHistoryRaw)
                .filter(
                    and_(
                        PriceHistoryRaw.symbol == symbol,
                        PriceHistoryRaw.exchange == "average",  # Use average prices for gap detection
                    )
                )
                .order_by(desc(PriceHistoryRaw.timestamp))
                .first()
            )

            if not latest_data:
                # No data at all - need complete backfill
                gaps_detected[symbol] = {
                    "type": "complete_missing",
                    "last_data": None,
                    "gap_days": None,
                    "needs_backfill": True,
                    "recommended_days": 365,  # Get 1 year of data for new coins
                }
            else:
                # Check how old the latest data is
                time_since_last = now - latest_data.timestamp
                gap_hours = time_since_last.total_seconds() / 3600
                gap_days = gap_hours / 24

                # If gap is more than 2 hours, we need backfill
                if gap_hours > 2:
                    gaps_detected[symbol] = {
                        "type": "gap_detected",
                        "last_data": latest_data.timestamp.isoformat(),
                        "gap_hours": round(gap_hours, 1),
                        "gap_days": round(gap_days, 1),
                        "needs_backfill": True,
                        "recommended_days": min(int(gap_days) + 1, 365),  # Backfill gap + buffer, max 1 year
                    }

        total_gaps = len(gaps_detected)
        total_coins = len(all_coins)

        logger.info(f"Gap detection complete: {total_gaps} coins need backfill out of {total_coins} total")

        return {
            "total_coins": total_coins,
            "coins_with_gaps": total_gaps,
            "coins_up_to_date": total_coins - total_gaps,
            "gaps": gaps_detected,
            "scan_timestamp": now.isoformat(),
        }

    # ==================== HISTORICAL DATA FETCHING ====================

    async def fetch_historical_prices_for_coin(
        self, symbol: str, days_back: int = 365, interval: str = "hourly"
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical price data for a single coin from CoinGecko
        """
        # Get CoinGecko ID for this symbol
        symbol_to_id = await self.coingecko_service.get_symbol_to_id_mapping()
        coin_id = symbol_to_id.get(symbol.upper())

        if not coin_id:
            logger.warning(f"No CoinGecko ID found for symbol {symbol}")
            return []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.base_url}/coins/{coin_id}/market_chart"
                params = {
                    "vs_currency": "usd",
                    "days": days_back,
                    "interval": interval,  # "hourly" or "daily"
                }

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                prices = data.get("prices", [])
                volumes = data.get("total_volumes", [])

                # Convert to our format
                historical_points = []
                for i, price_point in enumerate(prices):
                    timestamp_ms, price = price_point
                    volume = volumes[i][1] if i < len(volumes) else 0

                    historical_points.append(
                        {
                            "timestamp": datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC),
                            "price_usd": price,
                            "volume_24h_usd": volume,
                            "symbol": symbol.upper(),
                        }
                    )

                logger.info(f"Fetched {len(historical_points)} historical points for {symbol}")
                return historical_points

            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {e}")
                return []
