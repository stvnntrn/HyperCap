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
    # Startup: Start the scheduler
    start_scheduler()
    logger.info("FastAPI application started")
    yield
    # Shutdown: Stop the scheduler
    scheduler.shutdown()
    logger.info("Scheduler and FastAPI application shut down")


app = FastAPI(lifespan=lifespan)

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
