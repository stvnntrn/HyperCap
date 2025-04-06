import logging
from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..crud.coin import bulk_upsert_coins

logger = logging.getLogger(__name__)


def store_coin_data(db: Session, coin_data: List[Dict[str, Any]]) -> int:
    """Store Binance coin data into binance_coin_data table."""
    try:
        if not coin_data:
            logger.info("No coin data to store")
            return 0
        bulk_upsert_coins(db, coin_data)  # Use CRUD function
        logger.info(f"Stored {len(coin_data)} Binance pairs successfully")
        return len(coin_data)
    except Exception as e:
        logger.error(f"Error storing coin data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")
