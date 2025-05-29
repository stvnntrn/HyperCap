import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Dict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models import PriceHistory1d, PriceHistory1h, PriceHistory1w, PriceHistory5m, PriceHistoryRaw

logger = logging.getLogger(__name__)


class AggregationService:
    """
    Service for aggregating raw price data into OHLC intervals
    Creates professional time-series data for charts
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== 5-MINUTE AGGREGATION ====================

    def create_5m_aggregates(self, lookback_minutes: int = 10) -> int:
        """
        Create 5-minute OHLC aggregates from raw data
        Only processes recent data to avoid reprocessing
        """
        try:
            # Calculate time window (round down to 5-minute boundary)
            now = datetime.now(UTC)
            end_time = now.replace(second=0, microsecond=0)
            end_time = end_time.replace(minute=(end_time.minute // 5) * 5)
            start_time = end_time - timedelta(minutes=lookback_minutes)

            logger.info(f"Creating 5m aggregates from {start_time} to {end_time}")

            # Get all symbols and exchanges that have raw data in this window
            symbols_exchanges = (
                self.db.query(PriceHistoryRaw.symbol, PriceHistoryRaw.exchange)
                .filter(and_(PriceHistoryRaw.timestamp >= start_time, PriceHistoryRaw.timestamp < end_time))
                .distinct()
                .all()
            )

            created_count = 0

            for symbol, exchange in symbols_exchanges:
                # Create 5-minute windows for this symbol/exchange
                current_window = start_time
                while current_window < end_time:
                    window_end = current_window + timedelta(minutes=5)

                    # Check if aggregate already exists
                    existing = (
                        self.db.query(PriceHistory5m)
                        .filter(
                            and_(
                                PriceHistory5m.symbol == symbol,
                                PriceHistory5m.exchange == exchange,
                                PriceHistory5m.timestamp == current_window,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        # Get raw data for this 5-minute window
                        raw_data = (
                            self.db.query(PriceHistoryRaw)
                            .filter(
                                and_(
                                    PriceHistoryRaw.symbol == symbol,
                                    PriceHistoryRaw.exchange == exchange,
                                    PriceHistoryRaw.timestamp >= current_window,
                                    PriceHistoryRaw.timestamp < window_end,
                                )
                            )
                            .order_by(PriceHistoryRaw.timestamp.asc())
                            .all()
                        )

                        if raw_data:
                            # Calculate OHLC
                            prices = [float(row.price_usd) for row in raw_data]
                            volumes = [float(row.volume_24h_usd or 0) for row in raw_data]

                            ohlc_data = PriceHistory5m(
                                symbol=symbol,
                                exchange=exchange,
                                price_open=Decimal(str(prices[0])),
                                price_close=Decimal(str(prices[-1])),
                                price_high=Decimal(str(max(prices))),
                                price_low=Decimal(str(min(prices))),
                                volume_sum=Decimal(str(sum(volumes))),
                                timestamp=current_window,
                            )

                            self.db.add(ohlc_data)
                            created_count += 1

                    current_window = window_end

            self.db.commit()
            logger.info(f"Created {created_count} new 5-minute aggregates")
            return created_count

        except Exception as e:
            logger.error(f"Error creating 5m aggregates: {e}")
            self.db.rollback()
            return 0

    # ==================== 1-HOUR AGGREGATION ====================

    def create_1h_aggregates(self, lookback_hours: int = 2) -> int:
        """
        Create 1-hour OHLC aggregates from 5-minute data
        """
        try:
            # Calculate time window (round down to hour boundary)
            now = datetime.now(UTC)
            end_time = now.replace(minute=0, second=0, microsecond=0)
            start_time = end_time - timedelta(hours=lookback_hours)

            logger.info(f"Creating 1h aggregates from {start_time} to {end_time}")

            # Get all symbols and exchanges that have 5m data
            symbols_exchanges = (
                self.db.query(PriceHistory5m.symbol, PriceHistory5m.exchange)
                .filter(and_(PriceHistory5m.timestamp >= start_time, PriceHistory5m.timestamp < end_time))
                .distinct()
                .all()
            )

            created_count = 0

            for symbol, exchange in symbols_exchanges:
                # Create 1-hour windows
                current_window = start_time
                while current_window < end_time:
                    window_end = current_window + timedelta(hours=1)

                    # Check if aggregate already exists
                    existing = (
                        self.db.query(PriceHistory1h)
                        .filter(
                            and_(
                                PriceHistory1h.symbol == symbol,
                                PriceHistory1h.exchange == exchange,
                                PriceHistory1h.timestamp == current_window,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        # Get 5m data for this hour
                        data_5m = (
                            self.db.query(PriceHistory5m)
                            .filter(
                                and_(
                                    PriceHistory5m.symbol == symbol,
                                    PriceHistory5m.exchange == exchange,
                                    PriceHistory5m.timestamp >= current_window,
                                    PriceHistory5m.timestamp < window_end,
                                )
                            )
                            .order_by(PriceHistory5m.timestamp.asc())
                            .all()
                        )

                        if data_5m:
                            # Calculate OHLC from 5m data
                            open_price = float(data_5m[0].price_open)
                            close_price = float(data_5m[-1].price_close)
                            high_price = max(float(row.price_high) for row in data_5m)
                            low_price = min(float(row.price_low) for row in data_5m)
                            total_volume = sum(float(row.volume_sum or 0) for row in data_5m)

                            ohlc_data = PriceHistory1h(
                                symbol=symbol,
                                exchange=exchange,
                                price_open=Decimal(str(open_price)),
                                price_close=Decimal(str(close_price)),
                                price_high=Decimal(str(high_price)),
                                price_low=Decimal(str(low_price)),
                                volume_sum=Decimal(str(total_volume)),
                                timestamp=current_window,
                            )

                            self.db.add(ohlc_data)
                            created_count += 1

                    current_window = window_end

            self.db.commit()
            logger.info(f"Created {created_count} new 1-hour aggregates")
            return created_count

        except Exception as e:
            logger.error(f"Error creating 1h aggregates: {e}")
            self.db.rollback()
            return 0

    # ==================== 1-DAY AGGREGATION ====================

    def create_1d_aggregates(self, lookback_days: int = 2) -> int:
        """
        Create 1-day OHLC aggregates from 1-hour data
        """
        try:
            # Calculate time window (round down to day boundary)
            now = datetime.now(UTC)
            end_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = end_time - timedelta(days=lookback_days)

            logger.info(f"Creating 1d aggregates from {start_time} to {end_time}")

            # Get all symbols and exchanges that have 1h data
            symbols_exchanges = (
                self.db.query(PriceHistory1h.symbol, PriceHistory1h.exchange)
                .filter(and_(PriceHistory1h.timestamp >= start_time, PriceHistory1h.timestamp < end_time))
                .distinct()
                .all()
            )

            created_count = 0

            for symbol, exchange in symbols_exchanges:
                # Create 1-day windows
                current_window = start_time
                while current_window < end_time:
                    window_end = current_window + timedelta(days=1)

                    # Check if aggregate already exists
                    existing = (
                        self.db.query(PriceHistory1d)
                        .filter(
                            and_(
                                PriceHistory1d.symbol == symbol,
                                PriceHistory1d.exchange == exchange,
                                PriceHistory1d.timestamp == current_window,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        # Get 1h data for this day
                        data_1h = (
                            self.db.query(PriceHistory1h)
                            .filter(
                                and_(
                                    PriceHistory1h.symbol == symbol,
                                    PriceHistory1h.exchange == exchange,
                                    PriceHistory1h.timestamp >= current_window,
                                    PriceHistory1h.timestamp < window_end,
                                )
                            )
                            .order_by(PriceHistory1h.timestamp.asc())
                            .all()
                        )

                        if data_1h:
                            # Calculate OHLC from 1h data
                            open_price = float(data_1h[0].price_open)
                            close_price = float(data_1h[-1].price_close)
                            high_price = max(float(row.price_high) for row in data_1h)
                            low_price = min(float(row.price_low) for row in data_1h)
                            total_volume = sum(float(row.volume_sum or 0) for row in data_1h)

                            ohlc_data = PriceHistory1d(
                                symbol=symbol,
                                exchange=exchange,
                                price_open=Decimal(str(open_price)),
                                price_close=Decimal(str(close_price)),
                                price_high=Decimal(str(high_price)),
                                price_low=Decimal(str(low_price)),
                                volume_sum=Decimal(str(total_volume)),
                                timestamp=current_window,
                            )

                            self.db.add(ohlc_data)
                            created_count += 1

                    current_window = window_end

            self.db.commit()
            logger.info(f"Created {created_count} new 1-day aggregates")
            return created_count

        except Exception as e:
            logger.error(f"Error creating 1d aggregates: {e}")
            self.db.rollback()
            return 0

    # ==================== 1-WEEK AGGREGATION ====================

    def create_1w_aggregates(self, lookback_weeks: int = 2) -> int:
        """
        Create 1-week OHLC aggregates from 1-day data
        """
        try:
            # Calculate time window (round down to Monday)
            now = datetime.now(UTC)
            days_since_monday = now.weekday()
            end_time = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = end_time - timedelta(weeks=lookback_weeks)

            logger.info(f"Creating 1w aggregates from {start_time} to {end_time}")

            # Get all symbols and exchanges that have 1d data
            symbols_exchanges = (
                self.db.query(PriceHistory1d.symbol, PriceHistory1d.exchange)
                .filter(and_(PriceHistory1d.timestamp >= start_time, PriceHistory1d.timestamp < end_time))
                .distinct()
                .all()
            )

            created_count = 0

            for symbol, exchange in symbols_exchanges:
                # Create 1-week windows (starting on Mondays)
                current_window = start_time
                while current_window < end_time:
                    window_end = current_window + timedelta(weeks=1)

                    # Check if aggregate already exists
                    existing = (
                        self.db.query(PriceHistory1w)
                        .filter(
                            and_(
                                PriceHistory1w.symbol == symbol,
                                PriceHistory1w.exchange == exchange,
                                PriceHistory1w.timestamp == current_window,
                            )
                        )
                        .first()
                    )

                    if not existing:
                        # Get 1d data for this week
                        data_1d = (
                            self.db.query(PriceHistory1d)
                            .filter(
                                and_(
                                    PriceHistory1d.symbol == symbol,
                                    PriceHistory1d.exchange == exchange,
                                    PriceHistory1d.timestamp >= current_window,
                                    PriceHistory1d.timestamp < window_end,
                                )
                            )
                            .order_by(PriceHistory1d.timestamp.asc())
                            .all()
                        )

                        if data_1d:
                            # Calculate OHLC from 1d data
                            open_price = float(data_1d[0].price_open)
                            close_price = float(data_1d[-1].price_close)
                            high_price = max(float(row.price_high) for row in data_1d)
                            low_price = min(float(row.price_low) for row in data_1d)
                            total_volume = sum(float(row.volume_sum or 0) for row in data_1d)

                            ohlc_data = PriceHistory1w(
                                symbol=symbol,
                                exchange=exchange,
                                price_open=Decimal(str(open_price)),
                                price_close=Decimal(str(close_price)),
                                price_high=Decimal(str(high_price)),
                                price_low=Decimal(str(low_price)),
                                volume_sum=Decimal(str(total_volume)),
                                timestamp=current_window,
                            )

                            self.db.add(ohlc_data)
                            created_count += 1

                    current_window = window_end

            self.db.commit()
            logger.info(f"Created {created_count} new 1-week aggregates")
            return created_count

        except Exception as e:
            logger.error(f"Error creating 1w aggregates: {e}")
            self.db.rollback()
            return 0

    # ==================== DATA CLEANUP ====================

    def cleanup_old_raw_data(self, hours_to_keep: int = 24) -> int:
        """
        Remove raw price data older than specified hours
        Default: Keep 24 hours of raw data
        """
        try:
            cutoff_time = datetime.now(UTC) - timedelta(hours=hours_to_keep)

            deleted_count = self.db.query(PriceHistoryRaw).filter(PriceHistoryRaw.timestamp < cutoff_time).delete()

            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old raw price records (older than {hours_to_keep}h)")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up raw data: {e}")
            self.db.rollback()
            return 0

    def cleanup_old_5m_data(self, days_to_keep: int = 7) -> int:
        """
        Remove 5-minute data older than specified days
        Default: Keep 1 week of 5-minute data
        """
        try:
            cutoff_time = datetime.now(UTC) - timedelta(days=days_to_keep)

            deleted_count = self.db.query(PriceHistory5m).filter(PriceHistory5m.timestamp < cutoff_time).delete()

            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old 5m price records (older than {days_to_keep}d)")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up 5m data: {e}")
            self.db.rollback()
            return 0

    def cleanup_old_1h_data(self, days_to_keep: int = 30) -> int:
        """
        Remove 1-hour data older than specified days
        Default: Keep 1 month of 1-hour data
        """
        try:
            cutoff_time = datetime.now(UTC) - timedelta(days=days_to_keep)

            deleted_count = self.db.query(PriceHistory1h).filter(PriceHistory1h.timestamp < cutoff_time).delete()

            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old 1h price records (older than {days_to_keep}d)")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up 1h data: {e}")
            self.db.rollback()
            return 0

    def cleanup_old_1d_data(self, days_to_keep: int = 365) -> int:
        """
        Remove 1-day data older than specified days
        Default: Keep 1 year of 1-day data
        """
        try:
            cutoff_time = datetime.now(UTC) - timedelta(days=days_to_keep)

            deleted_count = self.db.query(PriceHistory1d).filter(PriceHistory1d.timestamp < cutoff_time).delete()

            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old 1d price records (older than {days_to_keep}d)")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up 1d data: {e}")
            self.db.rollback()
            return 0

    # Note: 1-week data is kept forever (no cleanup)

    # ==================== MAIN PROCESSING FUNCTIONS ====================

    def process_all_aggregations(self) -> Dict[str, int]:
        """
        Run all aggregation processes in correct order
        Called by scheduler every 5 minutes
        """
        results = {}

        try:
            # Process in order: 5m -> 1h -> 1d -> 1w
            results["aggregates_5m"] = self.create_5m_aggregates()
            results["aggregates_1h"] = self.create_1h_aggregates()
            results["aggregates_1d"] = self.create_1d_aggregates()
            results["aggregates_1w"] = self.create_1w_aggregates()

            logger.info(f"Aggregation completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in aggregation process: {e}")
            return {"error": str(e)}

    def process_all_cleanup(self) -> Dict[str, int]:
        """
        Run all cleanup processes
        Called by scheduler daily
        """
        results = {}

        try:
            results["raw_cleaned"] = self.cleanup_old_raw_data(24)  # Keep 24h
            results["5m_cleaned"] = self.cleanup_old_5m_data(7)  # Keep 1 week
            results["1h_cleaned"] = self.cleanup_old_1h_data(30)  # Keep 1 month
            results["1d_cleaned"] = self.cleanup_old_1d_data(365)  # Keep 1 year
            # 1w data kept forever

            logger.info(f"Cleanup completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in cleanup process: {e}")
            return {"error": str(e)}

    # ==================== UTILITY FUNCTIONS ====================

    def get_aggregation_stats(self) -> Dict[str, int]:
        """
        Get statistics about aggregated data
        Useful for monitoring and debugging
        """
        try:
            stats = {
                "raw_records": self.db.query(PriceHistoryRaw).count(),
                "5m_records": self.db.query(PriceHistory5m).count(),
                "1h_records": self.db.query(PriceHistory1h).count(),
                "1d_records": self.db.query(PriceHistory1d).count(),
                "1w_records": self.db.query(PriceHistory1w).count(),
            }

            # Get latest timestamps
            latest_raw = self.db.query(func.max(PriceHistoryRaw.timestamp)).scalar()
            latest_5m = self.db.query(func.max(PriceHistory5m.timestamp)).scalar()
            latest_1h = self.db.query(func.max(PriceHistory1h.timestamp)).scalar()
            latest_1d = self.db.query(func.max(PriceHistory1d.timestamp)).scalar()
            latest_1w = self.db.query(func.max(PriceHistory1w.timestamp)).scalar()

            stats["latest_raw"] = latest_raw.isoformat() if latest_raw else None
            stats["latest_5m"] = latest_5m.isoformat() if latest_5m else None
            stats["latest_1h"] = latest_1h.isoformat() if latest_1h else None
            stats["latest_1d"] = latest_1d.isoformat() if latest_1d else None
            stats["latest_1w"] = latest_1w.isoformat() if latest_1w else None

            return stats

        except Exception as e:
            logger.error(f"Error getting aggregation stats: {e}")
            return {"error": str(e)}
