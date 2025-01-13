"""
.. moduleauthor:: Kevin Johnson
"""
name = "pandas_ta_tnt"

# One-line import of __version__ from the same folder
from ._version import __version__

# If you want to keep a "version" attribute so older code can still do
#   pandas_ta_tnt.version
# just set it equal to __version__:
version = __version__

# Now import everything else needed
from pandas_ta_tnt.maps import (
    EXCHANGE_TZ,
    RATE,
    Category,
    Imports
)
from pandas_ta_tnt.utils import *
from pandas_ta_tnt.utils import __all__ as utils_all

# Flat Structure. Supports ta.ema() or ta.overlap.ema() calls.
from pandas_ta_tnt.candles import *
from pandas_ta_tnt.cycles import *
from pandas_ta_tnt.momentum import *
from pandas_ta_tnt.overlap import *
from pandas_ta_tnt.performance import *
from pandas_ta_tnt.statistics import *
from pandas_ta_tnt.transform import *
from pandas_ta_tnt.trend import *
from pandas_ta_tnt.volatility import *
from pandas_ta_tnt.volume import *

from pandas_ta_tnt.candles import __all__ as candles_all
from pandas_ta_tnt.cycles import __all__ as cycles_all
from pandas_ta_tnt.momentum import __all__ as momentum_all
from pandas_ta_tnt.overlap import __all__ as overlap_all
from pandas_ta_tnt.performance import __all__ as performance_all
from pandas_ta_tnt.statistics import __all__ as statistics_all
from pandas_ta_tnt.transform import __all__ as transform_all
from pandas_ta_tnt.trend import __all__ as trend_all
from pandas_ta_tnt.volatility import __all__ as volatility_all
from pandas_ta_tnt.volume import __all__ as volume_all

# Common Averages for Indicators with a mamode arg, e.g. ta.adx()
from pandas_ta_tnt.ma import ma

# Custom External Directory Commands (see help(import_dir))
from pandas_ta_tnt.custom import create_dir, import_dir

# Enable "ta" DataFrame Extension
from pandas_ta_tnt.core import AnalysisIndicators

__all__ = [
    "name",
    "EXCHANGE_TZ",
    "RATE",
    "Category",
    "Imports",
    "version",
    "ma",
    "create_dir",
    "import_dir",
    "AnalysisIndicators",
]

__all__ += utils_all
__all__ += candles_all
__all__ += cycles_all
__all__ += momentum_all
__all__ += overlap_all
__all__ += performance_all
__all__ += statistics_all
__all__ += transform_all
__all__ += trend_all
__all__ += volatility_all
__all__ += volume_all