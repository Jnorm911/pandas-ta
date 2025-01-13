# -*- coding: utf-8 -*-
from numpy import nan
from pandas import Series
from pandas_ta_tnt._typing import DictLike, Int
from pandas_ta_tnt.utils import v_bool, v_offset, v_pos_default, v_series
import numpy as np


def percent_return(
    close: Series, length: Int = None, cumulative: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Percent Return

    Calculates the percent return of a Series without using forward data.
    Instead of using np.roll (which can inadvertently mix future data), it
    uses .shift() for historical, non-leaking references.

    Sources:
        https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

    Args:
        close (pd.Series): Series of 'close's
        length (int): Its period. Default: 1
        cumulative (bool): If True, returns the cumulative returns.
            Default: False
        offset (int): How many periods to offset the result (>= 0).
            Negative offsets are clamped to 0 to avoid future leakage.

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

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
        pct_return = (close / close.iloc[0]) - 1
    else:
        pct_return = (close / close.shift(length)) - 1
        pct_return.iloc[:length] = nan

    # Offset
    if offset != 0:
        pct_return = pct_return.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pct_return.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pct_return.name = f"{'CUM' if cumulative else ''}PCTRET_{length}"
    pct_return.category = "performance"

    return pct_return