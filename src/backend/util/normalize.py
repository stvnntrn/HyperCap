from typing import Dict


def normalize_coin_abbr(abbr: str, exchange: str) -> str:
    """Normalize coin abbreviations across exchanges."""
    mappings: Dict[str, Dict[str, str]] = {
        "kraken": {
            "XBT": "BTC",
            "BCHABC": "BCH",
            # Add more Kraken-specific mappings as needed
        },
        "binance": {},
        "mexc": {},
    }
    return mappings.get(exchange, {}).get(abbr.upper(), abbr.upper())


def denormalize_coin_abbr(abbr: str, exchange: str) -> str:
    """Reverse normalization for exchange-specific queries."""
    reverse_mappings: Dict[str, Dict[str, str]] = {
        "kraken": {
            v: k
            for k, v in {
                "XBT": "BTC",
                "BCHABC": "BCH",
            }.items()
        },
        "binance": {},
        "mexc": {},
    }
    return reverse_mappings.get(exchange, {}).get(abbr.upper(), abbr.upper())
