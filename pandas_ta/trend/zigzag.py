import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
)


def zigzag(
    high: Series,
    low: Series,
    close: Series = None,
    legs: int = None,
    deviation: IntFloat = None,
    retrace: bool = None,
    last_extreme: bool = None,
    offset: Int = None,
    **kwargs: DictLike
) -> DataFrame:
    """
    Non-repainting ZigZag (no future data usage).

    It identifies a swing (high or low) only *after* price has reversed by a
    certain percentage (deviation) from the most recent pivot. This ensures:
      - No forward-looking data (no "repainting").
      - The same function name & columns, so existing code won't break.

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's. Default: None
        legs (int): (Unused but kept for compatibility) Default: 10
        deviation (float): Price Deviation Percentage to confirm a pivot.
                           Default: 5.0
        retrace (bool): (Unused but kept for compatibility) Default: False
        last_extreme (bool): (Unused but kept for compatibility) Default: True
        offset (int): Positive offset only. Negative shifts would cause leakage.
                      Default: 0

    Kwargs:
        fillna (value, optional): Value to fill missing data
        fill_method (value, optional): Method to fill missing data

    Returns:
        pd.DataFrame with columns:
            "ZIGZAGs_{deviation}%_{legs}" : swing signal (+1 pivot high, -1 pivot low, 0 otherwise)
            "ZIGZAGv_{deviation}%_{legs}" : pivot price at the pivot bar (0 otherwise)
            "ZIGZAGd_{deviation}%_{legs}" : % movement from the last pivot (0 otherwise)
    """
    # 1) Parameter defaults
    legs = v_pos_default(legs, 10)
    deviation = v_pos_default(deviation, 5.0)
    retrace = v_bool(retrace, False)
    last_extreme = v_bool(last_extreme, True)
    offset = v_offset(offset)

    # 2) Validate data
    _length = legs + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    if close is not None:
        close = v_series(close, _length)

    if high is None or low is None or high.empty or low.empty:
        return

    if offset < 0:
        raise ValueError("Negative offset not allowed. It would leak future data.")

    # 3) Prepare arrays
    n = len(high)
    swings = np.full(n, np.nan, dtype=np.float64)    # +1 or -1, else NaN
    pivot_vals = np.full(n, np.nan, dtype=np.float64)
    pivot_dev = np.full(n, np.nan, dtype=np.float64)

    # Convert deviation% to fraction
    dev_frac = deviation / 100.0

    # We'll track the last confirmed pivot index and type
    pivot_idx = 0
    pivot_type = 0  # +1 => last pivot was High, -1 => Low, 0 => undefined
    # Start pivot in the middle of the first bar
    pivot_price = (high.iloc[0] + low.iloc[0]) / 2.0
    last_price = pivot_price

    for i in range(1, n):
        curr_high = high.iloc[i]
        curr_low = low.iloc[i]

        # If pivot_type >= 0 => last pivot was High or undefined
        if pivot_type >= 0:
            drop_frac = (pivot_price - curr_low) / pivot_price  # how far we've dropped from pivot
            if drop_frac >= dev_frac:
                # Confirm prior pivot was High
                if pivot_type == +1:
                    pivot_dev[pivot_idx] = (last_price - pivot_price) / last_price * 100.0
                else:
                    pivot_dev[pivot_idx] = np.nan
                swings[pivot_idx] = +1
                pivot_vals[pivot_idx] = pivot_price

                # New pivot is a Low
                pivot_idx = i
                pivot_price = curr_low
                pivot_type = -1
                last_price = pivot_vals[pivot_idx]
            else:
                # Update pivot if we have a higher high or pivot_type==0 (first iteration)
                if curr_high > pivot_price or pivot_type == 0:
                    pivot_price = curr_high
                    pivot_idx = i

        # If pivot_type <= 0 => last pivot was Low or undefined
        if pivot_type <= 0:
            rise_frac = (curr_high - pivot_price) / pivot_price  # how far we've risen from pivot
            if rise_frac >= dev_frac:
                # Confirm prior pivot was Low
                if pivot_type == -1:
                    pivot_dev[pivot_idx] = (pivot_price - last_price) / last_price * 100.0
                else:
                    pivot_dev[pivot_idx] = np.nan
                swings[pivot_idx] = -1
                pivot_vals[pivot_idx] = pivot_price

                # New pivot is a High
                pivot_idx = i
                pivot_price = curr_high
                pivot_type = +1
                last_price = pivot_vals[pivot_idx]
            else:
                # Update pivot if we have a lower low or pivot_type==0
                if curr_low < pivot_price or pivot_type == 0:
                    pivot_price = curr_low
                    pivot_idx = i

    # Optionally mark final pivot (commented out for real-time usage):
    #   if pivot_type == +1:  # last pivot is a High
    #       swings[pivot_idx] = +1
    #       pivot_vals[pivot_idx] = pivot_price
    #   elif pivot_type == -1:
    #       swings[pivot_idx] = -1
    #       pivot_vals[pivot_idx] = pivot_price
    #   # pivot_dev remains NaN for the last pivot

    # 4) Apply offset if any (positive only)
    if offset > 0:
        swings = np.roll(swings, offset)
        pivot_vals = np.roll(pivot_vals, offset)
        pivot_dev = np.roll(pivot_dev, offset)
        swings[:offset] = np.nan
        pivot_vals[:offset] = np.nan
        pivot_dev[:offset] = np.nan

    # 5) Build DataFrame
    suffix = f"_{deviation}%_{legs}"
    data = {
        f"ZIGZAGs{suffix}": swings,
        f"ZIGZAGv{suffix}": pivot_vals,
        f"ZIGZAGd{suffix}": pivot_dev,
    }
    df = pd.DataFrame(data, index=high.index)
    df.name = f"ZIGZAG{suffix}"
    df.category = "trend"

    # 6) fillna / fill_method from kwargs or default to 0 to avoid NaN values
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)
    elif "fill_method" in kwargs:
        df.fillna(method=kwargs["fill_method"], inplace=True)
    else:
        df.fillna(0, inplace=True)

    return df