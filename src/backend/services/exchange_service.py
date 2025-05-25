import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import ccxt.async_support as ccxt
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import BINANCE_API_URL, KRAKEN_API_URL, MEXC_API_URL
from ..models.binance_coin import BinanceCoinData
from ..models.kraken_coin import KrakenCoinData
from ..models.mexc_coin import MexCCoinData
from ..utils.normalize import normalize_coin_abbr

logger = logging.getLogger(__name__)


async def fetch_exchange_data(exchange_name: str, db: Session) -> List[Dict[str, Any]]:
    """Fetch ticker data from the specified exchange."""

    async def process_ticker(symbol: str, ticker: Dict[str, Any], market: Dict[str, Any]) -> Dict[str, Any]:
        try:
            base = market.get("base", symbol.split("/")[0]).upper()
            quote = market.get("quote", symbol.split("/")[1]).upper()
            normalized_abbr = normalize_coin_abbr(base, exchange_name)
            price_usdt = float(ticker.get("last", 0)) if quote in ["USDT", "USD", "ZUSD"] else None
            volume_24h = float(ticker.get("baseVolume", ticker.get("volume", 0)))
            quote_volume_24h = float(ticker.get("quoteVolume", volume_24h * ticker.get("last", 0)))

            return {
                "pair": symbol,
                "coin_abbr": normalized_abbr,
                "quote_currency": quote,
                "price_usdt": price_usdt,
                "volume_24h": volume_24h,
                "quote_volume_24h": quote_volume_24h,
                "last_updated": datetime.now(UTC),
            }
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Invalid data for {symbol} on {exchange_name}: {str(e)}")
            return None

    if exchange_name == "binance":
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BINANCE_API_URL}/ticker/24hr")
                response.raise_for_status()
                data = response.json()
                exchange_info = await client.get(f"{BINANCE_API_URL}/exchangeInfo")
                exchange_info.raise_for_status()
                markets = {
                    s["symbol"]: {"base": s["baseAsset"], "quote": s["quoteAsset"]}
                    for s in exchange_info.json()["symbols"]
                }

                processed = [
                    await process_ticker(symbol, ticker, markets.get(symbol, {}))
                    for symbol, ticker in [(item["symbol"], item) for item in data]
                    if symbol.endswith("USDT")
                ]
                return [p for p in processed if p and p["price_usdt"]]
            except httpx.HTTPStatusError as e:
                logger.error(f"Binance API error: {str(e)}")
                raise HTTPException(status_code=e.response.status_code, detail="Binance API error")

    elif exchange_name == "kraken":
        async with httpx.AsyncClient() as client:
            try:
                pairs_response = await client.get(f"{KRAKEN_API_URL}/0/public/AssetPairs")
                pairs_response.raise_for_status()
                pairs_data = pairs_response.json().get("result", {})
                pair_names = [p for p in pairs_data.keys() if p.endswith(("USD", "ZUSD"))]

                batch_size = 20
                batches = [pair_names[i : i + batch_size] for i in range(0, len(pair_names), batch_size)]
                results = []
                for batch in batches:
                    response = await client.get(f"{KRAKEN_API_URL}/0/public/Ticker", params={"pair": ",".join(batch)})
                    response.raise_for_status()
                    ticker_data = response.json().get("result", {})
                    processed = [
                        await process_ticker(pair, ticker_data[pair], pairs_data.get(pair, {})) for pair in batch
                    ]
                    results.extend([p for p in processed if p and p["price_usdt"]])
                    await asyncio.sleep(0.5)  # Respect Kraken rate limits
                return results
            except httpx.HTTPStatusError as e:
                logger.error(f"Kraken API error: {str(e)}")
                raise HTTPException(status_code=e.response.status_code, detail="Kraken API error")

    elif exchange_name == "mexc":
        async with ccxt.mexc() as exchange:
            try:
                markets = await exchange.load_markets()
                symbols = [s for s in markets.keys() if s.endswith("USDT")]
                tickers = await exchange.fetch_tickers(symbols)
                processed = [await process_ticker(symbol, tickers[symbol], markets[symbol]) for symbol in symbols]
                await exchange.close()
                return [p for p in processed if p and p["price_usdt"]]
            except ccxt.BaseError as e:
                logger.error(f"MEXC API error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"MEXC API error: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported exchange")


async def get_crypto_price(exchange: str, pair: str) -> Dict[str, Any]:
    """Fetch real-time price for a specific pair on an exchange."""
    if exchange == "binance":
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BINANCE_API_URL}/ticker/price", params={"symbol": pair.upper()})
                response.raise_for_status()
                price = float(response.json()["price"])
                return {"status": "success", "pair": pair, "price": price}
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail="Binance API error")
    elif exchange == "kraken":
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{KRAKEN_API_URL}/0/public/Ticker", params={"pair": pair.upper()})
                response.raise_for_status()
                data = response.json().get("result", {}).get(pair.upper())
                if not data:
                    raise HTTPException(status_code=404, detail=f"Pair {pair} not found")
                price = float(data["c"][0])
                return {"status": "success", "pair": pair, "price": price}
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail="Kraken API error")
    elif exchange == "mexc":
        async with ccxt.mexc() as exchange:
            try:
                ticker = await exchange.fetch_ticker(pair.upper())
                price = float(ticker["last"])
                return {"status": "success", "pair": pair, "price": price}
            except ccxt.BaseError as e:
                raise HTTPException(status_code=404, detail=f"Pair {pair} not found or API error")
    else:
        raise HTTPException(status_code=400, detail="Unsupported exchange")
