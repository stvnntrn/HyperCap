import logging
from datetime import UTC, datetime, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from ..models.binance_coin import BinanceCoinData
from ..models.kraken_coin import KrakenCoinData
from ..models.mexc_coin import MexCCoinData
from ..services.storage_service import upsert_coin_data
from ..utils.normalize import normalize_coin_abbr

logger = logging.getLogger(__name__)


def compute_averages(db: Session, coin_data: Dict[str, List[Dict]]) -> List[Dict]:
    """Compute average prices and volumes across exchanges."""
    freshness_threshold = datetime.now(UTC) - timedelta(minutes=5)
    coin_data_avg = []

    # Aggregate all coin abbreviations
    all_abbrs = set()
    for exchange, data in coin_data.items():
        for coin in data:
            normalized_abbr = normalize_coin_abbr(coin["coin_abbr"], exchange)
            all_abbrs.add(normalized_abbr)

    for coin_abbr in all_abbrs:
        coins = []
        for exchange, data in coin_data.items():
            model = {"binance": BinanceCoinData, "kraken": KrakenCoinData, "mexc": MexCCoinData}[exchange]
            query = db.query(model).filter(
                model.coin_abbr.in_([coin_abbr, denormalize_coin_abbr(coin_abbr, exchange)]),
                model.quote_currency.in_(["USDT", "USD", "ZUSD"]),
                model.last_updated >= freshness_threshold,
            )
            coins.extend(query.all())

        if not coins:
            logger.debug(f"No fresh data for {coin_abbr}")
            continue

        price_usdt_sum = 0
        volume_24h_sum = 0
        quote_volume_24h_sum = 0
        count = 0
        circulating_supply = total_supply = max_supply = None
        coin_name = None

        for coin in coins:
            if coin.price_usdt:
                price_usdt_sum += coin.price_usdt
                count += 1
            volume_24h_sum += coin.volume_24h or 0
            quote_volume_24h_sum += coin.quote_volume_24h or 0
            if coin_name is None and hasattr(coin, "coin_name") and coin.coin_name:
                coin_name = coin.coin_name
            if circulating_supply is None and hasattr(coin, "circulating_supply"):
                circulating_supply = coin.circulating_supply
            if total_supply is None and hasattr(coin, "total_supply"):
                total_supply = coin.total_supply
            if max_supply is None and hasattr(coin, "max_supply"):
                max_supply = coin.max_supply

        if count == 0:
            logger.warning(f"No valid price data for {coin_abbr}")
            continue

        avg_price_usdt = price_usdt_sum / count
        market_cap = avg_price_usdt * circulating_supply if circulating_supply else None

        # Calculate price changes
        historical_prices = (
            db.query(HistoricalCoinData)
            .filter(HistoricalCoinData.coin_id == coin_abbr.lower())
            .order_by(HistoricalCoinData.timestamp.desc())
            .all()
        )

        time_thresholds = {
            "change_1h": datetime.now(UTC) - timedelta(hours=1),
            "change_24h": datetime.now(UTC) - timedelta(hours=24),
            "change_7d": datetime.now(UTC) - timedelta(days=7),
        }
        changes = {key: None for key in time_thresholds}
        for price in historical_prices:
            for key, threshold in time_thresholds.items():
                if changes[key] is None and price.timestamp >= threshold:
                    changes[key] = (
                        ((avg_price_usdt - price.price_usdt) / price.price_usdt * 100) if price.price_usdt else None
                    )

        coin_data_avg.append(
            {
                "pair": f"{coin_abbr}/USDT",
                "coin_name": coin_name,
                "coin_abbr": coin_abbr,
                "quote_currency": "USDT",
                "price_usdt": avg_price_usdt,
                "change_1h": changes["change_1h"],
                "change_24h": changes["change_24h"],
                "change_7d": changes["change_7d"],
                "volume_24h": volume_24h_sum,
                "quote_volume_24h": quote_volume_24h_sum,
                "market_cap": market_cap,
                "circulating_supply": circulating_supply,
                "total_supply": total_supply,
                "max_supply": max_supply,
                "exchange_count": count,
                "categories": [],  # Populated by coingecko_service
                "last_updated": datetime.now(UTC),
            }
        )

    upsert_coin_data(db, coin_data_avg, table="coin")
    logger.info(f"Computed and stored averages for {len(coin_data_avg)} coins")
    return coin_data_avg
