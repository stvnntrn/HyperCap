import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as crypto_router
from .scheduler import start_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(crypto_router)


@app.on_event("startup")
async def startup_event():
    start_scheduler()
    logger.info("FastAPI application started")


@app.on_event("shutdown")
async def shutdown_event():
    from .scheduler import scheduler

    scheduler.shutdown()
    logger.info("Scheduler and FastAPI application shut down")


@app.get("/")
async def root():
    return {"message": "Welcome to your crypto API!"}
