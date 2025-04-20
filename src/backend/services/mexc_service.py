import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

import ccxt.async_support as ccxt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.mexc_coin import MexCCoinData

logger = logging.getLogger(__name__)


async def fetch_mexc_ticker_data(db: Session) -> List[Dict[str, Any]]:
    async with ccxt.mexc() as exchange:
        for attempt in range(3):
            try:
                # Fetch all markets
                markets = await exchange.load_markets()
                symbols = list(markets.keys())  # e.g., ["BTC/USDT", "ETH/USDT"]

                # Fetch ticker data for all symbols
                tickers = await exchange.fetch_tickers(symbols)
                if not tickers:
                    logger.warning("MEXC returned empty ticker data")
                    return []

                logger.info(f"Fetched {len(tickers)} pairs from MEXC")
                return await process_ticker_data(db, tickers, markets)
            except ccxt.RateLimitExceeded:
                wait_time = 2**attempt
                logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
            except ccxt.BaseError as e:
                logger.error(f"MEXC API error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"MEXC API issue: {str(e)}")
        logger.error("Max retries exceeded for MEXC API")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


async def process_ticker_data(db: Session, tickers: Dict[str, Any], markets: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Build reference prices for USD conversion
    reference_prices = {}
    for symbol, ticker in tickers.items():
        if symbol.endswith("USDT"):
            try:
                base = markets[symbol]["base"]  # e.g., "BTC"
                price = float(ticker["last"])  # Last close price
                reference_prices[base] = price
            except (ValueError, TypeError, KeyError):
                logger.warning(f"Invalid USDT price for {symbol}")

    processed_pairs = []
    for symbol, ticker in tickers.items():
        market = markets.get(symbol, {})
        try:
            base = market.get("base", symbol.split("/")[0])  # e.g., "BTC"
            quote = market.get("quote", symbol.split("/")[1])  # e.g., "USDT"
            price = float(ticker["last"])  # Last close price
            price_usdt = (
                price
                if quote == "USDT"
                else (price * reference_prices.get(base, 0) if base in reference_prices else None)
            )

            # Volume is base asset volume
            volume_24h = float(ticker.get("baseVolume", 0))
            # Quote volume = volume * weighted average price
            weighted_avg_price = float(ticker.get("vwap", price))  # Fallback to last price
            quote_volume_24h = volume_24h * weighted_avg_price if volume_24h and weighted_avg_price else 0

            # Price change: (close - open) / open * 100
            open_price = float(ticker.get("open", price))
            price_change = price - open_price if open_price else 0
            price_change_percent = (price_change / open_price * 100) if open_price and price_change else 0

            # Query existing supply data for market cap
            existing_coin = db.query(MexCCoinData).filter(MexCCoinData.pair == symbol).first()
            circulating_supply = existing_coin.circulating_supply if existing_coin else None
            total_supply = existing_coin.total_supply if existing_coin else None

            market_cap = None
            if price_usdt:
                if circulating_supply is not None and circulating_supply > 0:
                    market_cap = price_usdt * circulating_supply
                elif total_supply is not None and total_supply > 0:
                    market_cap = price_usdt * total_supply
                    logger.debug(f"Used total_supply for market_cap of {symbol}")

            pair_data = {
                "pair": symbol,
                "coin_name": existing_coin.coin_name if existing_coin else None,
                "coin_abbr": base,
                "quote_currency": quote,
                "price": price,
                "price_usdt": price_usdt,
                "price_change": price_change,
                "price_change_percent": price_change_percent,
                "high_24h": float(ticker.get("high", price)),
                "low_24h": float(ticker.get("low", price)),
                "open_price_24h": open_price,
                "close_price_24h": price,
                "volume_24h": volume_24h,
                "quote_volume_24h": quote_volume_24h,
                "weighted_avg_price": weighted_avg_price,
                "market_cap": market_cap,
                "circulating_supply": circulating_supply,
                "total_supply": total_supply,
                "max_supply": existing_coin.max_supply if existing_coin else None,
                "last_updated": datetime.now(UTC),
            }
            processed_pairs.append(pair_data)
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Invalid data for {symbol}: {str(e)}")

    logger.info(f"Processed {len(processed_pairs)} pairs from MEXC")
    return processed_pairs


async def get_mexc_price(pair: str) -> Dict[str, Any]:
    async with ccxt.mexc() as exchange:
        try:
            ticker = await exchange.fetch_ticker(pair.upper())
            price = float(ticker["last"])
            logger.info(f"Fetched real-time price for {pair}: {price}")
            return {"status": "success", "pair": pair, "price": price}
        except ccxt.BaseError as e:
            logger.error(f"Error fetching price for {pair}: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Pair {pair} not found or API error")
