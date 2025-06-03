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

    def store_historical_data(self, historical_data: List[Dict[str, Any]]) -> int:
        """
        Store historical data points in PriceHistoryRaw
        Avoids duplicates by checking existing timestamps
        """
        stored_count = 0
        skipped_count = 0

        for data_point in historical_data:
            try:
                symbol = data_point["symbol"]
                timestamp = data_point["timestamp"]

                # Check if this data point already exists
                existing = (
                    self.db.query(PriceHistoryRaw)
                    .filter(
                        and_(
                            PriceHistoryRaw.symbol == symbol,
                            PriceHistoryRaw.exchange == "average",
                            PriceHistoryRaw.timestamp == timestamp,
                        )
                    )
                    .first()
                )

                if existing:
                    skipped_count += 1
                    continue

                # Store new data point
                historical_record = PriceHistoryRaw(
                    symbol=symbol,
                    exchange="average",  # Mark as average/historical data
                    price_usd=Decimal(str(data_point["price_usd"])),
                    volume_24h_usd=Decimal(str(data_point["volume_24h_usd"])) if data_point["volume_24h_usd"] else None,
                    timestamp=timestamp,
                )

                self.db.add(historical_record)
                stored_count += 1

                # Commit in batches to avoid memory issues
                if stored_count % 100 == 0:
                    self.db.commit()

            except Exception as e:
                logger.warning(f"Error storing historical point: {e}")
                continue

        # Final commit
        if stored_count > 0:
            self.db.commit()

        logger.info(f"Stored {stored_count} new historical points, skipped {skipped_count} duplicates")
        return stored_count

    # ==================== BULK OPERATIONS ====================

    async def backfill_all_coins(
        self, days_back: int = 365, pause_real_time: bool = True, batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Backfill historical data for ALL coins
        Pauses real-time fetching during operation to avoid rate limits
        """
        logger.info(f"Starting bulk historical backfill for all coins ({days_back} days)")

        if pause_real_time:
            logger.info("Pausing real-time data fetching...")
            pause_scheduler()

        try:
            # Get all coins
            all_coins = self.db.query(Coin).all()
            symbols = [coin.symbol for coin in all_coins]

            total_coins = len(symbols)
            processed_count = 0
            success_count = 0

            # Process in batches to manage rate limits
            for i in range(0, total_coins, batch_size):
                batch_symbols = symbols[i : i + batch_size]
                logger.info(
                    f"Processing batch {i // batch_size + 1}: symbols {i + 1}-{min(i + batch_size, total_coins)}"
                )

                for symbol in batch_symbols:
                    try:
                        # Fetch historical data
                        historical_data = await self.fetch_historical_prices_for_coin(symbol, days_back=days_back)

                        if historical_data:
                            # Store the data
                            stored_count = self.store_historical_data(historical_data)
                            if stored_count > 0:
                                success_count += 1
                                logger.info(f"✓ {symbol}: {stored_count} points stored")
                            else:
                                logger.info(f"○ {symbol}: no new data (already exists)")
                        else:
                            logger.warning(f"✗ {symbol}: no data received")

                        processed_count += 1

                        # Rate limiting delay
                        await asyncio.sleep(self.rate_limit_delay)

                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                        processed_count += 1
                        continue

                # Longer delay between batches
                if i + batch_size < total_coins:
                    logger.info("Batch complete. Waiting 10 seconds before next batch...")
                    await asyncio.sleep(10)

            result = {
                "total_coins": total_coins,
                "processed": processed_count,
                "successful": success_count,
                "failed": processed_count - success_count,
                "days_backfilled": days_back,
                "completion_time": datetime.now(UTC).isoformat(),
            }

            logger.info(f"Bulk backfill complete: {success_count}/{total_coins} coins successful")
            return result

        finally:
            if pause_real_time:
                logger.info("Resuming real-time data fetching...")
                resume_scheduler()

    async def backfill_missing_data_gaps(self) -> Dict[str, Any]:
        """
        Detect and backfill only the missing data gaps
        More efficient than full backfill
        """
        logger.info("Starting intelligent gap backfill...")

        # Pause real-time fetching
        pause_scheduler()

        try:
            # Detect gaps
            gap_analysis = self.detect_data_gaps()
            gaps = gap_analysis["gaps"]

            if not gaps:
                logger.info("No gaps detected - all data is up to date")
                return {
                    "status": "no_gaps",
                    "message": "All coins have current data",
                    "total_coins": gap_analysis["total_coins"],
                }

            processed_count = 0
            success_count = 0

            for symbol, gap_info in gaps.items():
                try:
                    days_to_fetch = gap_info["recommended_days"]
                    logger.info(f"Backfilling {symbol}: {days_to_fetch} days")

                    # Fetch historical data for this specific gap
                    historical_data = await self.fetch_historical_prices_for_coin(symbol, days_back=days_to_fetch)

                    if historical_data:
                        stored_count = self.store_historical_data(historical_data)
                        if stored_count > 0:
                            success_count += 1
                            logger.info(f"✓ {symbol}: {stored_count} points backfilled")
                        else:
                            logger.info(f"○ {symbol}: gap already filled")

                    processed_count += 1

                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    logger.error(f"Error backfilling {symbol}: {e}")
                    processed_count += 1
                    continue

            result = {
                "status": "completed",
                "gaps_detected": len(gaps),
                "processed": processed_count,
                "successful": success_count,
                "failed": processed_count - success_count,
                "completion_time": datetime.now(UTC).isoformat(),
            }

            logger.info(f"Gap backfill complete: {success_count}/{len(gaps)} gaps filled")
            return result

        finally:
            resume_scheduler()

    # ==================== STARTUP GAP CHECK ====================

    async def startup_gap_check_and_fill(self, max_gap_hours: int = 2) -> Dict[str, Any]:
        """
        Check for gaps on startup and automatically backfill if needed
        Call this when your API starts up after being offline
        """
        logger.info("Running startup gap check...")

        gap_analysis = self.detect_data_gaps()

        # Check if we have any significant gaps
        significant_gaps = {}
        for symbol, gap_info in gap_analysis["gaps"].items():
            if gap_info["type"] == "complete_missing":
                significant_gaps[symbol] = gap_info
            elif gap_info["type"] == "gap_detected" and gap_info.get("gap_hours", 0) > max_gap_hours:
                significant_gaps[symbol] = gap_info

        if not significant_gaps:
            logger.info("No significant gaps detected on startup")
            return {
                "status": "no_action_needed",
                "message": "All data is current",
                "total_coins": gap_analysis["total_coins"],
                "scan_result": gap_analysis,
            }

        logger.info(f"Found {len(significant_gaps)} coins with significant gaps - starting automatic backfill")

        # Automatically backfill the gaps
        backfill_result = await self.backfill_missing_data_gaps()

        return {
            "status": "gaps_filled",
            "message": f"Automatically backfilled {len(significant_gaps)} coins with data gaps",
            "gap_analysis": gap_analysis,
            "backfill_result": backfill_result,
        }
