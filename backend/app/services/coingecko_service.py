import asyncio
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.models import Coin
from app.services import CoinService

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """
    Service for fetching metadata from CoinGecko API
    Focused on one-time setup + new coins only approach
    """

    def __init__(self, db: Session):
        self.db = db
        self.coin_service = CoinService(db)
        self.base_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")

        # Rate limiting (CoinGecko free tier: ~10-50 requests/minute)
        self.rate_limit_delay = 1.2  # seconds between requests
        self.timeout = 30.0

        # Cache for symbol-to-id mapping
        self._symbol_to_id_cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=24)

    # ==================== SYMBOL MAPPING ====================

    async def get_symbol_to_id_mapping(self, force_refresh: bool = False) -> Dict[str, str]:
        """Get mapping of symbols to CoinGecko IDs (cached for performance)"""
        now = datetime.now(UTC)

        # Return cached data if still valid
        if (
            not force_refresh
            and self._symbol_to_id_cache
            and self._cache_timestamp
            and now - self._cache_timestamp < self._cache_duration
        ):
            return self._symbol_to_id_cache

        logger.info("Fetching fresh symbol-to-ID mapping from CoinGecko")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.base_url}/coins/list"
                response = await client.get(url)
                response.raise_for_status()

                coins_list = response.json()

                # Build symbol to ID mapping
                symbol_to_id = {}
                for coin in coins_list:
                    symbol = coin.get("symbol", "").upper()
                    coin_id = coin.get("id", "")

                    if symbol and coin_id:
                        # Handle duplicate symbols by preferring more popular coins
                        if symbol not in symbol_to_id:
                            symbol_to_id[symbol] = coin_id

                # Update cache
                self._symbol_to_id_cache = symbol_to_id
                self._cache_timestamp = now

                logger.info(f"Cached {len(symbol_to_id)} symbol mappings from CoinGecko")
                return symbol_to_id

            except Exception as e:
                logger.error(f"Error fetching CoinGecko symbol mapping: {e}")
                return self._symbol_to_id_cache or {}

    # ==================== COMPLETE METADATA FETCHING ====================

    async def fetch_complete_metadata_for_coin(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch complete metadata for a single coin"""
        symbol_to_id = await self.get_symbol_to_id_mapping()
        coin_id = symbol_to_id.get(symbol.upper())

        if not coin_id:
            logger.warning(f"No CoinGecko ID found for symbol {symbol}")
            return None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Get complete coin data
                url = f"{self.base_url}/coins/{coin_id}"
                params = {
                    "localization": False,
                    "tickers": False,
                    "market_data": True,
                    "community_data": False,
                    "developer_data": False,
                }

                response = await client.get(url, params=params)
                response.raise_for_status()

                coin_data = response.json()

                # Extract metadata
                market_data = coin_data.get("market_data", {})
                categories = coin_data.get("categories", [])

                # Filter out null/empty categories
                valid_categories = [cat for cat in categories if cat and cat.strip()]

                metadata = {
                    "name": coin_data.get("name"),
                    "symbol": coin_data.get("symbol", "").upper(),
                    "categories": valid_categories,
                    "circulating_supply": market_data.get("circulating_supply"),
                    "total_supply": market_data.get("total_supply"),
                    "max_supply": market_data.get("max_supply"),
                    "market_cap_rank": market_data.get("market_cap_rank"),
                    "coingecko_id": coin_id,
                }

                logger.info(f"Fetched complete metadata for {symbol}")
                return metadata

            except Exception as e:
                logger.error(f"Error fetching metadata for {symbol}: {e}")
                return None

    async def fetch_complete_metadata_bulk(
        self, symbols: List[str], batch_size: int = 250
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch basic metadata for multiple coins using bulk endpoint"""
        symbol_to_id = await self.get_symbol_to_id_mapping()

        # Filter to only symbols we have IDs for
        valid_symbols = [s for s in symbols if s.upper() in symbol_to_id]
        coin_ids = [symbol_to_id[s.upper()] for s in valid_symbols]

        if not coin_ids:
            logger.warning("No valid CoinGecko IDs found for provided symbols")
            return {}

        logger.info(f"Fetching bulk metadata for {len(coin_ids)} coins from CoinGecko")

        # Process in batches
        all_metadata = {}
        for i in range(0, len(coin_ids), batch_size):
            batch_ids = coin_ids[i : i + batch_size]
            batch_metadata = await self._fetch_bulk_batch(batch_ids)
            all_metadata.update(batch_metadata)

            # Rate limiting delay between batches
            if i + batch_size < len(coin_ids):
                await asyncio.sleep(self.rate_limit_delay)

        # Map back to symbols
        symbol_metadata = {}
        for symbol in valid_symbols:
            coin_id = symbol_to_id[symbol.upper()]
            if coin_id in all_metadata:
                symbol_metadata[symbol.upper()] = all_metadata[coin_id]

        logger.info(f"Retrieved bulk metadata for {len(symbol_metadata)} coins")
        return symbol_metadata

    async def _fetch_bulk_batch(self, coin_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch metadata for a batch of coins using markets endpoint"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                params = {
                    "vs_currency": "usd",
                    "ids": ",".join(coin_ids),
                    "order": "market_cap_desc",
                    "per_page": len(coin_ids),
                    "page": 1,
                    "sparkline": False,
                }

                url = f"{self.base_url}/coins/markets"
                response = await client.get(url, params=params)
                response.raise_for_status()

                coins_data = response.json()

                # Process response - basic metadata only (no categories)
                metadata = {}
                for coin in coins_data:
                    coin_id = coin.get("id")
                    if coin_id:
                        metadata[coin_id] = {
                            "name": coin.get("name"),
                            "symbol": coin.get("symbol", "").upper(),
                            "circulating_supply": coin.get("circulating_supply"),
                            "total_supply": coin.get("total_supply"),
                            "max_supply": coin.get("max_supply"),
                            "market_cap_rank": coin.get("market_cap_rank"),
                            "coingecko_id": coin_id,
                            "categories": [],  # Empty for bulk endpoint
                        }

                return metadata

            except Exception as e:
                logger.error(f"Error fetching CoinGecko bulk batch data: {e}")
                return {}

    # ==================== DATABASE UPDATE METHODS ====================

    def update_coin_with_metadata(self, symbol: str, metadata: Dict[str, Any]) -> bool:
        """Update a single coin with metadata"""
        try:
            coin = self.coin_service.get_coin(symbol)
            if not coin:
                logger.warning(f"Coin {symbol} not found in database")
                return False

            # Update with metadata
            coin.name = metadata.get("name") or coin.name
            coin.circulating_supply = metadata.get("circulating_supply")
            coin.total_supply = metadata.get("total_supply")
            coin.max_supply = metadata.get("max_supply")
            coin.market_cap_rank = metadata.get("market_cap_rank")
            coin.categories = metadata.get("categories", [])

            # Recalculate market cap with our price and CoinGecko supply
            if coin.price_usd and coin.circulating_supply:
                coin.market_cap = float(coin.price_usd) * float(coin.circulating_supply)

            # Mark as metadata complete
            coin.last_updated = datetime.now(UTC)

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error updating coin {symbol} with metadata: {e}")
            self.db.rollback()
            return False

    # ==================== MAIN PUBLIC METHODS ====================

    async def enrich_new_coins_only(self) -> int:
        """Check for coins missing metadata and enrich them (fast)"""
        # Find coins without complete metadata
        coins_needing_metadata = (
            self.db.query(Coin).filter((Coin.name.is_(None)) | (Coin.circulating_supply.is_(None))).all()
        )

        if not coins_needing_metadata:
            logger.info("No new coins need metadata enrichment")
            return 0

        symbols = [coin.symbol for coin in coins_needing_metadata]
        logger.info(f"Enriching {len(symbols)} new coins with metadata")

        # Get bulk metadata (fast)
        metadata_dict = await self.fetch_complete_metadata_bulk(symbols)

        # Update coins
        updated_count = 0
        for symbol, metadata in metadata_dict.items():
            if self.update_coin_with_metadata(symbol, metadata):
                updated_count += 1

        logger.info(f"Successfully enriched {updated_count} new coins")
        return updated_count

    async def fetch_all_metadata(self, include_categories: bool = True) -> int:
        """Fetch complete metadata for ALL coins (admin endpoint - slow)"""
        # Get all coins from database
        all_coins = self.db.query(Coin).all()
        symbols = [coin.symbol for coin in all_coins]

        if not symbols:
            logger.info("No coins in database to enrich")
            return 0

        logger.info(f"Starting complete metadata fetch for {len(symbols)} coins")

        if include_categories:
            # Individual API calls for complete data including categories (slow)
            updated_count = 0
            for symbol in symbols:
                try:
                    metadata = await self.fetch_complete_metadata_for_coin(symbol)
                    if metadata and self.update_coin_with_metadata(symbol, metadata):
                        updated_count += 1

                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)

                    # Progress logging
                    if updated_count % 10 == 0:
                        logger.info(f"Processed {updated_count}/{len(symbols)} coins")

                except Exception as e:
                    logger.warning(f"Error processing {symbol}: {e}")
                    continue
        else:
            # Bulk API calls for basic data only (fast)
            metadata_dict = await self.fetch_complete_metadata_bulk(symbols)
            updated_count = 0
            for symbol, metadata in metadata_dict.items():
                if self.update_coin_with_metadata(symbol, metadata):
                    updated_count += 1

        logger.info(f"Completed metadata fetch: {updated_count} coins updated")
        return updated_count

    def get_metadata_stats(self) -> Dict[str, int]:
        """Get statistics about metadata completeness"""
        total_coins = self.db.query(Coin).count()
        coins_with_names = self.db.query(Coin).filter(Coin.name.isnot(None)).count()
        coins_with_categories = self.db.query(Coin).filter(Coin.categories.isnot(None)).count()
        coins_with_supply = self.db.query(Coin).filter(Coin.circulating_supply.isnot(None)).count()

        return {
            "total_coins": total_coins,
            "coins_with_names": coins_with_names,
            "coins_with_categories": coins_with_categories,
            "coins_with_supply": coins_with_supply,
            "names_percentage": round((coins_with_names / total_coins * 100), 1) if total_coins else 0,
            "categories_percentage": round((coins_with_categories / total_coins * 100), 1) if total_coins else 0,
            "supply_percentage": round((coins_with_supply / total_coins * 100), 1) if total_coins else 0,
        }
