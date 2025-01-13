# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta_tnt._typing import DictLike, Int
from pandas_ta_tnt.overlap import sma
from pandas_ta_tnt.utils import v_bool, v_offset, v_pos_default, v_series


def dpo(
    close: Series, length: Int = None, centered: bool = True,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Detrend Price Oscillator (DPO)

    DPO attempts to remove trend from price and highlight cycles.

    If 'centered' is True, it shifts data backward by t = int(0.5 * length)+1,
    then forward again, effectively referencing future bars. This can cause
    data leakage in ML. Setting 'lookahead=False' in kwargs disables centering.

    Negative offsets are also clamped to prevent future leakage.

    Sources:
        https://www.tradingview.com/scripts/detrendedpriceoscillator/
        https://www.fidelity.com/learning-center/trading-investing/
             technical-analysis/technical-indicator-guide/dpo
        http://stockcharts.com/school/doku.php?id=chart_school:
            technical_indicators:detrended_price_osci

    Args:
        close (pd.Series): Series of 'close's
        length (int): Period. Default: 20
        centered (bool): If True, references data around the middle, 
            effectively peeking forward. Default: True
        offset (int): Shift result forward/backward (>= 0)

    Kwargs:
        lookahead (bool): If False, forcibly sets centered=False.
        fillna (value, optional): pd.Series.fillna(value)

    Returns:
        pd.Series: DPO
    """
    # Validate
    length = v_pos_default(length, 20)
    close = v_series(close, length + 1)
    if close is None:
        return

    centered = v_bool(centered, True)
    if not kwargs.get("lookahead", True):
        centered = False

    offset = v_offset(offset)
    offset = max(offset, 0)  # Clamp negative offsets

    # Calculate
    t = int(0.5 * length) + 1
    ma = sma(close, length)

    if centered:
        # shift forward and backward
        dpo = (close.shift(t) - ma).shift(-t)
    else:
        # standard approach with only backward shift
        dpo = close - ma.shift(t)

    # Offset
    if offset != 0:
        dpo = dpo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        dpo.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    dpo.name = f"DPO_{length}"
    dpo.category = "trend"

    return dpo