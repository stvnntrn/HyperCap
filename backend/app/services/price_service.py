import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import Coin, ExchangePair, PriceHistoryRaw
from app.services import CoinService

logger = logging.getLogger(__name__)


class PriceService:
    """
    Service for aggregating exchange data and calculating average prices
    """

    def __init__(self, db: Session):
        self.db = db
        self.coin_service = CoinService(db)

    # ==================== PRICE AGGREGATION ====================

    def aggregate_exchange_data(self, exchange_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Aggregate price data from multiple exchanges into average prices
        """
        # Group all data by symbol
        symbol_data = {}

        for exchange, pairs_data in exchange_data.items():
            for pair_data in pairs_data:
                symbol = pair_data["symbol"]
                price_usd = pair_data.get("price_usd")

                # Skip pairs without USD price
                if not price_usd or price_usd <= 0:
                    continue

                if symbol not in symbol_data:
                    symbol_data[symbol] = {
                        "symbol": symbol,
                        "exchanges": [],
                        "prices": [],
                        "volumes": [],
                        "price_changes": [],
                        "highs": [],
                        "lows": [],
                        "timestamp": datetime.now(UTC),
                    }

                # Add exchange data
                symbol_data[symbol]["exchanges"].append(exchange)
                symbol_data[symbol]["prices"].append(float(price_usd))
                symbol_data[symbol]["volumes"].append(float(pair_data.get("volume_24h_usd", 0)))
                symbol_data[symbol]["price_changes"].append(float(pair_data.get("price_change_24h", 0)))
                symbol_data[symbol]["highs"].append(float(pair_data.get("price_24h_high", price_usd)))
                symbol_data[symbol]["lows"].append(float(pair_data.get("price_24h_low", price_usd)))

        # Calculate averages for each symbol
        aggregated_coins = []
        for symbol, data in symbol_data.items():
            try:
                aggregated_coin = self._calculate_averages(data)
                if aggregated_coin:
                    aggregated_coins.append(aggregated_coin)
            except Exception as e:
                logger.warning(f"Error aggregating data for {symbol}: {e}")
                continue

        logger.info(f"Aggregated data for {len(aggregated_coins)} coins from exchanges")
        return aggregated_coins

    def _calculate_averages(self, symbol_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate average price and other metrics for a symbol"""
        prices = symbol_data["prices"]
        volumes = symbol_data["volumes"]
        price_changes = symbol_data["price_changes"]
        highs = symbol_data["highs"]
        lows = symbol_data["lows"]

        if not prices:
            return None

        # Calculate volume-weighted average price (VWAP) if possible
        total_volume = sum(volumes)
        if total_volume > 0:
            # Volume-weighted average
            weighted_price = sum(p * v for p, v in zip(prices, volumes)) / total_volume
        else:
            # Simple average if no volume data
            weighted_price = sum(prices) / len(prices)

        # Calculate other averages
        avg_price_change = sum(price_changes) / len(price_changes) if price_changes else 0
        max_high = max(highs) if highs else weighted_price
        min_low = min(lows) if lows else weighted_price
        total_volume_24h = sum(volumes)

        return {
            "symbol": symbol_data["symbol"],
            "price_usd": round(weighted_price, 8),
            "price_24h_high": round(max_high, 8),
            "price_24h_low": round(min_low, 8),
            "price_change_24h": round(avg_price_change, 4),
            "volume_24h_usd": round(total_volume_24h, 2),
            "exchange_count": len(symbol_data["exchanges"]),
            "timestamp": symbol_data["timestamp"],
        }

    # ==================== HISTORICAL PRICE MANAGEMENT ====================

    def store_price_history(self, exchange_data: Dict[str, List[Dict[str, Any]]]) -> int:
        """Store individual exchange prices and calculated averages in RAW price history"""
        stored_count = 0
        current_time = datetime.now(UTC)

        # Store individual exchange prices in RAW table
        for exchange, pairs_data in exchange_data.items():
            for pair_data in pairs_data:
                symbol = pair_data["symbol"]
                price_usd = pair_data.get("price_usd")
                volume_usd = pair_data.get("volume_24h_usd")

                if price_usd and price_usd > 0:
                    try:
                        # Store to PriceHistoryRaw
                        price_history = PriceHistoryRaw(
                            symbol=symbol,
                            exchange=exchange,
                            price_usd=Decimal(str(price_usd)),
                            volume_24h_usd=Decimal(str(volume_usd)) if volume_usd else None,
                            timestamp=current_time,
                        )
                        self.db.add(price_history)
                        stored_count += 1
                    except Exception as e:
                        logger.warning(f"Error storing raw price history for {symbol} on {exchange}: {e}")

        # Store aggregated averages in RAW table with exchange="average"
        aggregated_data = self.aggregate_exchange_data(exchange_data)
        for coin_data in aggregated_data:
            try:
                # Store average to PriceHistoryRaw
                avg_price_history = PriceHistoryRaw(
                    symbol=coin_data["symbol"],
                    exchange="average",  # Special exchange name for averages
                    price_usd=Decimal(str(coin_data["price_usd"])),
                    volume_24h_usd=Decimal(str(coin_data["volume_24h_usd"])),
                    timestamp=current_time,
                )
                self.db.add(avg_price_history)
                stored_count += 1
            except Exception as e:
                logger.warning(f"Error storing average price history for {coin_data['symbol']}: {e}")

        self.db.commit()
        logger.info(f"Stored {stored_count} RAW price history records")
        return stored_count

    def store_exchange_pairs(self, exchange_data: Dict[str, List[Dict[str, Any]]]) -> int:
        """Update exchange pairs table with current trading pairs"""
        updated_count = 0
        current_time = datetime.now(UTC)

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
                        .filter(and_(ExchangePair.exchange == exchange, ExchangePair.pair == pair))
                        .first()
                    )

                    if existing_pair:
                        # Update existing
                        existing_pair.symbol = symbol
                        existing_pair.quote_currency = quote_currency
                        existing_pair.is_active = True
                        existing_pair.last_seen = current_time
                    else:
                        # Create new
                        new_pair = ExchangePair(
                            symbol=symbol,
                            exchange=exchange,
                            pair=pair,
                            quote_currency=quote_currency,
                            is_active=True,
                            last_seen=current_time,
                        )
                        self.db.add(new_pair)

                    updated_count += 1

                except Exception as e:
                    logger.warning(f"Error updating exchange pair {pair_data}: {e}")
                    continue

        self.db.commit()
        logger.info(f"Updated {updated_count} exchange pairs")
        return updated_count

    # ==================== PRICE CHANGE CALCULATIONS ====================

    def calculate_historical_price_changes(self, symbol: str) -> Dict[str, Optional[float]]:
        """Calculate price changes based on historical data"""
        current_coin = self.coin_service.get_coin(symbol)
        if not current_coin or not current_coin.price_usd:
            return {}

        current_price = float(current_coin.price_usd)
        now = datetime.now(UTC)

        time_periods = {
            "1h": now - timedelta(hours=1),
            "24h": now - timedelta(days=1),
            "7d": now - timedelta(days=7),
            "30d": now - timedelta(days=30),
        }

        price_changes = {}

        for period, time_threshold in time_periods.items():
            try:
                # Use PriceHistoryRaw
                historical_price = (
                    self.db.query(PriceHistoryRaw)
                    .filter(
                        and_(
                            PriceHistoryRaw.symbol == symbol.upper(),
                            PriceHistoryRaw.exchange == "average",
                            PriceHistoryRaw.timestamp >= time_threshold,
                        )
                    )
                    .order_by(PriceHistoryRaw.timestamp.asc())
                    .first()
                )

                if historical_price and historical_price.price_usd:
                    old_price = float(historical_price.price_usd)
                    if old_price > 0:
                        change_percent = ((current_price - old_price) / old_price) * 100
                        price_changes[f"price_change_{period}"] = round(change_percent, 4)
                    else:
                        price_changes[f"price_change_{period}"] = None
                else:
                    price_changes[f"price_change_{period}"] = None

            except Exception as e:
                logger.warning(f"Error calculating {period} price change for {symbol}: {e}")
                price_changes[f"price_change_{period}"] = None

        return price_changes

    def update_all_price_changes(self) -> int:
        """Update price changes for all coins with recent data"""
        # Get all coins updated in the last hour
        recent_threshold = datetime.now(UTC) - timedelta(hours=1)
        recent_coins = self.db.query(Coin).filter(Coin.last_updated >= recent_threshold).all()

        updated_count = 0
        for coin in recent_coins:
            try:
                price_changes = self.calculate_historical_price_changes(coin.symbol)

                # Update coin with calculated changes
                for field, value in price_changes.items():
                    if hasattr(coin, field):
                        setattr(coin, field, value)

                updated_count += 1

            except Exception as e:
                logger.warning(f"Error updating price changes for {coin.symbol}: {e}")
                continue

        self.db.commit()
        logger.info(f"Updated price changes for {updated_count} coins")
        return updated_count

    # ==================== DATA CLEANUP ====================

    def cleanup_old_price_history(self, days_to_keep: int = 1) -> int:
        """Remove old RAW price history data (keep only 1 day by default)"""
        cutoff_date = datetime.now(UTC) - timedelta(days=days_to_keep)

        # Clean PriceHistoryRaw
        deleted_count = self.db.query(PriceHistoryRaw).filter(PriceHistoryRaw.timestamp < cutoff_date).delete()

        self.db.commit()
        logger.info(f"Cleaned up {deleted_count} old RAW price history records")
        return deleted_count

    # ==================== MAIN PROCESSING FUNCTION ====================

    async def update_prices_and_rankings(self, exchange_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """
        Enhanced main function to process all exchange data including rankings:
        1. Store price history
        2. Update exchange pairs
        3. Aggregate and store coin data
        4. Calculate price changes
        5. Update market cap rankings
        """
        results = {}

        try:
            # 1. Store individual and average price history
            results["price_history"] = self.store_price_history(exchange_data)

            # 2. Update exchange pairs
            results["exchange_pairs"] = self.store_exchange_pairs(exchange_data)

            # 3. Aggregate and store/update main coin data
            aggregated_coins = self.aggregate_exchange_data(exchange_data)
            results["coins_updated"] = self.coin_service.bulk_upsert_coins(aggregated_coins)

            # 4. Update price changes based on historical data
            results["price_changes_updated"] = self.update_all_price_changes()

            # 5. Update market cap rankings (NEW)
            results["rankings_updated"] = await self.update_market_cap_rankings()

            logger.info(f"Successfully processed exchange data with rankings: {results}")
            return results

        except Exception as e:
            logger.error(f"Error processing exchange data: {e}")
            self.db.rollback()
            raise

    async def update_market_cap_rankings(self) -> int:
        """
        Recalculate market cap rankings for all coins
        Called after price updates to keep rankings current
        """
        try:
            from sqlalchemy import desc

            from app.models.coin import Coin

            # Get all coins with market cap, ordered by market cap descending
            coins_with_market_cap = (
                self.db.query(Coin)
                .filter(Coin.market_cap.isnot(None))
                .filter(Coin.market_cap > 0)  # Exclude zero/negative market caps
                .order_by(desc(Coin.market_cap))
                .all()
            )

            # Update ranks
            updated_count = 0
            for rank, coin in enumerate(coins_with_market_cap, start=1):
                if coin.market_cap_rank != rank:
                    coin.market_cap_rank = rank
                    updated_count += 1

            # Coins without market cap get null rank
            coins_without_market_cap = (
                self.db.query(Coin).filter((Coin.market_cap.is_(None)) | (Coin.market_cap <= 0)).all()
            )

            for coin in coins_without_market_cap:
                if coin.market_cap_rank is not None:
                    coin.market_cap_rank = None
                    updated_count += 1

            self.db.commit()

            if updated_count > 0:
                logger.info(
                    f"Updated market cap rankings: {updated_count} changes, top coin: {coins_with_market_cap[0].symbol if coins_with_market_cap else 'None'}"
                )
            else:
                logger.debug("No ranking changes needed")

            return updated_count

        except Exception as e:
            logger.error(f"Error updating market cap rankings: {e}")
            self.db.rollback()
            return 0

    def process_exchange_data(self, exchange_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """
        Original main function to process all exchange data (without rankings):
        1. Store price history
        2. Update exchange pairs
        3. Aggregate and store coin data
        4. Calculate price changes

        Note: This method kept for backward compatibility
        Use update_prices_and_rankings() for production
        """
        results = {}

        try:
            # 1. Store individual and average price history
            results["price_history"] = self.store_price_history(exchange_data)

            # 2. Update exchange pairs
            results["exchange_pairs"] = self.store_exchange_pairs(exchange_data)

            # 3. Aggregate and store/update main coin data
            aggregated_coins = self.aggregate_exchange_data(exchange_data)
            results["coins_updated"] = self.coin_service.bulk_upsert_coins(aggregated_coins)

            # 4. Update price changes based on historical data
            results["price_changes_updated"] = self.update_all_price_changes()

            logger.info(f"Successfully processed exchange data: {results}")
            return results

        except Exception as e:
            logger.error(f"Error processing exchange data: {e}")
            self.db.rollback()
            raise
