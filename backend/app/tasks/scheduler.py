import logging
from datetime import UTC, datetime

from app.database import get_db
from app.services.exchange_service import ExchangeService
from app.services.price_service import PriceService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

# Track scheduler state
_scheduler_running = False

# ==================== SCHEDULED TASKS ====================


async def update_prices_job():
    """Scheduled job to update prices from exchanges"""
    db: Session = next(get_db())

    try:
        logger.info(f"Starting scheduled price update at {datetime.now(UTC)}")

        exchange_service = ExchangeService(db)
        price_service = PriceService(db)

        # Fetch from all exchanges
        exchange_data = await exchange_service.fetch_all_exchange_data()

        # Process and store
        results = price_service.process_exchange_data(exchange_data)

        logger.info(f"Scheduled price update completed: {results}")

    except Exception as e:
        logger.error(f"Error in scheduled price update: {e}")
    finally:
        db.close()
