from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BinanceCoinData
from ..schemas.coin import CoinInDB
from ..services.binance_service import fetch_ticker_data, get_crypto_price
from ..services.coin_service import store_coin_data

router = APIRouter()


@router.get("/marketcap/")
async def get_marketcap_data(page: Optional[int] = 1, size: Optional[int] = 100, db: Session = Depends(get_db)):
    """List USDT pairs, sorted by price_usdt (market_cap later when supply is added)."""
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Page and size must be positive")
    skip = (page - 1) * size
    # Filter to USDT pairs; sort by price_usdt until market_cap is populated
    coins = (
        db.query(BinanceCoinData)
        .filter(BinanceCoinData.quote_currency == "USDT")
        .order_by(BinanceCoinData.price_usdt.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    total = db.query(BinanceCoinData).filter(BinanceCoinData.quote_currency == "USDT").count()
    return {"status": "success", "data": [CoinInDB.model_validate(coin) for coin in coins], "total": total}


@router.get("/coin/{coin_abbr}")
async def get_coin_details(coin_abbr: str, db: Session = Depends(get_db)):
    """Get details for a coin's USDT pair."""
    # Auto-uppercase the coin abbreviation
    coin_abbr = coin_abbr.upper()
    coin = (
        db.query(BinanceCoinData)
        .filter(BinanceCoinData.coin_abbr == coin_abbr, BinanceCoinData.quote_currency == "USDT")
        .first()
    )
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found in USDT pair")
    return {
        "status": "success",
        "coin": CoinInDB.model_validate(coin),
        "available_on": ["Binance"],  # Hardcoded for now, expand later
    }


@router.get("/fetch-and-store/")
async def fetch_and_store(db: Session = Depends(get_db)):
    """Fetch and store all Binance ticker data."""
    ticker_data = await fetch_ticker_data(db)
    records = store_coin_data(db, ticker_data)
    return {"status": "success", "message": "Binance data fetched and stored", "records": records}


@router.get("/price/{pair}")
async def get_price(pair: str):
    """Get real-time price for a specific pair."""
    return await get_crypto_price(pair)
