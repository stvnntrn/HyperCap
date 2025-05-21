import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..crud.coin import bulk_upsert_coins
from ..models.binance_coin import BinanceCoinData
from ..models.kraken_coin import KrakenCoinData
from ..models.mexc_coin import MexCCoinData

logger = logging.getLogger(__name__)


def store_coin_data(db: Session, coin_data: List[Dict[str, Any]], table: str = "binance") -> int:
    """Store coin data into the specified table."""
    try:
        if not coin_data:
            logger.info("No coin data to store")
            return 0
        bulk_upsert_coins(db, coin_data, table=table)
        logger.info(f"Stored {len(coin_data)} {table} pairs successfully")
        return len(coin_data)
    except Exception as e:
        logger.error(f"Error storing {table} coin data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")


def compute_average_coin_data(db: Session, batch_size: int = 100) -> int:
    """Compute average coin data from Binance, Kraken, and MEXC, and store in average_coin_data."""
    try:
        # Map non-standard coin_abbr (consistent with routes.py)
        coin_abbr_mapping = {
            "XBT": "BTC",  # Kraken's Bitcoin
            "BCHABC": "BCH",  # Example for Bitcoin Cash
            # Add more mappings as needed
        }

        # Get unique coin_abbrs from all exchanges
        binance_abbrs = (
            db.query(BinanceCoinData.coin_abbr).filter(BinanceCoinData.quote_currency == "USDT").distinct().all()
        )
        kraken_abbrs = (
            db.query(KrakenCoinData.coin_abbr)
            .filter(KrakenCoinData.quote_currency.in_(["USD", "ZUSD"]))
            .distinct()
            .all()
        )
        mexc_abbrs = db.query(MexCCoinData.coin_abbr).filter(MexCCoinData.quote_currency == "USDT").distinct().all()

        # Normalize and combine unique coin_abbrs
        all_abbrs = set()
        for abbr in binance_abbrs + mexc_abbrs:
            all_abbrs.add(abbr[0])
        for abbr in kraken_abbrs:
            all_abbrs.add(coin_abbr_mapping.get(abbr[0], abbr[0]))

        # Filter for fresh data (last 5 minutes)
        freshness_threshold = datetime.now(UTC) - timedelta(minutes=5)
        average_coin_data = []
        total_processed = 0

        # Process in batches
        for i in range(0, len(all_abbrs), batch_size):
            batch_abbrs = list(all_abbrs)[i : i + batch_size]
            for coin_abbr in batch_abbrs:
                # Fetch coins for this coin_abbr
                binance_coins = (
                    db.query(BinanceCoinData)
                    .filter(
                        BinanceCoinData.coin_abbr == coin_abbr,
                        BinanceCoinData.quote_currency == "USDT",
                        BinanceCoinData.last_updated >= freshness_threshold,
                    )
                    .all()
                )
                kraken_coins = (
                    db.query(KrakenCoinData)
                    .filter(
                        KrakenCoinData.coin_abbr.in_([coin_abbr, "XBT" if coin_abbr == "BTC" else coin_abbr]),
                        KrakenCoinData.quote_currency.in_(["USD", "ZUSD"]),
                        KrakenCoinData.last_updated >= freshness_threshold,
                    )
                    .all()
                )
                mexc_coins = (
                    db.query(MexCCoinData)
                    .filter(
                        MexCCoinData.coin_abbr == coin_abbr,
                        MexCCoinData.quote_currency == "USDT",
                        MexCCoinData.last_updated >= freshness_threshold,
                    )
                    .all()
                )

                # Combine coin data
                coin_data_list = []
                for coin in binance_coins:
                    coin_data_list.append(
                        {
                            "pair": coin.pair,
                            "coin_name": coin.coin_name,
                            "coin_abbr": coin_abbr,
                            "quote_currency": "USDT",
                            "price_usdt": coin.price_usdt,
                            "price_change_percent": coin.price_change_percent,
                            "volume_24h": coin.volume_24h,
                            "quote_volume_24h": coin.quote_volume_24h,
                            "circulating_supply": coin.circulating_supply,
                            "total_supply": coin.total_supply,
                            "max_supply": coin.max_supply,
                        }
                    )
                for coin in kraken_coins:
                    normalized_abbr = coin_abbr_mapping.get(coin.coin_abbr, coin.coin_abbr)
                    if normalized_abbr == coin_abbr:
                        coin_data_list.append(
                            {
                                "pair": coin.pair,
                                "coin_name": coin.coin_name,
                                "coin_abbr": normalized_abbr,
                                "quote_currency": "USDT",
                                "price_usdt": coin.price_usdt,
                                "price_change_percent": coin.price_change_percent,
                                "volume_24h": coin.volume_24h,
                                "quote_volume_24h": coin.quote_volume_24h,
                                "circulating_supply": coin.circulating_supply,
                                "total_supply": coin.total_supply,
                                "max_supply": coin.max_supply,
                            }
                        )
                for coin in mexc_coins:
                    coin_data_list.append(
                        {
                            "pair": coin.pair,
                            "coin_name": coin.coin_name,
                            "coin_abbr": coin_abbr,
                            "quote_currency": "USDT",
                            "price_usdt": coin.price_usdt,
                            "price_change_percent": coin.price_change_percent,
                            "volume_24h": coin.volume_24h,
                            "quote_volume_24h": coin.quote_volume_24h,
                            "circulating_supply": coin.circulating_supply,
                            "total_supply": coin.total_supply,
                            "max_supply": coin.max_supply,
                        }
                    )

                if not coin_data_list:
                    logger.debug(f"No fresh data for {coin_abbr}")
                    continue

                # Compute averages
                price_usdt_sum = 0
                price_change_percent_sum = 0
                volume_24h_sum = 0
                quote_volume_24h_sum = 0
                count = 0
                coin_name = None
                circulating_supply = None
                total_supply = None
                max_supply = None

                for coin in coin_data_list:
                    if coin["price_usdt"] is not None:
                        price_usdt_sum += coin["price_usdt"]
                        price_change_percent_sum += coin["price_change_percent"] or 0
                        count += 1
                    volume_24h_sum += coin["volume_24h"] or 0
                    quote_volume_24h_sum += coin["quote_volume_24h"] or 0
                    if coin["coin_name"] and not coin_name:
                        coin_name = coin["coin_name"]
                    if coin["circulating_supply"] is not None and circulating_supply is None:
                        circulating_supply = coin["circulating_supply"]
                    if coin["total_supply"] is not None and total_supply is None:
                        total_supply = coin["total_supply"]
                    if coin["max_supply"] is not None and max_supply is None:
                        max_supply = coin["max_supply"]

                if count == 0:
                    logger.warning(f"No valid price data for {coin_abbr}")
                    continue

                # Compute averages
                avg_price_usdt = price_usdt_sum / count
                avg_price_change_percent = price_change_percent_sum / count
                market_cap = avg_price_usdt * circulating_supply if circulating_supply else None

                average_coin_data.append(
                    {
                        "pair": f"{coin_abbr}/USDT",
                        "coin_name": coin_name,
                        "coin_abbr": coin_abbr,
                        "quote_currency": "USDT",
                        "price_usdt": avg_price_usdt,
                        "price_change_percent": avg_price_change_percent,
                        "volume_24h": volume_24h_sum,
                        "quote_volume_24h": quote_volume_24h_sum,
                        "market_cap": market_cap,
                        "circulating_supply": circulating_supply,
                        "total_supply": total_supply,
                        "max_supply": max_supply,
                        "exchange_count": count,
                        "last_updated": datetime.now(UTC),
                    }
                )

            # Store batch
            if average_coin_data:
                bulk_upsert_coins(db, average_coin_data, table="average")
                total_processed += len(average_coin_data)
                logger.info(f"Stored {len(average_coin_data)} average coin records for batch {i // batch_size + 1}")
                average_coin_data = []  # Clear for next batch

        logger.info(f"Completed averaging, stored {total_processed} average coin records")
        return total_processed
    except Exception as e:
        logger.error(f"Error computing average coin data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error computing averages: {str(e)}")
