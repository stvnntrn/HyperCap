from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_24HR_URL = "https://api.binance.com/api/v3/ticker/24hr"


async def fetch_all_ticker_data():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BINANCE_24HR_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Binance API issue")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/marketcap/")
async def get_marketcap_data(limit: int = 100, quote_asset: Optional[str] = "USDT"):
    data = await fetch_all_ticker_data()

    # Process & filter data
    filtered_data = [
        {
            "symbol": item["symbol"],
            "price": float(item["lastPrice"]),
            "price_change": float(item["priceChange"]),
            "price_change_percent": float(item["priceChangePercent"]),
            "high_24h": float(item["highPrice"]),
            "low_24h": float(item["lowPrice"]),
            "volume": float(item["volume"]),
            "quote_volume": float(item["quoteVolume"]),
            "weighted_avg_price": float(item["weightedAvgPrice"]),
        }
        for item in data
        if item["symbol"].endswith(quote_asset.upper())
    ]

    # Sort by quote volume (proxy for market cap) and limit
    filtered_data = sorted(filtered_data, key=lambda x: x["quote_volume"], reverse=True)[:limit]

    return {"status": "success", "data": filtered_data, "total": len(filtered_data)}


@app.get("/price/{symbol}")
async def get_crypto_price(symbol: str):
    symbol = symbol.upper()  # Ensure uppercase
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BINANCE_API_URL, params={"symbol": symbol})
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["price"]),
                "status": "success",
            }
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail="Invalid symbol or Binance API issue")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Welcome to your crypto API!"}
