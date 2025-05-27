import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory5m, PriceHistoryRaw

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
