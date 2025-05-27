import logging
from datetime import UTC, datetime

from app.database import get_db
from app.services.coingecko_service import CoinGeckoService
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


async def enrich_new_coins_job():
    """Scheduled job to enrich new coins with metadata"""
    db: Session = next(get_db())

    try:
        logger.info(f"Starting scheduled metadata enrichment at {datetime.now(UTC)}")

        coingecko_service = CoinGeckoService(db)

        # Only enrich new coins (fast)
        updated_count = await coingecko_service.enrich_new_coins_only()

        if updated_count > 0:
            logger.info(f"Enriched {updated_count} new coins with metadata")
        else:
            logger.debug("No new coins needed metadata enrichment")

    except Exception as e:
        logger.error(f"Error in scheduled metadata enrichment: {e}")
    finally:
        db.close()
