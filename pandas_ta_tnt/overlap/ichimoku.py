# -*- coding: utf-8 -*-
from pandas import DataFrame, RangeIndex, Timedelta, Series, concat, date_range
from pandas_ta_tnt._typing import DictLike, Int
from pandas_ta_tnt.utils import v_offset, v_pos_default, v_series
from .midprice import midprice


def ichimoku(
    high: Series, low: Series, close: Series,
    tenkan: Int = None, kijun: Int = None, senkou: Int = None,
    include_chikou: bool = True,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Ichimoku Kinkō Hyō (ichimoku)

    By default, Ichimoku shifts the "cloud" lines forward by 'kijun' periods,
    which can expose future data for ML. Setting `lookahead=False` bypasses
    that shift to avoid future leakage. Negative offset is also clamped.

    Sources:
        https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/ichimoku-ich/

    Args:
        high (pd.Series), low (pd.Series), close (pd.Series)
        tenkan (int): Tenkan period. Default: 9
        kijun (int): Kijun period. Default: 26
        senkou (int): Senkou period. Default: 52
        include_chikou (bool): Whether to include chikou component
        offset (int): How many periods to shift results (>= 0)

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        lookahead (bool): If False, no forward shift is applied for the cloud.
            Default: True

    Returns:
        (pd.DataFrame, pd.DataFrame): The visible Ichimoku DataFrame and
            the "forward" Spans DataFrame if `lookahead=True`, else (df, None).
    """
    # Validate
    tenkan = v_pos_default(tenkan, 9)
    kijun = v_pos_default(kijun, 26)
    senkou = v_pos_default(senkou, 52)
    _length = max(tenkan, kijun, senkou)
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)
    if high is None or low is None or close is None:
        return None, None

    offset = v_offset(offset)
    offset = max(offset, 0)  # clamp negative offset
    do_lookahead = kwargs.get("lookahead", True)
    if not do_lookahead:
        include_chikou = False

    # Calculate
    tenkan_sen = midprice(high=high, low=low, length=tenkan)
    kijun_sen = midprice(high=high, low=low, length=kijun)
    span_a = 0.5 * (tenkan_sen + kijun_sen)
    span_b = midprice(high=high, low=low, length=senkou)
    chikou_span = close.shift(-kijun + 1)  # default usage

    if do_lookahead:
        # Standard Ichimoku uses forward shift
        span_a = span_a.shift(kijun - 1)
        span_b = span_b.shift(kijun - 1)
    else:
        # No forward shift to avoid future leakage
        chikou_span = None

    # Offset
    if offset != 0:
        tenkan_sen = tenkan_sen.shift(offset)
        kijun_sen = kijun_sen.shift(offset)
        if do_lookahead:
            span_a = span_a.shift(offset)
            span_b = span_b.shift(offset)
            chikou_span = chikou_span.shift(offset) if chikou_span is not None else None
        else:
            tenkan_sen = tenkan_sen.shift(offset)
            kijun_sen = kijun_sen.shift(offset)

    # Fill
    if "fillna" in kwargs:
        fillval = kwargs["fillna"]
        tenkan_sen.fillna(fillval, inplace=True)
        kijun_sen.fillna(fillval, inplace=True)
        if do_lookahead:
            span_a.fillna(fillval, inplace=True)
            span_b.fillna(fillval, inplace=True)
            if chikou_span is not None:
                chikou_span.fillna(fillval, inplace=True)

    # Name & Category
    span_a.name = f"ISA_{tenkan}"
    span_b.name = f"ISB_{kijun}"
    tenkan_sen.name = f"ITS_{tenkan}"
    kijun_sen.name = f"IKS_{kijun}"
    if chikou_span is not None:
        chikou_span.name = f"ICS_{kijun}"

    ichimokudf = {
        span_a.name: span_a,
        span_b.name: span_b,
        tenkan_sen.name: tenkan_sen,
        kijun_sen.name: kijun_sen,
    }
    if do_lookahead and include_chikou and chikou_span is not None:
        ichimokudf[chikou_span.name] = chikou_span

    ichimokudf = DataFrame(ichimokudf, index=close.index)
    ichimokudf.name = f"ICHIMOKU_{tenkan}_{kijun}_{senkou}"
    ichimokudf.category = "overlap"

    # If lookahead=True, produce a forward Span DataFrame
    spandf = None
    if do_lookahead:
        last = close.index[-1]
        # Attempt to generate forward periods
        _forward_periods = kijun
        # For integer index
        if close.index.dtype == "int64":
            ext_index = RangeIndex(start=last + 1, stop=last + _forward_periods + 1)
        else:
            # fallback
            df_freq = close.index.value_counts().mode()[0]
            tdelta = Timedelta(df_freq, unit="d")
            ext_index = date_range(start=last + tdelta, periods=_forward_periods, freq="B")

        spandf = DataFrame(index=ext_index, columns=[span_a.name, span_b.name])
        # Copy last kijun values for forward plotting
        _span_a = span_a[-kijun:].shift(-1).copy()
        _span_b = span_b[-kijun:].shift(-1).copy()

        _span_a.index = ext_index
        _span_b.index = ext_index
        spandf[span_a.name] = _span_a
        spandf[span_b.name] = _span_b
        spandf.name = f"ICHISPAN_{tenkan}_{kijun}"
        spandf.category = "overlap"

    return ichimokudf, spandf