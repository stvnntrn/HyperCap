import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as crypto_router
from .tasks import scheduler, start_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("🚀 FastAPI application starting up...")

    try:
        # 1. First check for data gaps and backfill if needed
        logger.info("🔍 Checking for historical data gaps...")
        from .database import SessionLocal
        from .services.historical_data_service import HistoricalDataService

        db = SessionLocal()
        try:
            historical_service = HistoricalDataService(db)

            # Run startup gap check (this will automatically backfill if needed)
            startup_result = await historical_service.startup_gap_check_and_fill(max_gap_hours=2)

            if startup_result["status"] == "no_action_needed":
                logger.info("✅ All historical data is current - no backfill needed")
            elif startup_result["status"] == "gaps_filled":
                logger.info(f"✅ {startup_result['message']}")
            else:
                logger.warning(f"⚠️ Startup gap check: {startup_result}")

        finally:
            db.close()

        # 2. Start the scheduler for real-time data
        logger.info("⏰ Starting background scheduler...")
        start_scheduler()

        logger.info("🎉 FastAPI application started successfully!")
        logger.info("📊 Real-time data fetching: ACTIVE")
        logger.info("🔄 Background jobs: RUNNING")
        logger.info("📈 Historical data: CURRENT")

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        # Continue anyway - don't crash the app
        logger.info("⚠️ Starting with limited functionality...")

    yield

    # Shutdown sequence
    logger.info("🛑 FastAPI application shutting down...")
    try:
        scheduler.shutdown()
        logger.info("✅ Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")

    logger.info("👋 FastAPI application shut down complete")


app = FastAPI(
    title="Crypto Price API",
    description="Comprehensive cryptocurrency price tracking with historical data",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(crypto_router)


@app.get("/")
async def root():
    return {"message": "Welcome to your crypto API!"}
