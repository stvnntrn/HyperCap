import logging
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Coin
from app.services import AggregationService, CoinGeckoService, ExchangeService, PriceService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

# Track scheduler state
_scheduler_running = False

# ==================== SCHEDULED TASKS ====================


async def update_prices_job():
    """
    Scheduled job to update prices from exchanges
    Now includes market cap rankings update
    """
    db: Session = next(get_db())

    try:
        logger.info(f"Starting scheduled price update at {datetime.now(UTC)}")

        exchange_service = ExchangeService(db)
        price_service = PriceService(db)

        # Fetch from all exchanges
        exchange_data = await exchange_service.fetch_all_exchange_data()

        # Process and store (includes ranking updates now)
        results = await price_service.update_prices_and_rankings(exchange_data)

        logger.info(f"Scheduled price update completed: {results}")

    except Exception as e:
        logger.error(f"Error in scheduled price update: {e}")
    finally:
        db.close()


async def discover_new_coins_job():
    """
    Scheduled job to check for new coins and enrich them
    Now includes historical data backfill for new coins
    """
    db: Session = next(get_db())

    try:
        logger.info(f"Checking for new coins at {datetime.now(UTC)}")

        coingecko_service = CoinGeckoService(db)

        # Check for new coins without metadata
        updated_count = await coingecko_service.enrich_new_coins_only()

        if updated_count > 0:
            logger.info(f"Found and enriched {updated_count} new coins with metadata")

            # Get the newly discovered coin symbols (coins updated in the last hour with metadata)
            recent_threshold = datetime.now(UTC) - timedelta(hours=1)
            new_coins = (
                db.query(Coin)
                .filter(
                    Coin.last_updated >= recent_threshold,
                    Coin.name.isnot(None),  # Only coins with metadata (newly enriched)
                )
                .all()
            )

            new_coin_symbols = [coin.symbol for coin in new_coins]

            if new_coin_symbols:
                # Backfill 7 days of historical data for new coins
                logger.info(f"Starting historical backfill for {len(new_coin_symbols)} new coins")
                backfilled_count = await coingecko_service.backfill_historical_data_for_new_coins(
                    new_coin_symbols, days_back=7
                )
                logger.info(f"Historical backfill completed: {backfilled_count} coins processed")
            else:
                logger.info("No new coins found requiring historical backfill")

        else:
            logger.debug("No new coins found needing metadata")

    except Exception as e:
        logger.error(f"Error in new coin discovery: {e}")
    finally:
        db.close()


async def health_monitoring_job():
    """
    Scheduled job to monitor data health and API connectivity
    """
    db: Session = next(get_db())

    try:
        logger.info(f"Running health check at {datetime.now(UTC)}")

        stale_threshold = datetime.now(UTC) - timedelta(minutes=5)
        stale_coins = db.query(Coin).filter(Coin.last_updated < stale_threshold).count()

        if stale_coins > 0:
            logger.warning(f"Found {stale_coins} coins with stale price data (>5 minutes old)")

        # Check total coin count
        total_coins = db.query(Coin).count()
        logger.info(f"Health check: {total_coins} total coins, {stale_coins} stale")

        # TODO: Add more health checks
        # - Exchange API connectivity
        # - Database response times
        # - Missing critical data

    except Exception as e:
        logger.error(f"Error in health monitoring: {e}")
    finally:
        db.close()


async def aggregate_price_data_job():
    """
    Scheduled job to aggregate raw price data into OHLC intervals
    Creates professional time-series data for charts
    """
    db: Session = next(get_db())

    try:
        logger.info(f"Starting price data aggregation at {datetime.now(UTC)}")

        aggregation_service = AggregationService(db)

        # Process all aggregations (5m, 1h, 1d, 1w)
        results = aggregation_service.process_all_aggregations()

        logger.info(f"Aggregation completed: {results}")

    except Exception as e:
        logger.error(f"Error in aggregation job: {e}")
    finally:
        db.close()


async def cleanup_old_data_job():
    """
    Scheduled job to clean up old time-series data
    Maintains retention policies for each interval
    """
    db: Session = next(get_db())

    try:
        logger.info(f"Starting data cleanup at {datetime.now(UTC)}")

        aggregation_service = AggregationService(db)

        # Clean up old data according to retention policies
        results = aggregation_service.process_all_cleanup()

        logger.info(f"Cleanup completed: {results}")

    except Exception as e:
        logger.error(f"Error in cleanup job: {e}")
    finally:
        db.close()


# ==================== SCHEDULER MANAGEMENT ====================


