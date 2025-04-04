import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.crypto_routes import router as crypto_router
from .config import API_PREFIX

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
app.include_router(crypto_router, prefix=API_PREFIX)


@app.get("/")
async def root():
    return {"message": "Welcome to your crypto API!"}
