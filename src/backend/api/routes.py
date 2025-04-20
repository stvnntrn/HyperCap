from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.binance_coin import BinanceCoinData
from ..models.kraken_coin import KrakenCoinData
from ..models.mexc_coin import MexCCoinData
from ..schemas.coin import CoinInDB
from ..services.binance_service import fetch_ticker_data as fetch_binance_ticker_data
from ..services.binance_service import get_crypto_price
from ..services.coin_service import store_coin_data
from ..services.coingecko_service import append_supply_data
from ..services.kraken_service import fetch_kraken_ticker_data, get_kraken_price
from ..services.mexc_service import fetch_mexc_ticker_data, get_mexc_price

router = APIRouter()


@router.get("/marketcap/")
async def get_marketcap_data(page: Optional[int] = 1, size: Optional[int] = 100, db: Session = Depends(get_db)):
    """List USDT pairs, sorted by market_cap."""
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Page and size must be positive")
    skip = (page - 1) * size
    binance_coins = (
        db.query(BinanceCoinData)
        .filter(BinanceCoinData.quote_currency == "USDT")
        .order_by(BinanceCoinData.market_cap.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    kraken_coins = (
        db.query(KrakenCoinData)
        .filter(KrakenCoinData.quote_currency.in_(["USD", "ZUSD"]))
        .order_by(KrakenCoinData.market_cap.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    mexc_coins = (
        db.query(MexCCoinData)
        .filter(MexCCoinData.quote_currency == "USDT")
        .order_by(MexCCoinData.market_cap.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    total_binance = db.query(BinanceCoinData).filter(BinanceCoinData.quote_currency == "USDT").count()
    total_kraken = db.query(KrakenCoinData).filter(KrakenCoinData.quote_currency.in_(["USD", "ZUSD"])).count()
    total_mexc = db.query(MexCCoinData).filter(MexCCoinData.quote_currency == "USDT").count()
    return {
        "status": "success",
        "data": {
            "binance": [CoinInDB.model_validate(coin) for coin in binance_coins],
            "kraken": [CoinInDB.model_validate(coin) for coin in kraken_coins],
            "mexc": [CoinInDB.model_validate(coin) for coin in mexc_coins],
        },
        "total": {"binance": total_binance, "kraken": total_kraken, "mexc": total_mexc},
    }


@router.get("/coin/{coin_abbr}")
async def get_coin_details(coin_abbr: str, db: Session = Depends(get_db)):
    """Get details for a coin's USDT pair."""
    coin_abbr = coin_abbr.upper()
    binance_coin = (
        db.query(BinanceCoinData)
        .filter(BinanceCoinData.coin_abbr == coin_abbr, BinanceCoinData.quote_currency == "USDT")
        .first()
    )
    kraken_coin = (
        db.query(KrakenCoinData)
        .filter(KrakenCoinData.coin_abbr == coin_abbr, KrakenCoinData.quote_currency.in_(["USD", "ZUSD"]))
        .first()
    )
    mexc_coin = (
        db.query(MexCCoinData)
        .filter(MexCCoinData.coin_abbr == coin_abbr, MexCCoinData.quote_currency == "USDT")
        .first()
    )
    available_on = []
    if binance_coin:
        available_on.append("Binance")
    if kraken_coin:
        available_on.append("Kraken")
    if mexc_coin:
        available_on.append("MEXC")
    if not available_on:
        raise HTTPException(status_code=404, detail="Coin not found in USDT pair")
    return {
        "status": "success",
        "coin": {
            "binance": CoinInDB.model_validate(binance_coin) if binance_coin else None,
            "kraken": CoinInDB.model_validate(kraken_coin) if kraken_coin else None,
            "mexc": CoinInDB.model_validate(mexc_coin) if mexc_coin else None,
        },
        "available_on": available_on,
    }


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
async def update_supply_data(db: Session = Depends(get_db)):
    """Update supply data for Binance, Kraken, and MEXC from CoinGecko."""
    binance_ticker_data = await fetch_binance_ticker_data(db)
    kraken_ticker_data = await fetch_kraken_ticker_data(db)
    mexc_ticker_data = await fetch_mexc_ticker_data(db)
    updated_binance = await append_supply_data(db, binance_ticker_data)
    updated_kraken = await append_supply_data(db, kraken_ticker_data)
    updated_mexc = await append_supply_data(db, mexc_ticker_data)
    binance_records = store_coin_data(db, updated_binance, table="binance")
    kraken_records = store_coin_data(db, updated_kraken, table="kraken")
    mexc_records = store_coin_data(db, updated_mexc, table="mexc")
    return {
        "status": "success",
        "message": "Supply data updated from CoinGecko",
        "records": {"binance": binance_records, "kraken": kraken_records, "mexc": mexc_records},
    }


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
