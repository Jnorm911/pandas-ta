# -*- coding: utf-8 -*-
from numpy import exp, isnan, logical_and, max, min
from pandas import DataFrame, Series
from pandas_ta_tnt._typing import DictLike, Int, IntFloat
from pandas_ta_tnt.utils import v_int, v_offset, v_scalar, v_series
from .remap import remap


def ifisher(
    close: Series,
    amp: IntFloat = None, signal_offset: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """
    Indicator: Inverse Fisher Transform

    Transforms data in [-1, 1] domain using the inverse Fisher function.
    Negative offsets are clamped to 0 to prevent future data leakage.

    Sources:
        https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf
        Book: Cycle Analytics for Traders, 2014, by John Ehlers (p.198)

    Args:
        close (pd.Series): Series of 'close's
        amp (float): Amplification factor. Default: 1
        signal_offset (int): Signal line shift (>= 0). Default: -1
        offset (int): Final result shift (>= 0). Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: Two columns for the transform and signal.
    """
    # Validate
    close = v_series(close)
    amp = v_scalar(amp, 1.0)
    signal_offset = v_int(signal_offset, -1, 0)
    offset = v_offset(offset)

    # Clamp offsets to avoid future leakage
    offset = max(offset, 0)
    signal_offset = max(signal_offset, 0)

    # Calculate
    np_close = close.to_numpy()
    is_remapped = logical_and(np_close >= -1, np_close <= 1)
    if not all(is_remapped):
        np_max, np_min = max(np_close), min(np_close)
        close_map = remap(
            close,  # calls our updated remap
            fmin=np_min, fmax=np_max, tmin=-1, tmax=1
        )
        if close_map is None or all(isnan(close_map.to_numpy())):
            return  # Emergency Break
        np_close = close_map.to_numpy()

    amped = exp(amp * np_close)
    result = (amped - 1) / (amped + 1)

    inv_fisher = Series(result, index=close.index)
    signal = Series(result, index=close.index)

    # Offset
    if offset != 0:
        inv_fisher = inv_fisher.shift(offset)
        signal = signal.shift(offset)
    if signal_offset != 0:
        inv_fisher = inv_fisher.shift(signal_offset)
        signal = signal.shift(signal_offset)

    # Fill
    if "fillna" in kwargs:
        inv_fisher.fillna(kwargs["fillna"], inplace=True)
        signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{amp}"
    inv_fisher.name = f"INVFISHER{_props}"
    signal.name = f"INVFISHERs{_props}"
    inv_fisher.category = signal.category = "transform"

    data = {inv_fisher.name: inv_fisher, signal.name: signal}
    df = DataFrame(data, index=close.index)
    df.name = f"INVFISHER{_props}"
    df.category = inv_fisher.category

    return df