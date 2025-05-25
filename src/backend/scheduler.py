import asyncio
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from .crud.coin import create_historical_coin
from .database import get_db
from .models.historical_coin_data import HistoricalCoinData
from .services.binance_service import fetch_ticker_data as fetch_binance_ticker_data
from .services.coin_service import compute_coin_data, store_coin_data
from .services.coingecko_service import append_supply_data, fetch_coingecko_coin_list, fetch_coingecko_historical_data
from .services.kraken_service import fetch_kraken_ticker_data
from .services.mexc_service import fetch_mexc_ticker_data

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def fetch_price_data():
    """Fetch price data from exchanges and store in historical_coin_data."""
    db: Session = next(get_db())
    try:
        logger.info(f"Starting price data fetch at {datetime.now(UTC)}")

        # Fetch ticker data
        symbol_to_id = await fetch_coingecko_coin_list()
        binance_data = await fetch_binance_ticker_data(db)
        kraken_data = await fetch_kraken_ticker_data(db)
        mexc_data = await fetch_mexc_ticker_data(db)

        # Store historical data
        for data, exchange in [
            (binance_data, "binance"),
            (kraken_data, "kraken"),
            (mexc_data, "mexc"),
        ]:
            for coin in data:
                if coin.get("price_usdt") and coin.get("coin_abbr"):
                    coin_id = symbol_to_id.get(coin["coin_abbr"], coin["coin_abbr"].lower())
                    historical_entry = {
                        "coin_id": coin_id,
                        "exchange": exchange,
                        "price_usdt": coin["price_usdt"],
                        "timestamp": datetime.now(UTC),
                    }
                    create_historical_coin(db, historical_entry)

        # Store data (preserve existing supply data)
        binance_records = store_coin_data(db, binance_data, table="binance")
        kraken_records = store_coin_data(db, kraken_data, table="kraken")
        mexc_records = store_coin_data(db, mexc_data, table="mexc")

        # Compute and store averages
        avg_records = compute_coin_data(db)

        logger.info(
            f"Price update completed: {binance_records} Binance, {kraken_records} Kraken, "
            f"{mexc_records} MEXC, {avg_records} average records"
        )
    except Exception as e:
        logger.error(f"Error in price data fetch: {str(e)}")
    finally:
        db.close()


async def fetch_supply_data():
    """Fetch supply data from CoinGecko and update market caps."""
    db: Session = next(get_db())
    try:
        logger.info(f"Starting supply data fetch at {datetime.now(UTC)}")

        # Fetch ticker data to get latest coin_abbrs
        binance_data = await fetch_binance_ticker_data(db)
        kraken_data = await fetch_kraken_ticker_data(db)
        mexc_data = await fetch_mexc_ticker_data(db)

        # Append CoinGecko supply data
        updated_binance = await append_supply_data(db, binance_data)
        updated_kraken = await append_supply_data(db, kraken_data)
        updated_mexc = await append_supply_data(db, mexc_data)

        # Store updated data
        binance_records = store_coin_data(db, updated_binance, table="binance")
        kraken_records = store_coin_data(db, updated_kraken, table="kraken")
        mexc_records = store_coin_data(db, updated_mexc, table="mexc")

        # Compute averages with updated supply data
        avg_records = compute_coin_data(db)

        logger.info(
            f"Supply update completed: {binance_records} Binance, {kraken_records} Kraken, "
            f"{mexc_records} MEXC, {avg_records} average records"
        )
    except Exception as e:
        logger.error(f"Error in supply data fetch: {str(e)}")
    finally:
        db.close()


async def fetch_historical_data():
    """Fetch full historical price data from CoinGecko for coins without history."""
    db: Session = next(get_db())
    try:
        logger.info(f"Starting historical data fetch at {datetime.now(UTC)}")
        symbol_to_id = await fetch_coingecko_coin_list()
        for symbol, coin_id in symbol_to_id.items():
            # Check if historical data exists for this coin
            existing_data = (
                db.query(HistoricalCoinData)
                .filter(HistoricalCoinData.coin_id == coin_id, HistoricalCoinData.exchange == "coingecko")
                .first()
            )
            if not existing_data:
                historical_data = await fetch_coingecko_historical_data(db, coin_id, days="max")
                for entry in historical_data:
                    create_historical_coin(db, entry)
                await asyncio.sleep(1.2)  # Respect CoinGecko rate limits
        logger.info("Historical data fetch completed")
    except Exception as e:
        logger.error(f"Error in historical data fetch: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """Start the scheduler for price and supply data updates."""
    scheduler.add_job(
        fetch_price_data,
        "interval",
        seconds=30,  # Fetch prices every 30 seconds
        id="fetch_price_data",
        replace_existing=True,
    )
    scheduler.add_job(
        fetch_supply_data,
        "interval",
        hours=1,  # Fetch supply data every 1 hour
        id="fetch_supply_data",
        replace_existing=True,
    )
    scheduler.add_job(
        fetch_historical_data,
        "interval",
        days=7,  # Run weekly to catch new coins
        id="fetch_historical_data",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started for periodic data updates")
