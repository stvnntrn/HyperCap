import os
from typing import List

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST: str = os.getenv("DB_HOST", "")
DB_PORT: str = os.getenv("DB_PORT", "")
DB_NAME: str = os.getenv("DB_NAME", "")
DB_USER: str = os.getenv("DB_USER", "")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Binance API configuration
BINANCE_API_URL: str = os.getenv("BINANCE_API_URL", "")
BINANCE_24HR_URL: str = os.getenv("BINANCE_24HR_URL", "")
BINANCE_INFO_URL: str = os.getenv("BINANCE_INFO_URL", "")

# Kraken API configuration
KRAKEN_API_URL: str = os.getenv("KRAKEN_API_URL", "")

# MEXC API configuration
MEXC_API_URL: str = os.getenv("MEXC_API_URL", "")

# Logging configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# CORS configuration
CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
