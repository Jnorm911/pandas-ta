# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta_tnt._typing import DictLike, Int, IntFloat
from pandas_ta_tnt.utils import v_float, v_offset, v_series


def remap(
    close: Series, fmin: IntFloat = None, fmax: IntFloat = None,
    tmin: IntFloat = None, tmax: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """
    Indicator: ReMap (REMAP)

    Maps (normalizes) data from [fmin, fmax] to [tmin, tmax].
    Negative offset is clamped to 0 to avoid forward-looking data.

    Examples:
        RSI -> IFISHER: fmin=0, fmax=100, tmin=-1, tmax=1

    Args:
        close (pd.Series): Series of 'close's
        fmin (float): Input minimum. Default: 0.0
        fmax (float): Input maximum. Default: 100.0
        tmin (float): Output minimum. Default: -1.0
        tmax (float): Output maximum. Default: 1.0
        offset (int): Shift the result forward/backward (>= 0).

    Kwargs:
        fillna (value, optional): pd.Series.fillna(value)

    Returns:
        pd.Series: Remapped feature.
    """
    # Validate
    close = v_series(close)
    fmin = v_float(fmin, 0.0, 0.0)
    fmax = v_float(fmax, 100.0, 0.0)
    tmin = v_float(tmin, -1.0, 0.0)
    tmax = v_float(tmax, 1.0, 0.0)
    offset = v_offset(offset)
    offset = max(offset, 0)  # clamp negative offset

    if close is None:
        return

    # Calculate
    frange = fmax - fmin
    trange = tmax - tmin
    if frange <= 0 or trange <= 0:
        return

    result = tmin + (trange / frange) * (close.to_numpy() - fmin)
    result = Series(result, index=close.index)

    # Offset
    if offset != 0:
        result = result.shift(offset)

    # Fill
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    result.name = f"REMAP_{fmin}_{fmax}_{tmin}_{tmax}"
    result.category = "transform"

    return result