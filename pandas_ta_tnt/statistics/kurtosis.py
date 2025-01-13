# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta_tnt._typing import DictLike, Int
from pandas_ta_tnt.utils import v_offset, v_pos_default, v_series


def kurtosis(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Kurtosis

    Computes the kurtosis over a rolling window. For machine-learning usage,
    rolling windows can still leak future data if not carefully implemented
    in a strictly forward manner. This function only clamps negative offset.

    Args:
        close (pd.Series): Series of 'close's
        length (int): Window size. Default: 30
        offset (int): Shift the result (>= 0)

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        min_periods (int, optional): Passed to rolling().

    Returns:
        pd.Series: Kurtosis
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
    kurtosis = close.rolling(length, min_periods=min_periods).kurt()

    # Offset
    if offset != 0:
        kurtosis = kurtosis.shift(offset)

    # Fill
    if "fillna" in kwargs:
        kurtosis.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    kurtosis.name = f"KURT_{length}"
    kurtosis.category = "statistics"

    return kurtosis