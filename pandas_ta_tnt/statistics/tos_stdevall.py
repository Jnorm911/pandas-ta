# -*- coding: utf-8 -*-
from numpy import arange, array, polyfit, std
from pandas import DataFrame, DatetimeIndex, Series
from pandas_ta_tnt._typing import DictLike, Int, List
from pandas_ta_tnt.utils import v_list, v_lowerbound, v_offset, v_series


def tos_stdevall(
    close: Series, length: Int,
    stds: List = None, ddof: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """TD Ameritrade's Think or Swim Standard Deviation All (TOS_STDEV)

    A port of TOS Standard Deviation All, but forced to require a user-defined
    'length' to avoid referencing the entire future dataset at once.
    Any negative offset is clamped to 0.

    WARNING: Using a single large 'length' over the entire dataset means the
    final lines are computed from that entire chunk. For true bar-by-bar
    usage, you'd need a rolling approach.

    Sources:
        https://tlc.thinkorswim.com/center/reference/thinkScript/Functions/Statistical/StDevAll

    Args:
        close (pd.Series): Series of 'close's
        length (int): Required window length (>= 2)
        stds (list): List of Standard Deviations in ascending order from the
            central Linear Regression line. Default: [1, 2, 3]
        ddof (int): Delta Degrees of Freedom. The divisor used in
            calculations is N - ddof. Default: 1
        offset (int): Shift the final lines forward/backward (>= 0).

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: LR plus pairs of Lower/Upper LR lines (multiple stdev).
    """
    if length is None:
        raise ValueError(
            "tos_stdevall requires a 'length' to avoid full-future leakage."
        )

    close = v_series(close, 2)
    if close is None:
        return

    # Validate
    length = v_lowerbound(length, 2, 30)
    close = close.iloc[-length:]  # Only the last 'length' bars
    stds = v_list(stds, [1, 2, 3])
    if min(stds) <= 0:
        return
    # Ensure ascending order
    if not all(i < j for i, j in zip(stds, stds[1:])):
        stds = stds[::-1]

    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    offset = v_offset(offset)
    offset = max(offset, 0)  # clamp

    # Calculate
    X = close.index
    if isinstance(close.index, DatetimeIndex):
        X = arange(length)
        close_arr = array(close)
    else:
        close_arr = close.to_numpy()

    m, b = polyfit(X, close_arr, 1)
    lr = Series(m * X + b, index=close.index)
    stdev_val = std(close_arr, ddof=ddof)

    # Build DataFrame
    _props = f"TOS_STDEVALL_{length}"
    df = DataFrame({f"{_props}_LR": lr}, index=close.index)
    for i in stds:
        df[f"{_props}_L_{i}"] = lr - i * stdev_val
        df[f"{_props}_U_{i}"] = lr + i * stdev_val
        df[f"{_props}_L_{i}"].name = df[f"{_props}_U_{i}"].name = f"{_props}"
        df[f"{_props}_L_{i}"].category = df[f"{_props}_U_{i}"].category = "statistics"

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    df.name = _props
    df.category = "statistics"

    return df