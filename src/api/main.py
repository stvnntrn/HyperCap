import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"


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
