from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.coin import CoinData
from ..services.binance_service import fetch_all_ticker_data, get_crypto_price, process_ticker_data

router = APIRouter()


@router.get("/alldata/")
async def get_all_data(limit: Optional[int] = None):
    data = await fetch_all_ticker_data()
    filtered_data = [
        {
            "symbol": item["symbol"],
            "price": float(item.get("lastPrice", 0)),
            "price_change": float(item.get("priceChange", 0)),
            "price_change_percent": float(item.get("priceChangePercent", 0)),
            "high_24h": float(item.get("highPrice", 0)),
            "low_24h": float(item.get("lowPrice", 0)),
            "volume": float(item.get("volume", 0)),
            "quote_volume": float(item.get("quoteVolume", 0)),
            "weighted_avg_price": float(item.get("weightedAvgPrice", 0)),
        }
        for item in data
    ]
    return {"status": "success", "data": filtered_data[:limit] if limit else filtered_data, "total": len(filtered_data)}


@router.get("/marketcap/")
async def get_marketcap_data(page: Optional[int] = 1, size: Optional[int] = 100):
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Page and size must be positive")

    data = await fetch_all_ticker_data()
    if not data:
        raise HTTPException(status_code=404, detail="No ticker data available from Binance")

    processed_data = process_ticker_data(data)
    sorted_data = sorted(processed_data, key=lambda x: x["quote_volume"], reverse=True)

    start = (page - 1) * size
    if start >= len(sorted_data):
        return {"status": "success", "data": [], "total": len(sorted_data)}
    end = min(start + size, len(sorted_data))

    return {"status": "success", "data": sorted_data[start:end], "total": len(sorted_data)}


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    return await get_crypto_price(symbol)


@router.get("/db-test/")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Test database connection by trying to get count of records
        count = db.query(CoinData).count()
        return {"status": "success", "message": "Database connection successful", "total_records": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
