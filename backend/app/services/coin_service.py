from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import Session

from app.models import Coin, ExchangePair, PriceHistoryRaw
from app.schemas.coin import CoinCreate, CoinUpdate, ExchangePairInfo


class CoinService:
    """
    Service handling all coin-related operations
    Combines CRUD operations with business logic
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== BASIC CRUD OPERATIONS ====================

    def get_coin(self, symbol: str) -> Optional[Coin]:
        """Get a single coin by symbol"""
        return self.db.query(Coin).filter(Coin.symbol == symbol.upper()).first()

    def get_coins(
        self, skip: int = 0, limit: int = 100, sort_by: str = "market_cap_rank", sort_desc: bool = False
    ) -> List[Coin]:
        """Get multiple coins with pagination and sorting"""
        query = self.db.query(Coin)

        # Apply sorting
        sort_column = getattr(Coin, sort_by, Coin.market_cap_rank)
        if sort_desc:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        return query.offset(skip).limit(limit).all()

    def get_total_coins(self) -> int:
        """Get total number of coins"""
        return self.db.query(Coin).count()

    def create_coin(self, coin_data: CoinCreate) -> Coin:
        """Create a new coin"""
        db_coin = Coin(**coin_data.dict())
        self.db.add(db_coin)
        self.db.commit()
        self.db.refresh(db_coin)
        return db_coin

    def update_coin(self, symbol: str, coin_data: CoinUpdate) -> Optional[Coin]:
        """Update an existing coin"""
        db_coin = self.get_coin(symbol)
        if db_coin:
            for field, value in coin_data.dict(exclude_unset=True).items():
                setattr(db_coin, field, value)
            db_coin.last_updated = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(db_coin)
        return db_coin

    def upsert_coin(self, coin_data: Dict[str, Any]) -> Coin:
        """Create or update a coin"""
        symbol = coin_data.get("symbol", "").upper()
        existing_coin = self.get_coin(symbol)

        if existing_coin:
            # Update existing
            for field, value in coin_data.items():
                if hasattr(existing_coin, field) and value is not None:
                    setattr(existing_coin, field, value)
            existing_coin.last_updated = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(existing_coin)
            return existing_coin
        else:
            # Create new
            coin_data["symbol"] = symbol
            coin_data["last_updated"] = datetime.now(UTC)
            new_coin = Coin(**coin_data)
            self.db.add(new_coin)
            self.db.commit()
            self.db.refresh(new_coin)
            return new_coin

    # ==================== BUSINESS LOGIC OPERATIONS ====================

    def get_top_coins_by_market_cap(self, limit: int = 100) -> List[Coin]:
        """Get top coins by market cap"""
        return (
            self.db.query(Coin)
            .filter(Coin.market_cap.isnot(None))
            .order_by(asc(Coin.market_cap_rank))
            .limit(limit)
            .all()
        )

    def search_coins(self, query: str, limit: int = 10) -> List[Coin]:
        """Search coins by name or symbol"""
        search_term = f"%{query.upper()}%"
        return (
            self.db.query(Coin)
            .filter(or_(Coin.symbol.ilike(search_term), Coin.name.ilike(search_term)))
            .order_by(asc(Coin.market_cap_rank))
            .limit(limit)
            .all()
        )

    def get_trending_coins(self, limit: int = 10) -> List[Coin]:
        """Get coins with highest 24h volume"""
        return (
            self.db.query(Coin)
            .filter(Coin.volume_24h_usd.isnot(None))
            .order_by(desc(Coin.volume_24h_usd))
            .limit(limit)
            .all()
        )

    def get_biggest_gainers(self, limit: int = 10) -> List[Coin]:
        """Get coins with highest 24h price change"""
        return (
            self.db.query(Coin)
            .filter(Coin.price_change_24h.isnot(None))
            .order_by(desc(Coin.price_change_24h))
            .limit(limit)
            .all()
        )

    def get_biggest_losers(self, limit: int = 10) -> List[Coin]:
        """Get coins with lowest 24h price change"""
        return (
            self.db.query(Coin)
            .filter(Coin.price_change_24h.isnot(None))
            .order_by(asc(Coin.price_change_24h))
            .limit(limit)
            .all()
        )

    def get_coin_with_exchange_pairs(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get coin with its available exchange pairs"""
        coin = self.get_coin(symbol)
        if not coin:
            return None

        # Get exchange pairs
        exchange_pairs = (
            self.db.query(ExchangePair)
            .filter(and_(ExchangePair.symbol == symbol.upper(), ExchangePair.is_active))
            .all()
        )

        # Convert to response format
        pairs_info = [
            ExchangePairInfo(
                exchange=pair.exchange, pair=pair.pair, quote_currency=pair.quote_currency, is_active=pair.is_active
            )
            for pair in exchange_pairs
        ]

        # Create response
        coin_dict = {
            "symbol": coin.symbol,
            "name": coin.name,
            "price_usd": coin.price_usd,
            "price_24h_high": coin.price_24h_high,
            "price_24h_low": coin.price_24h_low,
            "price_change_1h": coin.price_change_1h,
            "price_change_24h": coin.price_change_24h,
            "price_change_7d": coin.price_change_7d,
            "volume_24h_usd": coin.volume_24h_usd,
            "volume_24h_base": coin.volume_24h_base,
            "market_cap": coin.market_cap,
            "circulating_supply": coin.circulating_supply,
            "total_supply": coin.total_supply,
            "max_supply": coin.max_supply,
            "categories": coin.categories,
            "market_cap_rank": coin.market_cap_rank,
            "exchange_count": coin.exchange_count,
            "last_updated": coin.last_updated,
            "exchange_pairs": pairs_info,
        }

        return coin_dict

    def calculate_price_changes(self, symbol: str) -> Dict[str, Optional[float]]:
        """Calculate price changes for a coin based on historical data"""
        current_coin = self.get_coin(symbol)
        if not current_coin or not current_coin.price_usd:
            return {}

        now = datetime.now(UTC)
        time_ranges = {
            "1h": now - timedelta(hours=1),
            "24h": now - timedelta(days=1),
            "7d": now - timedelta(days=7),
            "30d": now - timedelta(days=30),
        }

        changes = {}
        current_price = float(current_coin.price_usd)

        for period, time_threshold in time_ranges.items():
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
                change_pct = ((current_price - old_price) / old_price) * 100
                changes[f"change_{period}"] = round(change_pct, 2)
            else:
                changes[f"change_{period}"] = None

        return changes

    def bulk_upsert_coins(self, coins_data: List[Dict[str, Any]]) -> int:
        """Bulk insert/update multiple coins efficiently"""
        updated_count = 0

        for coin_data in coins_data:
            try:
                self.upsert_coin(coin_data)
                updated_count += 1
            except Exception as e:
                print(f"Error upserting coin {coin_data.get('symbol', 'UNKNOWN')}: {e}")
                continue

        return updated_count

    def update_market_cap_ranks(self) -> int:
        """Update market cap rankings for all coins"""
        # Get all coins with market cap, ordered by market cap descending
        coins_with_market_cap = (
            self.db.query(Coin).filter(Coin.market_cap.isnot(None)).order_by(desc(Coin.market_cap)).all()
        )

        # Update ranks
        for index, coin in enumerate(coins_with_market_cap, 1):
            coin.market_cap_rank = index

        self.db.commit()
        return len(coins_with_market_cap)
