import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.models import ExchangePair

logger = logging.getLogger(__name__)


class ExchangeService:
    """
    Service for fetching data from cryptocurrency exchanges
    """

    def __init__(self, db: Session):
        self.db = db
        self.timeout = 30.0
        self.max_retries = 3

        # Load URLs from environment
        self.binance_api_url = os.getenv("BINANCE_API_URL", "https://api.binance.com/api/v3")
        self.binance_24hr_url = os.getenv("BINANCE_24HR_URL", "https://api.binance.com/api/v3/ticker/24hr")
        self.kraken_api_url = os.getenv("KRAKEN_API_URL", "https://api.kraken.com")
        self.mexc_api_url = os.getenv("MEXC_API_URL", "https://www.mexc.com/open/api/v3")
        self.coingecko_api_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")

    # ==================== BINANCE API ====================

    async def fetch_binance_data(self) -> List[Dict[str, Any]]:
        """Fetch ticker data from Binance - ALL pairs"""
        url = self.binance_24hr_url

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                processed_data = []
                usd_reference_prices = {}

                # First pass: collect USDT prices for conversion
                for ticker in data:
                    symbol = ticker["symbol"]
                    if symbol.endswith("USDT"):
                        base_symbol, _ = self._parse_binance_symbol(symbol)
                        if base_symbol:
                            usd_reference_prices[base_symbol] = float(ticker["lastPrice"])

                # Second pass: process all pairs
                for ticker in data:
                    try:
                        symbol = ticker["symbol"]

                        # Skip very low volume pairs (less than $10k daily volume)
                        quote_volume = float(ticker.get("quoteVolume", 0))
                        if quote_volume < 10000:
                            continue

                        # Parse symbol
                        base_symbol, quote_currency = self._parse_binance_symbol(symbol)
                        if not base_symbol or not quote_currency:
                            continue

                        last_price = float(ticker["lastPrice"])

                        # Convert to USD
                        price_usd = self._convert_to_usd(last_price, quote_currency, usd_reference_prices)

                        processed_data.append(
                            {
                                "symbol": base_symbol,
                                "exchange": "binance",
                                "pair": symbol,
                                "quote_currency": quote_currency,
                                "price_usd": price_usd,
                                "price_24h_high": float(ticker["highPrice"]),
                                "price_24h_low": float(ticker["lowPrice"]),
                                "price_change_24h": float(ticker["priceChangePercent"]),
                                "volume_24h_base": float(ticker["volume"]),
                                "volume_24h_usd": quote_volume,
                                "timestamp": datetime.now(UTC),
                            }
                        )
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error processing Binance ticker {symbol}: {e}")
                        continue

                logger.info(f"Fetched {len(processed_data)} pairs from Binance")
                return processed_data

            except httpx.HTTPError as e:
                logger.error(f"Binance API error: {e}")
                return []

    def _parse_binance_symbol(self, symbol: str) -> tuple[Optional[str], Optional[str]]:
        """Parse Binance symbol into base and quote (simple but effective)"""
        # Common quote currencies (order matters - longest first)
        quote_currencies = ["USDT", "BUSD", "USDC", "TUSD", "BTC", "ETH", "BNB", "ADA", "XRP", "DOT", "USD"]

        for quote in quote_currencies:
            if symbol.endswith(quote):
                base = symbol[: -len(quote)]
                if len(base) > 0:
                    return base, quote

        return None, None

    def _convert_to_usd(self, price: float, quote_currency: str, reference_prices: Dict[str, float]) -> Optional[float]:
        """Convert price to USD using reference prices"""
        if quote_currency in ["USDT", "BUSD", "USDC", "TUSD", "USD"]:
            return price
        elif quote_currency in reference_prices:
            return price * reference_prices[quote_currency]
        else:
            return None

    # ==================== KRAKEN API ====================

    async def fetch_kraken_data(self) -> List[Dict[str, Any]]:
        """Fetch ticker data from Kraken - ALL pairs"""
        pairs_url = f"{self.kraken_api_url}/0/public/AssetPairs"
        ticker_url = f"{self.kraken_api_url}/0/public/Ticker"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Get asset pairs
                pairs_response = await client.get(pairs_url)
                pairs_response.raise_for_status()
                pairs_data = pairs_response.json()["result"]

                # Get ticker data for all pairs
                ticker_response = await client.get(ticker_url)
                ticker_response.raise_for_status()
                ticker_data = ticker_response.json()["result"]

                processed_data = []
                usd_reference_prices = {}

                # First pass: collect USD prices for conversion
                for pair, ticker in ticker_data.items():
                    if pair.endswith("USD") or pair.endswith("ZUSD"):
                        pair_info = pairs_data.get(pair, {})
                        base = pair_info.get("base", "").replace("X", "").replace("Z", "")
                        if base == "XBT":
                            base = "BTC"
                        usd_reference_prices[base] = float(ticker["c"][0])

                # Second pass: process all pairs
                for pair, ticker in ticker_data.items():
                    try:
                        pair_info = pairs_data.get(pair, {})
                        base = pair_info.get("base", "").replace("X", "").replace("Z", "")
                        quote = pair_info.get("quote", "").replace("X", "").replace("Z", "")

                        # Normalize symbols
                        if base == "XBT":
                            base = "BTC"
                        if quote == "XBT":
                            quote = "BTC"

                        last_price = float(ticker["c"][0])
                        volume_24h = float(ticker["v"][1])

                        # Skip very low volume pairs
                        if volume_24h < 1:
                            continue

                        # Convert to USD
                        price_usd = self._convert_to_usd(last_price, quote, usd_reference_prices)

                        # Calculate price change
                        open_price = float(ticker["o"])
                        price_change_24h = ((last_price - open_price) / open_price * 100) if open_price else 0

                        processed_data.append(
                            {
                                "symbol": base,
                                "exchange": "kraken",
                                "pair": pair,
                                "quote_currency": quote,
                                "price_usd": price_usd,
                                "price_24h_high": float(ticker["h"][1]),
                                "price_24h_low": float(ticker["l"][1]),
                                "price_change_24h": price_change_24h,
                                "volume_24h_base": volume_24h,
                                "volume_24h_usd": volume_24h * last_price if price_usd else None,
                                "timestamp": datetime.now(UTC),
                            }
                        )
                    except (ValueError, KeyError, IndexError) as e:
                        logger.warning(f"Error processing Kraken ticker {pair}: {e}")
                        continue

                logger.info(f"Fetched {len(processed_data)} pairs from Kraken")
                return processed_data

            except httpx.HTTPError as e:
                logger.error(f"Kraken API error: {e}")
                return []

    # ==================== MEXC API ====================

    async def fetch_mexc_data(self) -> List[Dict[str, Any]]:
        """Fetch ticker data from MEXC - ALL pairs"""
        # MEXC v3 API endpoint for tickers
        url = f"{self.mexc_api_url}/ticker/24hr"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                # MEXC v3 returns a direct list, not nested in "data"
                if not isinstance(data, list):
                    logger.warning(f"MEXC returned unexpected format: {type(data)}")
                    return []

                if not data:
                    logger.warning("MEXC returned empty ticker data")
                    return []

                processed_data = []
                usd_reference_prices = {}

                # First pass: collect USDT prices for conversion
                for ticker in data:
                    symbol = ticker.get("symbol", "")
                    if symbol.endswith("USDT"):
                        base_symbol, _ = self._parse_mexc_symbol(symbol)
                        if base_symbol:
                            last_price = ticker.get("lastPrice", "0")
                            if last_price and float(last_price) > 0:
                                usd_reference_prices[base_symbol] = float(last_price)

                # Second pass: process all pairs
                for ticker in data:
                    try:
                        symbol = ticker.get("symbol", "")

                        # Skip very low volume pairs
                        volume = float(ticker.get("volume", 0))
                        if volume < 1000:  # Lower threshold for MEXC
                            continue

                        base_symbol, quote_currency = self._parse_mexc_symbol(symbol)
                        if not base_symbol or not quote_currency:
                            continue

                        last_price = float(ticker.get("lastPrice", 0))
                        if last_price <= 0:
                            continue

                        # Convert to USD
                        price_usd = self._convert_to_usd(last_price, quote_currency, usd_reference_prices)

                        # Calculate 24h change - MEXC v3 provides priceChangePercent
                        price_change_24h = float(ticker.get("priceChangePercent", 0))

                        processed_data.append(
                            {
                                "symbol": base_symbol,
                                "exchange": "mexc",
                                "pair": symbol,
                                "quote_currency": quote_currency,
                                "price_usd": price_usd,
                                "price_24h_high": float(ticker.get("highPrice", last_price)),
                                "price_24h_low": float(ticker.get("lowPrice", last_price)),
                                "price_change_24h": price_change_24h,
                                "volume_24h_base": volume,
                                "volume_24h_usd": volume * last_price if price_usd else None,
                                "timestamp": datetime.now(UTC),
                            }
                        )
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error processing MEXC ticker {symbol}: {e}")
                        continue

                logger.info(f"Fetched {len(processed_data)} pairs from MEXC")
                return processed_data

            except httpx.HTTPError as e:
                logger.error(f"MEXC API error: {e}")
                return []

    def _parse_mexc_symbol(self, symbol: str) -> tuple[Optional[str], Optional[str]]:
        """Parse MEXC symbol into base and quote"""
        quote_currencies = ["USDT", "USDC", "BTC", "ETH"]

        for quote in quote_currencies:
            if symbol.endswith(quote):
                base = symbol[: -len(quote)]
                if len(base) > 0:
                    return base, quote

        return None, None

    # ==================== AGGREGATE DATA ====================

    async def fetch_all_exchange_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch data from all exchanges concurrently"""
        logger.info("Starting to fetch data from all exchanges")

        # Run all exchange fetches concurrently
        tasks = [self.fetch_binance_data(), self.fetch_kraken_data(), self.fetch_mexc_data()]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            exchange_data = {
                "binance": results[0] if not isinstance(results[0], Exception) else [],
                "kraken": results[1] if not isinstance(results[1], Exception) else [],
                "mexc": results[2] if not isinstance(results[2], Exception) else [],
            }

            # Log results
            for exchange, data in exchange_data.items():
                if isinstance(data, list):
                    logger.info(f"{exchange}: {len(data)} pairs fetched")
                else:
                    logger.error(f"{exchange}: Failed to fetch data")

            return exchange_data

        except Exception as e:
            logger.error(f"Error fetching exchange data: {e}")
            return {"binance": [], "kraken": [], "mexc": []}

    def update_exchange_pairs(self, exchange_data: Dict[str, List[Dict[str, Any]]]) -> int:
        """Update exchange pairs table with current data"""
        updated_count = 0

        # Mark all pairs as inactive first
        self.db.query(ExchangePair).update({ExchangePair.is_active: False})

        for exchange, pairs_data in exchange_data.items():
            for pair_data in pairs_data:
                try:
                    symbol = pair_data["symbol"]
                    pair = pair_data["pair"]
                    quote_currency = pair_data["quote_currency"]

                    # Check if pair exists
                    existing_pair = (
                        self.db.query(ExchangePair)
                        .filter(ExchangePair.exchange == exchange, ExchangePair.pair == pair)
                        .first()
                    )

                    if existing_pair:
                        # Update existing
                        existing_pair.symbol = symbol
                        existing_pair.quote_currency = quote_currency
                        existing_pair.is_active = True
                        existing_pair.last_seen = datetime.now(UTC)
                    else:
                        # Create new
                        new_pair = ExchangePair(
                            symbol=symbol,
                            exchange=exchange,
                            pair=pair,
                            quote_currency=quote_currency,
                            is_active=True,
                            last_seen=datetime.now(UTC),
                        )
                        self.db.add(new_pair)

                    updated_count += 1

                except Exception as e:
                    logger.warning(f"Error updating exchange pair {pair_data}: {e}")
                    continue

        self.db.commit()
        logger.info(f"Updated {updated_count} exchange pairs")
        return updated_count

    async def get_single_price(self, exchange: str, symbol: str) -> Optional[float]:
        """Get real-time price for a specific symbol from specific exchange"""
        symbol = symbol.upper()

        if exchange.lower() == "binance":
            url = f"{self.binance_api_url}/ticker/price?symbol={symbol}USDT"
        elif exchange.lower() == "kraken":
            # Convert BTC to XBT for Kraken
            kraken_symbol = "XBT" if symbol == "BTC" else symbol
            url = f"{self.kraken_api_url}/0/public/Ticker?pair={kraken_symbol}USD"
        elif exchange.lower() == "mexc":
            url = f"{self.mexc_api_url}/market/ticker?symbol={symbol}_USDT"
        else:
            return None

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if exchange.lower() == "binance":
                    return float(data["price"])
                elif exchange.lower() == "kraken":
                    ticker_data = list(data["result"].values())[0]
                    return float(ticker_data["c"][0])
                elif exchange.lower() == "mexc":
                    return float(data["price"])

            except Exception as e:
                logger.error(f"Error fetching {symbol} price from {exchange}: {e}")
                return None