def start_scheduler():
    """Start the background scheduler"""
    global _scheduler_running

    if _scheduler_running:
        logger.warning("Scheduler is already running")
        return

    try:
        # Clear any existing jobs
        scheduler.remove_all_jobs()

        # Add price update job (every 30 seconds)
        # This now includes market cap ranking updates
        scheduler.add_job(
            update_prices_job,
            trigger=IntervalTrigger(seconds=30),
            id="update_prices",
            name="Update cryptocurrency prices + rankings",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping runs
        )

        # Add new coin discovery job (every 6 hours)
        # Only enriches NEW coins, not existing ones
        scheduler.add_job(
            discover_new_coins_job,
            trigger=IntervalTrigger(hours=6),
            id="discover_coins",
            name="Discover and enrich new coins",
            replace_existing=True,
            max_instances=1,
        )

        # Add health monitoring job (every hour)
        scheduler.add_job(
            health_monitoring_job,
            trigger=IntervalTrigger(hours=1),
            id="health_check",
            name="Monitor data health and connectivity",
            replace_existing=True,
            max_instances=1,
        )

        # Add aggregation job (every 5 minutes) - ADD THIS
        scheduler.add_job(
            aggregate_price_data_job,
            trigger=IntervalTrigger(minutes=5),
            id="aggregate_data",
            name="Aggregate raw data into OHLC intervals",
            replace_existing=True,
            max_instances=1,
        )

        # Add cleanup job (daily) - ADD THIS
        scheduler.add_job(
            cleanup_old_data_job,
            trigger=IntervalTrigger(hours=24),
            id="cleanup_data",
            name="Clean up old time-series data",
            replace_existing=True,
            max_instances=1,
        )

        # Start the scheduler
        scheduler.start()
        _scheduler_running = True

        logger.info("Background scheduler started successfully")
        logger.info("Schedule:")
        logger.info("  - Price updates + rankings: Every 30 seconds")
        logger.info("  - Data aggregation (OHLC): Every 5 minutes")
        logger.info("  - Data cleanup: Daily")
        logger.info("  - New coin discovery: Every 6 hours")
        logger.info("  - Health monitoring: Every hour")
        logger.info("  - Data retention: ALL price history kept permanently")

    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise


def stop_scheduler():
    """Stop the background scheduler"""
    global _scheduler_running

    if not _scheduler_running:
        logger.warning("Scheduler is not running")
        return

    try:
        scheduler.shutdown(wait=True)
        _scheduler_running = False
        logger.info("Background scheduler stopped successfully")

    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise


def pause_scheduler():
    """Pause the scheduler (useful during maintenance)"""
    if _scheduler_running:
        scheduler.pause()
        logger.info("Scheduler paused")
    else:
        logger.warning("Cannot pause - scheduler is not running")


def resume_scheduler():
    """Resume the paused scheduler"""
    if _scheduler_running:
        scheduler.resume()
        logger.info("Scheduler resumed")
    else:
        logger.warning("Cannot resume - scheduler is not running")


def get_scheduler_status() -> dict:
    """Get current scheduler status and job information"""

    status = {"running": _scheduler_running, "jobs": [], "next_runs": {}}

    if _scheduler_running and scheduler.running:
        # Get job information
        for job in scheduler.get_jobs():
            job_info = {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            status["jobs"].append(job_info)

            if job.next_run_time:
                status["next_runs"][job.id] = job.next_run_time.isoformat()

    return status


def trigger_job_now(job_id: str) -> bool:
    """Manually trigger a scheduled job immediately"""

    if not _scheduler_running:
        logger.error("Cannot trigger job - scheduler is not running")
        return False

    try:
        # Get the job
        job = scheduler.get_job(job_id)
        if not job:
            logger.error(f"Job '{job_id}' not found")
            return False

        # Schedule it to run now
        scheduler.modify_job(job_id, next_run_time=datetime.now())
        logger.info(f"Job '{job_id}' triggered to run immediately")
        return True

    except Exception as e:
        logger.error(f"Error triggering job '{job_id}': {e}")
        return False


# ==================== SCHEDULER ENDPOINTS (for admin routes) ====================


async def start_scheduler_endpoint():
    """Endpoint wrapper for starting scheduler"""
    try:
        start_scheduler()
        return {"success": True, "message": "Background scheduler started", "status": get_scheduler_status()}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to start scheduler"}


async def stop_scheduler_endpoint():
    """Endpoint wrapper for stopping scheduler"""
    try:
        stop_scheduler()
        return {"success": True, "message": "Background scheduler stopped"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to stop scheduler"}


async def get_scheduler_status_endpoint():
    """Endpoint wrapper for scheduler status"""
    try:
        status = get_scheduler_status()
        return {"success": True, "data": status, "message": "Scheduler status retrieved"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to get scheduler status"}
