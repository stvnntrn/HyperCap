from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.coin import CoinData


def get_coin(db: Session, symbol: str) -> Optional[CoinData]:
    return db.query(CoinData).filter(CoinData.symbol == symbol).first()


def get_coins(
    db: Session, skip: int = 0, limit: int = 100, sort_by: str = "quote_volume_24h", sort_order: str = "desc"
) -> List[CoinData]:
    query = db.query(CoinData)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(getattr(CoinData, sort_by)))
    else:
        query = query.order_by(getattr(CoinData, sort_by))
    return query.offset(skip).limit(limit).all()


def create_coin(db: Session, coin_data: dict) -> CoinData:
    db_coin = CoinData(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def update_coin(db: Session, symbol: str, coin_data: dict) -> Optional[CoinData]:
    db_coin = get_coin(db, symbol)
    if db_coin:
        for key, value in coin_data.items():
            setattr(db_coin, key, value)
        db.commit()
        db.refresh(db_coin)
    return db_coin


def delete_coin(db: Session, symbol: str) -> bool:
    db_coin = get_coin(db, symbol)
    if db_coin:
        db.delete(db_coin)
        db.commit()
        return True
    return False


def bulk_upsert_coins(db: Session, coins_data: List[dict]) -> None:
    for coin_data in coins_data:
        symbol = coin_data["symbol"]
        existing_coin = get_coin(db, symbol)
        if existing_coin:
            update_coin(db, symbol, coin_data)
        else:
            create_coin(db, coin_data)
