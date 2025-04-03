import logging
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_24HR_URL = "https://api.binance.com/api/v3/ticker/24hr"


async def fetch_all_ticker_data():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BINANCE_24HR_URL)
            response.raise_for_status()
            data = response.json()
            if not data:
                logger.warning("Binance returned empty ticker data")
                return []
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Binance API error: {str(e)}")
            raise HTTPException(status_code=e.response.status_code, detail="Binance API issue")
        except Exception as e:
            logger.error(f"Error fetching ticker data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


def process_ticker_data(data):
    # Step 1: Collect reference prices for conversion (USDT-based pairs)
    reference_prices = {}
    for item in data:
        symbol = item["symbol"]
        if symbol.endswith("USDT"):
            try:
                base = symbol[:-4]
                price = item.get("lastPrice")
                if price is not None:
                    reference_prices[base] = float(price)
                else:
                    logger.warning(f"Missing lastPrice for {symbol}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid price data for {symbol}: {str(e)}")

    # Step 2: Process pairs
    processed_coins = {}
    seen_bases = set()

    for item in data:
        symbol = item["symbol"]
        quote = symbol[-3:] if len(symbol) <= 6 else symbol[-4:]
        base = symbol[: -len(quote)]

        if base in seen_bases:
            continue

        try:
            price = float(item.get("lastPrice", 0))  # Default to 0 if missing
            coin_data = {
                "symbol": symbol,
                "price_usdt": price,
                "price_change": float(item.get("priceChange", 0)),
                "price_change_percent": float(item.get("priceChangePercent", 0)),
                "high_24h": float(item.get("highPrice", 0)),
                "low_24h": float(item.get("lowPrice", 0)),
                "volume": float(item.get("volume", 0)),
                "quote_volume": float(item.get("quoteVolume", 0)),
                "weighted_avg_price": float(item.get("weightedAvgPrice", 0)),
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid data for {symbol}: {str(e)}")
            continue

        # Priority: Direct stablecoin pairs
        if quote in ["USDT", "USDC", "FDUSD"]:
            processed_coins[base] = coin_data
            seen_bases.add(base)
        # Convert non-stablecoin pairs to USDT
        elif quote in reference_prices and base not in seen_bases:
            conversion_rate = reference_prices[quote]
            coin_data["price_usdt"] = price * conversion_rate
            coin_data["price_change"] = coin_data["price_change"] * conversion_rate
            coin_data["high_24h"] = coin_data["high_24h"] * conversion_rate
            coin_data["low_24h"] = coin_data["low_24h"] * conversion_rate
            coin_data["quote_volume"] = coin_data["quote_volume"] * conversion_rate
            coin_data["weighted_avg_price"] = coin_data["weighted_avg_price"] * conversion_rate
            processed_coins[base] = coin_data
            seen_bases.add(base)
        else:
            logger.debug(f"Skipping {symbol} - no stablecoin pair or reference price")

    return list(processed_coins.values())


@app.get("/alldata/")
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


@app.get("/marketcap/")
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


@app.get("/price/{symbol}")
async def get_crypto_price(symbol: str):
    symbol = symbol.upper()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BINANCE_API_URL, params={"symbol": symbol})
            response.raise_for_status()
            data = response.json()
            return {
                "status": "success",
                "symbol": data["symbol"],
                "price": float(data["price"]),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch {symbol}: {str(e)}")
            raise HTTPException(status_code=404, detail="Invalid symbol or Binance API issue")
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Welcome to your crypto API!"}
