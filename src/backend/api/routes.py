from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.average_coin import AverageCoinData
from ..models.binance_coin import BinanceCoinData
from ..models.kraken_coin import KrakenCoinData
from ..models.mexc_coin import MexCCoinData
from ..schemas.coin import CoinInDB
from ..services.binance_service import fetch_ticker_data as fetch_binance_ticker_data
from ..services.binance_service import get_crypto_price
from ..services.coin_service import compute_average_coin_data, store_coin_data
from ..services.coingecko_service import append_supply_data
from ..services.kraken_service import fetch_kraken_ticker_data, get_kraken_price
from ..services.mexc_service import fetch_mexc_ticker_data, get_mexc_price

router = APIRouter()


@router.get("/marketcap/")
async def get_marketcap_data(page: Optional[int] = 1, size: Optional[int] = 100, db: Session = Depends(get_db)):
    """List USDT pairs from average_coin_data, sorted by market_cap, with exchange details."""
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Page and size must be positive")
    skip = (page - 1) * size

    # Get coins from average_coin_data
    average_coins = (
        db.query(AverageCoinData)
        .filter(AverageCoinData.quote_currency == "USDT")
        .order_by(AverageCoinData.market_cap.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    total_average = db.query(AverageCoinData).filter(AverageCoinData.quote_currency == "USDT").count()

    # Normalize coin_abbr and fetch exchange details
    coin_abbr_mapping = {"XBT": "BTC", "BCHABC": "BCH"}  # Consistent with coin_service.py  # noqa: F841
    response_data = []
    for coin in average_coins:
        coin_abbr = coin.coin_abbr
        # Fetch exchange-specific data
        binance_coin = (
            db.query(BinanceCoinData)
            .filter(BinanceCoinData.coin_abbr == coin_abbr, BinanceCoinData.quote_currency == "USDT")
            .first()
        )
        kraken_coin = (
            db.query(KrakenCoinData)
            .filter(
                KrakenCoinData.coin_abbr.in_([coin_abbr, "XBT" if coin_abbr == "BTC" else coin_abbr]),
                KrakenCoinData.quote_currency.in_(["USD", "ZUSD"]),
            )
            .first()
        )
        mexc_coin = (
            db.query(MexCCoinData)
            .filter(MexCCoinData.coin_abbr == coin_abbr, MexCCoinData.quote_currency == "USDT")
            .first()
        )

        # Build exchange_details
        exchange_details = {
            "binance": {
                "price_usdt": binance_coin.price_usdt if binance_coin else None,
                "market_cap": binance_coin.market_cap if binance_coin else None,
            },
            "kraken": {
                "price_usdt": kraken_coin.price_usdt if kraken_coin else None,
                "market_cap": kraken_coin.market_cap if kraken_coin else None,
            },
            "mexc": {
                "price_usdt": mexc_coin.price_usdt if mexc_coin else None,
                "market_cap": mexc_coin.market_cap if mexc_coin else None,
            },
        }

        # Create response coin with normalized coin_abbr
        coin_data = CoinInDB.model_validate(coin).model_dump()
        coin_data["exchange_details"] = exchange_details
        response_data.append(coin_data)

    return {
        "status": "success",
        "data": response_data,
        "total": total_average,
    }


@router.get("/coin/{coin_abbr}")
async def get_coin_details(coin_abbr: str, db: Session = Depends(get_db)):
    """Get details for a coin's USDT pair, emphasizing average market_cap."""
    coin_abbr = coin_abbr.upper()
    normalized_abbr = coin_abbr  # Default to input

    # Normalize coin_abbr for consistency
    coin_abbr_mapping = {"XBT": "BTC", "BCHABC": "BCH"}
    reverse_mapping = {v: k for k, v in coin_abbr_mapping.items()}
    query_abbrs = [coin_abbr, reverse_mapping.get(coin_abbr, coin_abbr)]  # e.g., ["BTC", "XBT"]

    # Query exchange data
    binance_coin = (
        db.query(BinanceCoinData)
        .filter(BinanceCoinData.coin_abbr == coin_abbr, BinanceCoinData.quote_currency == "USDT")
        .first()
    )
    kraken_coin = (
        db.query(KrakenCoinData)
        .filter(KrakenCoinData.coin_abbr.in_(query_abbrs), KrakenCoinData.quote_currency.in_(["USD", "ZUSD"]))
        .first()
    )
    mexc_coin = (
        db.query(MexCCoinData)
        .filter(MexCCoinData.coin_abbr == coin_abbr, MexCCoinData.quote_currency == "USDT")
        .first()
    )
    average_coin = (
        db.query(AverageCoinData)
        .filter(AverageCoinData.coin_abbr == coin_abbr, AverageCoinData.quote_currency == "USDT")
        .first()
    )

    # Normalize coin_abbr in response
    if kraken_coin and kraken_coin.coin_abbr in coin_abbr_mapping:
        normalized_abbr = coin_abbr_mapping.get(kraken_coin.coin_abbr, kraken_coin.coin_abbr)

    available_on = []
    if binance_coin:
        available_on.append("Binance")
    if kraken_coin:
        available_on.append("Kraken")
    if mexc_coin:
        available_on.append("MEXC")
    if average_coin:
        available_on.append("Average")
    if not available_on:
        raise HTTPException(status_code=404, detail="Coin not found in USDT pair")

    # Build response with normalized coin_abbr
    response = {
        "status": "success",
        "coin": {
            "binance": (
                CoinInDB.model_validate(binance_coin).model_dump() | {"coin_abbr": normalized_abbr}
                if binance_coin
                else None
            ),
            "kraken": (
                CoinInDB.model_validate(kraken_coin).model_dump() | {"coin_abbr": normalized_abbr}
                if kraken_coin
                else None
            ),
            "mexc": (
                CoinInDB.model_validate(mexc_coin).model_dump() | {"coin_abbr": normalized_abbr} if mexc_coin else None
            ),
            "average": (
                CoinInDB.model_validate(average_coin).model_dump() | {"coin_abbr": normalized_abbr}
                if average_coin
                else None
            ),
        },
        "available_on": available_on,
    }

    return response


@router.get("/fetch-and-store/")
async def fetch_and_store_binance(db: Session = Depends(get_db)):
    """Fetch and store all Binance ticker data."""
    ticker_data = await fetch_binance_ticker_data(db)
    records = store_coin_data(db, ticker_data, table="binance")
    return {"status": "success", "message": "Binance data fetched and stored", "records": records}


@router.get("/fetch-and-store-kraken/")
async def fetch_and_store_kraken(db: Session = Depends(get_db)):
    """Fetch and store all Kraken ticker data."""
    ticker_data = await fetch_kraken_ticker_data(db)
    records = store_coin_data(db, ticker_data, table="kraken")
    return {"status": "success", "message": "Kraken data fetched and stored", "records": records}


@router.get("/fetch-and-store-mexc/")
async def fetch_and_store_mexc(db: Session = Depends(get_db)):
    """Fetch and store all MEXC ticker data."""
    ticker_data = await fetch_mexc_ticker_data(db)
    records = store_coin_data(db, ticker_data, table="mexc")
    return {"status": "success", "message": "MEXC data fetched and stored", "records": records}


@router.get("/update-supply-data/")
async def update_supply_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update supply data for Binance, Kraken, and MEXC from CoinGecko, and compute averages."""
    binance_ticker_data = await fetch_binance_ticker_data(db)
    kraken_ticker_data = await fetch_kraken_ticker_data(db)
    mexc_ticker_data = await fetch_mexc_ticker_data(db)
    updated_binance = await append_supply_data(db, binance_ticker_data)
    updated_kraken = await append_supply_data(db, kraken_ticker_data)
    updated_mexc = await append_supply_data(db, mexc_ticker_data)
    binance_records = store_coin_data(db, updated_binance, table="binance")
    kraken_records = store_coin_data(db, updated_kraken, table="kraken")
    mexc_records = store_coin_data(db, updated_mexc, table="mexc")

    # Run averaging in background
    background_tasks.add_task(compute_average_coin_data, db)

    return {
        "status": "success",
        "message": "Supply data updated from CoinGecko, averaging started in background",
        "records": {
            "binance": binance_records,
            "kraken": kraken_records,
            "mexc": mexc_records,
            "average": "pending",  # Averaging runs asynchronously
        },
    }


@router.get("/compute-averages/")
async def compute_averages(db: Session = Depends(get_db)):
    """Compute and store average coin data across exchanges."""
    records = compute_average_coin_data(db)
    return {"status": "success", "message": "Average coin data computed and stored", "records": records}


@router.get("/price/{exchange}/{pair}")
async def get_price(exchange: str, pair: str):
    """Get real-time price for a specific pair on an exchange."""
    exchange = exchange.lower()
    if exchange == "binance":
        return await get_crypto_price(pair)
    elif exchange == "kraken":
        return await get_kraken_price(pair)
    elif exchange == "mexc":
        return await get_mexc_price(pair)
    else:
        raise HTTPException(status_code=400, detail="Unsupported exchange")
