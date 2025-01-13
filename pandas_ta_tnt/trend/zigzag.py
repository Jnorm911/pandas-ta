# -*- coding: utf-8 -*-
from numpy import floor, isnan, nan, zeros, zeros_like
from numba import njit
from pandas import Series, DataFrame
from pandas_ta_tnt._typing import DictLike, Int, IntFloat
from pandas_ta_tnt.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
)


@njit(cache=True)
def nb_rolling_hl(np_high, np_low, window_size):
    m = np_high.size
    idx = zeros(m)
    swing = zeros(m)
    value = zeros(m)

    extremums = 0
    left = int(floor(window_size / 2))
    right = left + 1
    for i in range(left, m - right):
        low_center = np_low[i]
        high_center = np_high[i]
        low_window = np_low[i - left : i + right]
        high_window = np_high[i - left : i + right]

        if (low_center <= low_window).all():
            idx[extremums] = i
            swing[extremums] = -1
            value[extremums] = low_center
            extremums += 1

        if (high_center >= high_window).all():
            idx[extremums] = i
            swing[extremums] = 1
            value[extremums] = high_center
            extremums += 1

    return idx[:extremums], swing[:extremums], value[:extremums]


@njit(cache=True)
def nb_find_zigzags(idx, swing, value, deviation):
    zz_idx = zeros_like(idx)
    zz_swing = zeros_like(swing)
    zz_value = zeros_like(value)
    zz_dev = zeros_like(idx)

    zigzags = 0
    zz_idx[zigzags] = idx[-1]
    zz_swing[zigzags] = swing[-1]
    zz_value[zigzags] = value[-1]
    zz_dev[zigzags] = 0

    m = idx.size
    for i in range(m - 2, -1, -1):
        # If last point in zigzag is bottom
        if zz_swing[zigzags] == -1:
            if swing[i] == -1:
                if zz_value[zigzags] > value[i] and zigzags > 1:
                    current_dev = (zz_value[zigzags - 1] - value[i]) / value[i]
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev
            else:
                current_dev = (value[i] - zz_value[zigzags]) / value[i]
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags] == idx[i]:
                        continue
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev

        # If last point in zigzag is peak
        else:
            if swing[i] == 1:
                if zz_value[zigzags] < value[i] and zigzags > 1:
                    current_dev = (value[i] - zz_value[zigzags - 1]) / value[i]
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev
            else:
                current_dev = (zz_value[zigzags] - value[i]) / value[i]
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags] == idx[i]:
                        continue
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev

    _n = zigzags + 1
    return zz_idx[:_n], zz_swing[:_n], zz_value[:_n], zz_dev[:_n]


@njit(cache=True)
def nb_map_zigzag(idx, swing, value, deviation, n):
    swing_map = zeros(n)
    value_map = zeros(n)
    dev_map = zeros(n)

    for j, i in enumerate(idx):
        i = int(i)
        swing_map[i] = swing[j]
        value_map[i] = value[j]
        dev_map[i] = deviation[j]

    for i in range(n):
        if swing_map[i] == 0:
            swing_map[i] = nan
            value_map[i] = nan
            dev_map[i] = nan

    return swing_map, value_map, dev_map


def zigzag(
    high: Series, low: Series, close: Series = None,
    legs: int = None, deviation: IntFloat = None,
    retrace: bool = None, last_extreme: bool = None,
    offset: Int = None, **kwargs: DictLike
):
    """Zigzag (ZIGZAG)

    Zigzag is inherently a future-looking indicator since it "confirms" pivots
    only in hindsight. This version simply clamps any negative offset to 0 so
    you cannot forcibly shift the final result into the past (which would
    explicitly leak future data).

    Args:
        high, low (pd.Series)
        close (pd.Series): Optional
        legs (int): Window size
        deviation (float): Price deviation threshold
        retrace (bool): Not used, placeholder
        last_extreme (bool): Not used, placeholder
        offset (int): Shift (>= 0) to avoid future leakage.

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)

    Returns:
        pd.DataFrame: swing, swing_value, swing_deviation
    """
    # Validate
    legs = v_pos_default(legs, 10)
    _length = legs + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    if high is None or low is None:
        return

    if close is not None:
        close = v_series(close, _length)
        if close is None:
            return

    deviation = v_pos_default(deviation, 5.0)
    retrace = v_bool(retrace, False)
    last_extreme = v_bool(last_extreme, True)
    offset = v_offset(offset)
    offset = max(offset, 0)  # Clamp negative offset

    # Calculation
    np_high, np_low = high.to_numpy(), low.to_numpy()
    hli, hls, hlv = nb_rolling_hl(np_high, np_low, legs)
    zzi, zzs, zzv, zzd = nb_find_zigzags(hli, hls, hlv, deviation)
    zz_swing, zz_value, zz_dev = nb_map_zigzag(zzi, zzs, zzv, zzd, np_high.size)

    zz_swing = Series(zz_swing, index=high.index)
    zz_value = Series(zz_value, index=high.index)
    zz_dev = Series(zz_dev, index=high.index)

    # Offset
    if offset != 0:
        zz_swing = zz_swing.shift(offset)
        zz_value = zz_value.shift(offset)
        zz_dev = zz_dev.shift(offset)

    # Fill
    if "fillna" in kwargs:
        zz_swing.fillna(kwargs["fillna"], inplace=True)
        zz_value.fillna(kwargs["fillna"], inplace=True)
        zz_dev.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        zz_swing.fillna(method=kwargs["fill_method"], inplace=True)
        zz_value.fillna(method=kwargs["fill_method"], inplace=True)
        zz_dev.fillna(method=kwargs["fill_method"], inplace=True)

    _props = f"_{deviation}%_{legs}"
    data = {
        f"ZIGZAGs{_props}": zz_swing,
        f"ZIGZAGv{_props}": zz_value,
        f"ZIGZAGd{_props}": zz_dev,
    }
    df = DataFrame(data, index=high.index)
    df.name = f"ZIGZAG{_props}"
    df.category = "trend"

    return df