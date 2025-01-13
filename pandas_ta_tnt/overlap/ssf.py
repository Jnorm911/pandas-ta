# -*- coding: utf-8 -*-
from numpy import copy, cos, exp
from numba import njit
from pandas import Series
from pandas_ta_tnt._typing import DictLike, Int, IntFloat
from pandas_ta_tnt.utils import (
    v_bool, v_offset, v_pos_default, v_series
)


@njit(cache=True)
def nb_ssf(x, n, pi, sqrt2):
    m = x.size
    ratio = sqrt2 / n
    result = copy(x)
    a = exp(-pi * ratio)
    b = 2 * a * cos(180 * ratio)
    c = a * a - b + 1

    for i in range(2, m):
        result[i] = 0.5 * c * (x[i] + x[i - 1]) + b * result[i - 1] \
            - a * a * result[i - 2]
    return result


@njit(cache=True)
def nb_ssf_everget(x, n, pi, sqrt2):
    m = x.size
    arg = pi * sqrt2 / n
    result = copy(x)
    a = exp(-arg)
    b = 2 * a * cos(arg)

    for i in range(2, m):
        result[i] = 0.5 * (a * a - b + 1) * (x[i] + x[i - 1]) \
            + b * result[i - 1] - a * a * result[i - 2]
    return result


def ssf(
    close: Series, length: Int = None,
    everget: bool = None, pi: IntFloat = None, sqrt2: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Ehler's Super Smoother Filter (SSF)

    A recursive digital filter with two poles to reduce lag. Some forms can 
    leak data in ML usage if not carefully handled bar-by-bar. Here we only
    clamp negative offset to avoid explicit forward shift.

    Sources:
        http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html
        https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/

    Args:
        close (pd.Series)
        length (int): Period. Default: 20
        everget (bool): If True, uses nb_ssf_everget logic (TradingView).
        pi (float): PI factor. Default: 3.14159
        sqrt2 (float): sqrt(2) factor. Default: 1.414
        offset (int): Shift (>= 0)

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.Series: SSF
    """
    # Validate
    length = v_pos_default(length, 20)
    close = v_series(close, length)
    if close is None:
        return

    pi = v_pos_default(pi, 3.14159)
    sqrt2 = v_pos_default(sqrt2, 1.414)
    everget = v_bool(everget, False)
    offset = v_offset(offset)
    offset = max(offset, 0)  # clamp negative offset

    # Calculate
    np_close = close.to_numpy()
    if everget:
        result = nb_ssf_everget(np_close, length, pi, sqrt2)
    else:
        result = nb_ssf(np_close, length, pi, sqrt2)

    ssf_ = Series(result, index=close.index)

    # Offset
    if offset != 0:
        ssf_ = ssf_.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ssf_.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    ssf_.name = f"SSF{'e' if everget else ''}_{length}"
    ssf_.category = "overlap"

    return ssf_