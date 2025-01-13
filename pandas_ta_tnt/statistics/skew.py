# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta_tnt._typing import DictLike, Int
from pandas_ta_tnt.utils import v_offset, v_pos_default, v_series


def skew(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Skew

    Computes the skewness over a rolling window. For ML usage, purely 
    historical rolling windows can still leak if not handled properly. This
    function clamps negative offset to avoid explicit forward shift.

    Args:
        close (pd.Series): Series of 'close's
        length (int): Rolling window size. Default: 30
        offset (int): Shift the result (>= 0)

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        min_periods (int, optional): Passed to rolling().

    Returns:
        pd.Series: Rolling Skew
    """
    # Validate
    length = v_pos_default(length, 30)
    min_periods = kwargs.get("min_periods", length)
    if min_periods is None:
        min_periods = length
    close = v_series(close, max(length, min_periods))
    if close is None:
        return

    offset = v_offset(offset)
    offset = max(offset, 0)  # Clamp negative offset

    # Calculate
    skew = close.rolling(length, min_periods=min_periods).skew()

    # Offset
    if offset != 0:
        skew = skew.shift(offset)

    # Fill
    if "fillna" in kwargs:
        skew.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    skew.name = f"SKEW_{length}"
    skew.category = "statistics"

    return skew