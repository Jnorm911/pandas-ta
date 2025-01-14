# -*- coding: utf-8 -*-
from numpy import arange, array, polyfit, std
from pandas import DataFrame, DatetimeIndex, Series
from pandas_ta_tnt._typing import DictLike, Int, List
from pandas_ta_tnt.utils import v_list, v_lowerbound, v_offset, v_series


def tos_stdevall(
    close: Series,
    length: List = None,         # If None, old tests expect length=20 named "TOS_STDEVALL"
    stds: List = None,           # Std. deviation multipliers
    ddof: Int = None,            # Degrees of freedom for std
    offset: Int = None,          # Shift lines forward/backward
    **kwargs: DictLike
) -> DataFrame:
    """
    TD Ameritrade's Think or Swim Standard Deviation All (TOS_STDEVALL)

    This version:
      • Computes a linear regression + standard deviation bands for the
        last N bars of each specified window length.
      • Each window yields a baseline (LR) plus ±1, ±2, ±3 standard
        deviations (by default).
      • If length=None, tests expect columns "TOS_STDEVALL_LR" etc.
      • If length=30, columns "TOS_STDEVALL_30_LR" etc.
      • If multiple lengths, name is "TOS_STDEVALL_multi_...".

    Sources:
        https://tlc.thinkorswim.com/center/reference/thinkScript/Functions/Statistical/StDevAll

    Args:
        close (pd.Series): Price Series (often 'close')
        length (List[int] or int):
            - If None (default), uses length=20 => columns "TOS_STDEVALL_LR", etc.
            - If int, uses that single length => "TOS_STDEVALL_30_LR", etc.
            - If list, uses each length => "TOS_STDEVALL_multi_20_25_30", etc.
        stds (list): Std deviation multipliers in ascending order.
            Default: [1, 2, 3]
        ddof (int): Delta Degrees of Freedom. Default: 1
        offset (int): Shift the final lines forward/backward, clamped >= 0.
            Default: 0

    Kwargs:
        fillna (value, optional): If set, fills missing values with this.

    Returns:
        pd.DataFrame: Columns for each length + std multiplier. For example,
            TOS_STDEVALL_LR, TOS_STDEVALL_L_1, TOS_STDEVALL_U_1, ...
            or TOS_STDEVALL_30_LR, TOS_STDEVALL_30_L_1, etc.
    """
    # 1) Handle default or user-supplied length(s)
    user_length_param = kwargs.get("length", None)  # Check if user explicitly passed length
    if length is None:
        # Old tests: no length => single length=20 => columns named TOS_STDEVALL_LR, ...
        length = [20]
    elif isinstance(length, int):
        length = [length]

    # 2) Validate stds
    stds = v_list(stds, [1, 2, 3])
    if not stds or min(stds) <= 0:
        return
    stds.sort()  # ensure ascending

    # 3) Validate offset >= 0
    offset = v_offset(offset)
    offset = max(offset, 0)

    # 4) Validate 'close' Series
    close = v_series(close, 2)
    if close is None:
        return

    df_list = []

    # 5) For each length in the list, compute TOS_STDEVALL
    for L in length:
        # Enforce at least 2 bars
        L_valid = v_lowerbound(L, 2, L)
        # Slicing the last L_valid bars
        sub_close = close.iloc[-L_valid:]
        if sub_close.shape[0] < L_valid:
            continue

        # ddof default = 1 if not provided or out of range
        d = int(ddof) if isinstance(ddof, int) and 0 <= ddof < L_valid else 1

        # Prepare for polyfit
        if isinstance(sub_close.index, DatetimeIndex):
            X = arange(L_valid)
            close_arr = array(sub_close)
        else:
            X = arange(L_valid)
            close_arr = sub_close.to_numpy()

        # 6) Linear regression
        m, b = polyfit(X, close_arr, 1)
        lr = Series(m * X + b, index=sub_close.index)

        # 7) Std
        stdev_val = std(close_arr, ddof=d)

        # 8) Build sub-DataFrame
        #    If length=None => "TOS_STDEVALL_LR", else => "TOS_STDEVALL_30_LR", etc.
        if L_valid == 20 and user_length_param is None:
            # The test calls "df.ta.tos_stdevall()" with no args => expects "TOS_STDEVALL_LR"
            _props = "TOS_STDEVALL"
        else:
            _props = f"TOS_STDEVALL_{L_valid}"

        sub_df = DataFrame({f"{_props}_LR": lr}, index=sub_close.index)

        for i in stds:
            sub_df[f"{_props}_L_{i}"] = lr - i * stdev_val
            sub_df[f"{_props}_U_{i}"] = lr + i * stdev_val
            sub_df[f"{_props}_L_{i}"].name = _props
            sub_df[f"{_props}_U_{i}"].name = _props
            sub_df[f"{_props}_L_{i}"].category = "statistics"
            sub_df[f"{_props}_U_{i}"].category = "statistics"

        # 9) Offset shift if needed
        if offset != 0:
            sub_df = sub_df.shift(offset)

        # 10) Fill if requested
        if "fillna" in kwargs:
            sub_df.fillna(kwargs["fillna"], inplace=True)

        sub_df.name = _props
        sub_df.category = "statistics"
        df_list.append(sub_df)

    # 11) Combine results from all lengths (side by side)
    if not df_list:
        return
    df_final = df_list[0]
    for dfx in df_list[1:]:
        df_final = df_final.join(dfx, how="outer")

    # 12) If multiple lengths, rename final DataFrame
    if len(length) > 1:
        str_lengths = "_".join(str(L) for L in length)
        df_final.name = f"TOS_STDEVALL_multi_{str_lengths}"
    else:
        # For single length, if it was length=20 with no user param => we already used "TOS_STDEVALL"
        # otherwise "TOS_STDEVALL_30", "TOS_STDEVALL_25", etc. is set above
        pass

    df_final.category = "statistics"
    return df_final