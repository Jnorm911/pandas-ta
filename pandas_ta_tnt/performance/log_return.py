# -*- coding: utf-8 -*-
from pandas import Series
from numpy import log, nan
from pandas_ta_tnt._typing import DictLike, Int
from pandas_ta_tnt.utils import v_bool, v_offset, v_pos_default, v_series
import numpy as np


def log_return(
    close: Series, length: Int = None, cumulative: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Log Return

    Calculates the logarithmic return of a Series without using forward data.
    Instead of using np.roll (which can inadvertently mix future data), it
    uses .shift() for historical, non-leaking references.

    Sources:
        https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

    Args:
        close (pd.Series): Series of 'close's
        length (int): It's period. Default: 1
        cumulative (bool): If True, returns the cumulative returns.
            Default: False
        offset (int): How many periods to offset the result (>= 0). 
            Negative offsets are clamped to 0 to avoid future leakage.

    Kwargs:
        fillna (value, optional): pd.Series.fillna(value)

    Returns:
        pd.Series: New feature generated.
    """
    # Validate
    length = v_pos_default(length, 1)
    close = v_series(close, length + 1)
    if close is None:
        return

    cumulative = v_bool(cumulative, False)
    offset = v_offset(offset)
    offset = max(offset, 0)  # Clamp negative offset

    # Calculate
    if cumulative:
        # Log of ratio from first valid to current
        log_return = (close / close.iloc[0]).apply(np.log)
    else:
        # Log of ratio from length bars ago
        log_return = (close / close.shift(length)).apply(np.log)
        # First 'length' bars have insufficient history
        log_return.iloc[:length] = nan

    # Offset
    if offset != 0:
        log_return = log_return.shift(offset)

    # Fill
    if "fillna" in kwargs:
        log_return.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    log_return.name = f"{'CUM' if cumulative else ''}LOGRET_{length}"
    log_return.category = "performance"

    return log_return