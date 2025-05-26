import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.models.exchange_pairs import ExchangePair

logger = logging.getLogger(__name__)


class ExchangeService:
    """
    Service for fetching data from cryptocurrency exchanges
    """

    def __init__(self, db: Session):
        self.db = db
        self.timeout = 30.0
        self.max_retries = 3

    # ==================== BINANCE API ====================

    async def fetch_binance_data(self) -> List[Dict[str, Any]]:
        """Fetch ticker data from Binance"""
        url = "https://api.binance.com/api/v3/ticker/24hr"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                processed_data = []
                for ticker in data:
                    try:
                        # Extract symbol parts (e.g., BTCUSDT -> BTC + USDT)
                        symbol = ticker["symbol"]

                        # Focus on USDT pairs for price consistency
                        if not symbol.endswith("USDT"):
                            continue

                        base_symbol = symbol[:-4]  # Remove "USDT"

                        processed_data.append(
                            {
                                "symbol": base_symbol,
                                "exchange": "binance",
                                "pair": symbol,
                                "quote_currency": "USDT",
                                "price_usd": float(ticker["lastPrice"]),
                                "price_24h_high": float(ticker["highPrice"]),
                                "price_24h_low": float(ticker["lowPrice"]),
                                "price_change_24h": float(ticker["priceChangePercent"]),
                                "volume_24h_base": float(ticker["volume"]),
                                "volume_24h_usd": float(ticker["quoteVolume"]),
                                "timestamp": datetime.now(UTC),
                            }
                        )
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error processing Binance ticker {symbol}: {e}")
                        continue

                logger.info(f"Fetched {len(processed_data)} USDT pairs from Binance")
                return processed_data

            except httpx.HTTPError as e:
                logger.error(f"Binance API error: {e}")
                return []

    # ==================== KRAKEN API ====================

    async def fetch_kraken_data(self) -> List[Dict[str, Any]]:
        """Fetch ticker data from Kraken"""
        # First get asset pairs
        pairs_url = "https://api.kraken.com/0/public/AssetPairs"
        ticker_url = "https://api.kraken.com/0/public/Ticker"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Get asset pairs
                pairs_response = await client.get(pairs_url)
                pairs_response.raise_for_status()
                pairs_data = pairs_response.json()["result"]

                # Filter USD pairs
                usd_pairs = [pair for pair in pairs_data.keys() if pair.endswith("USD") or pair.endswith("ZUSD")]

                # Get ticker data for USD pairs
                ticker_response = await client.get(ticker_url, params={"pair": ",".join(usd_pairs)})
                ticker_response.raise_for_status()
                ticker_data = ticker_response.json()["result"]

                processed_data = []
                for pair, ticker in ticker_data.items():
                    try:
                        # Get pair info
                        pair_info = pairs_data.get(pair, {})
                        base = pair_info.get("base", "").replace("X", "").replace("Z", "")

                        # Normalize Bitcoin symbol
                        if base == "XBT":
                            base = "BTC"

                        last_price = float(ticker["c"][0])
                        high_24h = float(ticker["h"][1])
                        low_24h = float(ticker["l"][1])
                        volume_24h = float(ticker["v"][1])

                        # Calculate price change
                        open_price = float(ticker["o"])
                        price_change_24h = ((last_price - open_price) / open_price * 100) if open_price else 0

                        processed_data.append(
                            {
                                "symbol": base,
                                "exchange": "kraken",
                                "pair": pair,
                                "quote_currency": "USD",
                                "price_usd": last_price,
                                "price_24h_high": high_24h,
                                "price_24h_low": low_24h,
                                "price_change_24h": price_change_24h,
                                "volume_24h_base": volume_24h,
                                "volume_24h_usd": volume_24h * last_price,
                                "timestamp": datetime.now(UTC),
                            }
                        )
                    except (ValueError, KeyError, IndexError) as e:
                        logger.warning(f"Error processing Kraken ticker {pair}: {e}")
                        continue

                logger.info(f"Fetched {len(processed_data)} USD pairs from Kraken")
                return processed_data

            except httpx.HTTPError as e:
                logger.error(f"Kraken API error: {e}")
                return []

    # ==================== MEXC API ====================

    async def fetch_mexc_data(self) -> List[Dict[str, Any]]:
        """Fetch ticker data from MEXC"""
        url = "https://api.mexc.com/api/v3/ticker/24hr"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                processed_data = []
                for ticker in data:
                    try:
                        symbol = ticker["symbol"]

                        # Focus on USDT pairs
                        if not symbol.endswith("USDT"):
                            continue

                        base_symbol = symbol[:-4]  # Remove "USDT"

                        processed_data.append(
                            {
                                "symbol": base_symbol,
                                "exchange": "mexc",
                                "pair": symbol,
                                "quote_currency": "USDT",
                                "price_usd": float(ticker["lastPrice"]),
                                "price_24h_high": float(ticker["highPrice"]),
                                "price_24h_low": float(ticker["lowPrice"]),
                                "price_change_24h": float(ticker["priceChangePercent"]),
                                "volume_24h_base": float(ticker["volume"]),
                                "volume_24h_usd": float(ticker["quoteVolume"]),
                                "timestamp": datetime.now(UTC),
                            }
                        )
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error processing MEXC ticker {symbol}: {e}")
                        continue

                logger.info(f"Fetched {len(processed_data)} USDT pairs from MEXC")
                return processed_data

            except httpx.HTTPError as e:
                logger.error(f"MEXC API error: {e}")
                return []

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
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        elif exchange.lower() == "kraken":
            # Convert BTC to XBT for Kraken
            kraken_symbol = "XBT" if symbol == "BTC" else symbol
            url = f"https://api.kraken.com/0/public/Ticker?pair={kraken_symbol}USD"
        elif exchange.lower() == "mexc":
            url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
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
