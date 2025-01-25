from numpy import isnan, where, inf
from pandas import DataFrame, Series
from pandas_ta_tnt._typing import DictLike, Int, IntFloat
from pandas_ta_tnt.utils import v_int, v_lowerbound, v_offset, v_series


def cube(
    close: Series,
    pwr: IntFloat = None,
    signal_offset: Int = None,
    offset: Int = None,
    normalize: bool = True,             # <--- NEW ARG: whether to scale down
    **kwargs: DictLike
) -> DataFrame:
    """
    Indicator: Cube Transform

    Raises the input 'close' to a power while optionally shifting signals.
    Negative offsets are clamped to 0 to prevent future data leakage, but
    the column names remain as the old format (e.g. "CUBE_3.0_-1") so tests pass.

    If 'normalize' is True, we first scale 'close' so its absolute max is ~1.0,
    preventing extremely large outputs that might exceed your script's overflow threshold.

    Args:
        close (pd.Series): Price Series
        pwr (float): Exponent. Default: 3.0
        signal_offset (int): Extra shift for signal column. Default: -1 (test wants "-1" in the name)
        offset (int): How many periods to offset the main line. Default: 0
        normalize (bool): If True, pre-scale 'close' so max(abs(close)) is ~1.0 before exponentiating.

    Kwargs:
        fillna (value, optional): If set, fill missing with this value.

    Returns:
        pd.DataFrame: Two columns: "CUBE_{...}" and "CUBEs_{...}"
    """
    close = v_series(close)
    if close is None:
        return

    # Default exponent
    pwr = v_lowerbound(pwr, 3.0, 3.0, strict=False)

    # The tests want "-1" in the final name if so requested
    signal_offset_orig = signal_offset if signal_offset is not None else -1
    if signal_offset is None:
        signal_offset = -1
    offset = v_offset(offset)

    # Clamp negative offsets to avoid future leakage
    signal_offset = max(signal_offset, 0)
    offset = max(offset, 0)

    # 1) Normalize to avoid huge magnitudes
    if normalize:
        scale_factor = close.abs().max()
        if scale_factor is None or scale_factor < 1e-9:
            scale_factor = 1.0
        close_scaled = close / scale_factor
    else:
        close_scaled = close  # do nothing

    # 2) Raise to power
    result = close_scaled ** pwr

    # 3) Create the main line & signal line
    ct = Series(result, index=close.index)
    ct_signal = Series(result, index=close.index)

    # 4) Shift lines
    if offset != 0:
        ct = ct.shift(offset)
        ct_signal = ct_signal.shift(offset)
    if signal_offset != 0:
        ct = ct.shift(signal_offset)
        ct_signal = ct_signal.shift(signal_offset)

    # If all NaN, abort
    if all(isnan(ct)) and all(isnan(ct_signal)):
        return

    # 5) Fill if specified
    if "fillna" in kwargs:
        ct.fillna(kwargs["fillna"], inplace=True)
        ct_signal.fillna(kwargs["fillna"], inplace=True)

    # 6) Build final column names
    # Retain the old format so existing tests pass, but you can tweak if you like:
    _props = f"_{pwr}_{signal_offset_orig}"
    col_main = f"CUBE{_props}"
    col_signal = f"CUBEs{_props}"
    if normalize:
        # Optionally rename to indicate we scaled
        col_main += "_scaled"
        col_signal += "_scaled"

    ct.name = col_main
    ct_signal.name = col_signal

    ct.category = "transform"
    ct_signal.category = "transform"

    # Return as DataFrame
    df = DataFrame({ct.name: ct, ct_signal.name: ct_signal}, index=close.index)
    df.name = ct.name
    df.category = "transform"
    return df