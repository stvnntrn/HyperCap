from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.average_coin import AverageCoinData
from ..models.binance_coin import BinanceCoinData
from ..models.historical_coin_data import HistoricalCoinData
from ..models.kraken_coin import KrakenCoinData
from ..models.mexc_coin import MexCCoinData


def get_binance_coin(db: Session, pair: str) -> Optional[BinanceCoinData]:
    return db.query(BinanceCoinData).filter(BinanceCoinData.pair == pair).first()


def get_kraken_coin(db: Session, pair: str) -> Optional[KrakenCoinData]:
    return db.query(KrakenCoinData).filter(KrakenCoinData.pair == pair).first()


def get_mexc_coin(db: Session, pair: str) -> Optional[MexCCoinData]:
    return db.query(MexCCoinData).filter(MexCCoinData.pair == pair).first()


def get_average_coin(db: Session, pair: str) -> Optional[AverageCoinData]:
    return db.query(AverageCoinData).filter(AverageCoinData.pair == pair).first()


def get_binance_coins(
    db: Session, skip: int = 0, limit: int = 100, sort_by: str = "quote_volume_24h", sort_order: str = "desc"
) -> List[BinanceCoinData]:
    query = db.query(BinanceCoinData)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(getattr(BinanceCoinData, sort_by)))
    else:
        query = query.order_by(getattr(BinanceCoinData, sort_by))
    return query.offset(skip).limit(limit).all()


def create_binance_coin(db: Session, coin_data: dict) -> BinanceCoinData:
    db_coin = BinanceCoinData(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def create_kraken_coin(db: Session, coin_data: dict) -> KrakenCoinData:
    db_coin = KrakenCoinData(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def create_mexc_coin(db: Session, coin_data: dict) -> MexCCoinData:
    db_coin = MexCCoinData(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def create_average_coin(db: Session, coin_data: dict) -> AverageCoinData:
    db_coin = AverageCoinData(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def create_historical_coin(db: Session, coin_data: dict) -> HistoricalCoinData:
    db_coin = HistoricalCoinData(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def update_binance_coin(db: Session, pair: str, coin_data: dict) -> Optional[BinanceCoinData]:
    db_coin = get_binance_coin(db, pair)
    if db_coin:
        for key, value in coin_data.items():
            setattr(db_coin, key, value)
        db.commit()
        db.refresh(db_coin)
    return db_coin


def update_kraken_coin(db: Session, pair: str, coin_data: dict) -> Optional[KrakenCoinData]:
    db_coin = get_kraken_coin(db, pair)
    if db_coin:
        for key, value in coin_data.items():
            setattr(db_coin, key, value)
        db.commit()
        db.refresh(db_coin)
    return db_coin


def update_mexc_coin(db: Session, pair: str, coin_data: dict) -> Optional[MexCCoinData]:
    db_coin = get_mexc_coin(db, pair)
    if db_coin:
        for key, value in coin_data.items():
            setattr(db_coin, key, value)
        db.commit()
        db.refresh(db_coin)
    return db_coin


def update_average_coin(db: Session, pair: str, coin_data: dict) -> Optional[AverageCoinData]:
    db_coin = get_average_coin(db, pair)
    if db_coin:
        for key, value in coin_data.items():
            setattr(db_coin, key, value)
        db.commit()
        db.refresh(db_coin)
    return db_coin


def delete_binance_coin(db: Session, pair: str) -> bool:
    db_coin = get_binance_coin(db, pair)
    if db_coin:
        db.delete(db_coin)
        db.commit()
        return True
    return False


def delete_kraken_coin(db: Session, pair: str) -> bool:
    db_coin = get_kraken_coin(db, pair)
    if db_coin:
        db.delete(db_coin)
        db.commit()
        return True
    return False


def delete_mexc_coin(db: Session, pair: str) -> bool:
    db_coin = get_mexc_coin(db, pair)
    if db_coin:
        db.delete(db_coin)
        db.commit()
        return True
    return False


def delete_average_coin(db: Session, pair: str) -> bool:
    db_coin = get_average_coin(db, pair)
    if db_coin:
        db.delete(db_coin)
        db.commit()
        return True
    return False


def bulk_upsert_coins(db: Session, coins_data: List[dict], table: str = "binance") -> None:
    for coin_data in coins_data:
        pair = coin_data["pair"]
        if table == "binance":
            existing_coin = get_binance_coin(db, pair)
            if existing_coin:
                update_binance_coin(db, pair, coin_data)
            else:
                create_binance_coin(db, coin_data)
        elif table == "kraken":
            existing_coin = get_kraken_coin(db, pair)
            if existing_coin:
                update_kraken_coin(db, pair, coin_data)
            else:
                create_kraken_coin(db, coin_data)
        elif table == "mexc":
            existing_coin = get_mexc_coin(db, pair)
            if existing_coin:
                update_mexc_coin(db, pair, coin_data)
            else:
                create_mexc_coin(db, coin_data)
        elif table == "average":
            existing_coin = get_average_coin(db, pair)
            if existing_coin:
                update_average_coin(db, pair, coin_data)
            else:
                create_average_coin(db, coin_data)
