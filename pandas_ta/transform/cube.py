import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import (
    v_series, v_lowerbound, v_int, v_offset
)


def cube(
    close: Series,
    pwr: IntFloat = None,
    signal_offset: Int = None,
    offset: Int = None,
    **kwargs: DictLike
) -> DataFrame:
    """
    Cube Transform (non-leaking, scaled outputs)

    John Ehlers describes this indicator to be useful in compressing signals
    near zero for a normalized oscillator like the Inverse Fisher Transform.
    This version:
      1) Disallows negative shifting (no future leakage).
      2) Scales outputs to avoid extreme spikes.

    Sources:
        Book: Cycle Analytics for Traders, 2014, John Ehlers (p.200)
        Coded by rengel8 based on Markus K. (cryptocoinserver)'s source.

    Args:
        close (pd.Series): Series of 'close' values.
        pwr (float): The exponent. Default=3.0.
        signal_offset (int): Additional shift for the signal line. Must be >= 0.
                             Default=0 in practice, though old code used -1.
        offset (int): Shift for the main output. Must be >= 0. Default=0.

    Kwargs:
        scale_minmax (int): The integer bound to clamp the output. Default=100.
        rolling_window (int): Window for rolling max calculation. Default=100.
        fillna (value, optional): pd.DataFrame.fillna(value).
    
    Returns:
        pd.DataFrame: Two columns:
            - 'CUBE_{pwr}_{signal_offset}'
            - 'CUBEs_{pwr}_{signal_offset}'
        Both columns are integer-scaled transforms of 'close'**pwr.
    """
    # Validate input
    close = v_series(close)
    if close is None or close.empty:
        return

    # Default parameter handling
    if pwr is None:
        pwr = 3.0
    pwr = v_lowerbound(pwr, 3.0, 3.0, strict=False)

    if signal_offset is None:
        # Older code used -1 by default, which leaks. We set to 0 by default now.
        signal_offset = 0
    signal_offset = v_int(signal_offset, 0, 0)
    if signal_offset < 0:
        raise ValueError("cube(): Negative signal_offset not allowed (future leakage).")

    if offset is None:
        offset = 0
    offset = v_offset(offset)
    if offset < 0:
        raise ValueError("cube(): Negative offset not allowed (future leakage).")

    # Additional kwargs for scaling
    scale_minmax = kwargs.pop("scale_minmax", 100)
    rolling_window = kwargs.pop("rolling_window", 100)

    # 1) Exponentiate
    result = close**pwr  # uses current bar only

    # 2) Rolling-based absolute max to avoid large outliers
    #    - real-time safe (doesn't see future)
    rolling_absmax = (
        result.abs()
              .rolling(window=rolling_window, min_periods=1)
              .max()
              .replace(0, np.nan)
              .ffill()
    )
    rolling_absmax.fillna(1.0, inplace=True)  # avoid div-by-zero

    # 3) Scale to ±scale_minmax & convert to int
    scaled = (result / rolling_absmax) * scale_minmax
    scaled_clamped = scaled.clip(-scale_minmax, scale_minmax).round().astype(int)

    # Create main output and "signal" (same data, different shift)
    ct = pd.Series(scaled_clamped, index=close.index)
    ct_signal = ct.copy()

    # 4) Shift if needed (no negative shift allowed)
    if offset > 0:
        ct = ct.shift(offset)
        ct_signal = ct_signal.shift(offset)
    if signal_offset > 0:
        ct = ct.shift(signal_offset)
        ct_signal = ct_signal.shift(signal_offset)

    # 5) Fill NaNs
    if "fillna" in kwargs:
        fill_val = kwargs["fillna"]
        ct.fillna(fill_val, inplace=True)
        ct_signal.fillna(fill_val, inplace=True)

    # 6) Name columns & build DataFrame
    _props = f"_{pwr}_{signal_offset}"
    ct.name = f"CUBE{_props}"
    ct_signal.name = f"CUBEs{_props}"
    ct.category = "transform"
    ct_signal.category = "transform"

    df = pd.DataFrame({ct.name: ct, ct_signal.name: ct_signal}, index=close.index)
    df.name = f"CUBE{_props}"
    df.category = "transform"

    return df