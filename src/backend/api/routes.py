from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud.coin import get_coin, get_coins
from ..database import get_db
from ..schemas.coin import CoinInDB
from ..services.binance_service import fetch_and_store_ticker_data, get_crypto_price

router = APIRouter()


@router.get("/alldata/")
async def get_all_data(limit: Optional[int] = None, db: Session = Depends(get_db)):
    coins = get_coins(db, limit=limit if limit else 1000)
    return {"status": "success", "data": [CoinInDB.model_validate(coin) for coin in coins], "total": len(coins)}


@router.get("/marketcap/")
async def get_marketcap_data(page: Optional[int] = 1, size: Optional[int] = 100, db: Session = Depends(get_db)):
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Page and size must be positive")

    skip = (page - 1) * size
    coins = get_coins(db, skip=skip, limit=size, sort_by="quote_volume_24h", sort_order="desc")
    total = len(get_coins(db))

    if not coins:
        return {"status": "success", "data": [], "total": total}

    return {"status": "success", "data": [CoinInDB.model_validate(coin) for coin in coins], "total": total}


@router.get("/price/{symbol}")
async def get_price(symbol: str, db: Session = Depends(get_db)):
    coin = get_coin(db, symbol.upper())
    if not coin:
        return await get_crypto_price(symbol)
    return {"status": "success", "symbol": coin.symbol, "price": coin.price_usdt}  # Could use CoinInDB here too


@router.get("/db-test/")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        count = len(get_coins(db))
        return {"status": "success", "message": "Database connection successful", "total_records": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


@router.get("/fetch-and-store/")
async def fetch_and_store(db: Session = Depends(get_db)):
    return await fetch_and_store_ticker_data(db)
