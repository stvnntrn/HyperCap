"""
Database models package initialization
"""

from .binance_coin import BinanceCoinData
from .kraken_coin import KrakenCoinData

__all__ = ["BinanceCoinData", "KrakenCoinData"]
