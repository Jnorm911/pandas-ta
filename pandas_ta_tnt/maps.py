# -*- coding: utf-8 -*-
"""
maps.py - Contains dictionaries, version references, category definitions, etc.
"""

from importlib.util import find_spec
from pathlib import Path
from pkg_resources import DistributionNotFound

from pandas_ta_tnt._typing import Dict, IntFloat, ListStr

# 1) Import the same version used by the package
try:
    from ._version import __version__ as version
except ImportError:
    version = "unknown"

Imports: Dict[str, bool] = {
    "alphaVantage-api": find_spec("alphaVantageAPI") is not None,
    "dotenv": find_spec("dotenv") is not None,
    "matplotlib": find_spec("matplotlib") is not None,
    "mplfinance": find_spec("mplfinance") is not None,
    "numba": find_spec("numba") is not None,
    "polygon": find_spec("polygon") is not None,
    "scipy": find_spec("scipy") is not None,
    "sklearn": find_spec("sklearn") is not None,
    "statsmodels": find_spec("statsmodels") is not None,
    "stochastic": find_spec("stochastic") is not None,
    "talib": find_spec("talib") is not None,
    "tqdm": find_spec("tqdm") is not None,
    "urllib": find_spec("urllib") is not None,
    "vectorbt": find_spec("vectorbt") is not None,
    "yaml": find_spec("yaml") is not None,
    "yfinance": find_spec("yfinance") is not None,
}

# Not ideal and not dynamic but it works.
# Will find a dynamic solution later.
Category: Dict[str, ListStr] = {
    # Candles
    "candles": [
        "cdl_pattern", "cdl_z", "ha"
    ],
    # Cycles
    "cycles": ["ebsw", "reflex"],
    # Momentum
    "momentum": [
        "ao", "apo", "bias", "bop", "brar", "cci", "cfo", "cg", "cmo",
        "coppock", "crsi", "cti", "er", "eri", "exhc", "fisher", "inertia",
        "kdj", "kst", "macd", "mom", "pgo", "ppo", "psl", "qqe", "roc",
        "rsi", "rsx", "rvgi", "slope", "smc", "smi", "squeeze", "squeeze_pro",
        "stc", "stoch", "stochf", "stochrsi", "tmo", "trix", "tsi", "uo",
        "willr"
    ],
    # Overlap
    "overlap": [
        "alligator", "alma", "dema", "ema", "fwma", "hilo", "hl2", "hlc3",
        "hma", "hwma", "ichimoku", "jma", "kama", "linreg", "mama",
        "mcgd", "midpoint", "midprice", "ohlc4", "pivots", "pwma", "rma",
        "sinwma", "sma", "smma", "ssf", "ssf3", "supertrend", "swma", "t3",
        "tema", "trima", "vidya", "wcp", "wma", "zlma"
    ],
    # Performance
    "performance": ["log_return", "percent_return"],
    # Statistics
    "statistics": [
        "entropy", "kurtosis", "mad", "median", "quantile", "skew", "stdev",
        "tos_stdevall", "variance", "zscore"
    ],
    # Transform
    "transform": ["cube", "ifisher", "remap"],
    # Trend
    "trend": [
        "adx", "alphatrend", "amat", "aroon", "chop", "cksp", "decay",
        "decreasing", "dpo", "ht_trendline", "increasing", "long_run",
        "psar", "qstick", "rwi", "short_run", "trendflex", "tsignals",
        "vhf", "vortex", "xsignals", "zigzag"
    ],
    # Volatility
    "volatility": [
        "aberration", "accbands", "atr", "atrts", "bbands", "chandelier_exit",
        "donchian", "hwc", "kc", "massi", "natr", "pdist", "rvi", "thermo",
        "true_range", "ui"
    ],

    # Volume.
    # Note: "vp" or "Volume Profile" is excluded since it does not return a Time Series
    "volume": [
        "ad", "adosc", "aobv", "cmf", "efi", "eom", "kvo", "mfi", "nvi",
        "obv", "pvi", "pvo", "pvol", "pvr", "pvt", "vhm", "vwap", "vwma",
        "wb_tsv"
    ],
}

CANDLE_AGG: Dict[str, str] = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum"
}

# https://www.worldtimezone.com/markets24.php
EXCHANGE_TZ: Dict[str, IntFloat] = {
    "NZSX": 12, "ASX": 11,
    "TSE": 9, "HKE": 8, "SSE": 8, "SGX": 8,
    "NSE": 5.5, "DIFX": 4, "RTS": 3,
    "JSE": 2, "FWB": 1, "LSE": 1,
    "BMF": -2, "NYSE": -4, "TSX": -4,
    "GENR": 0 # Generated Data
}

RATE: Dict[str, IntFloat] = {
    "DAYS_PER_MONTH": 21,
    "MINUTES_PER_HOUR": 60,
    "MONTHS_PER_YEAR": 12,
    "QUARTERS_PER_YEAR": 4,
    "TRADING_DAYS_PER_YEAR": 252,  # Keep even
    "TRADING_HOURS_PER_DAY": 6.5,
    "WEEKS_PER_YEAR": 52,
    "YEARLY": 1,
}