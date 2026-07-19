"""detect.py — origin point detection, v2 (empirically corrected).

DIVERGENCE FROM SPEC (documented, see VALIDATION_REPORT.md):
Origin_Point_Detection.md selects the last candle *before* the impulse whose close is on the
swept side of an ATR-swing-anchored pool. The 12 Tier 1 labels do something different and
simpler: the origin candle IS the extremum candle — the candle whose wick takes out the prior
running extreme — regardless of its own close color (T1-006 is bullish). Swept references are
running intraday extremes a few bars back, far shallower than k=1.5 ATR swing points.

Rule implemented (BUY case; SELL mirrors):
  bar i is an origin candidate iff
    1. low[i] < min(low[i-W .. i-1])          -- takes out the prior W-bar running low
    2. low[i] == min(low[i-W .. i+3])         -- it is THE extreme; no lower low in the
                                                 displacement window (origin closest to impulse)
    3. max(high[i+1 .. i+3]) - low[i] >= K_DISP * ATR[i]   -- qualifying displacement
    4. some close in [i .. i+3] > min(low[i-W .. i-1])     -- price closes back above the
                                                              swept reference (sweep, not break)
  zone = [low[i], high[i]] wick-to-wick  (FULL_5M)

W (reference lookback) is a declared calibration parameter, swept over {6,12,24,48} in
validation — Tier 1 IS the calibration set; tuning here is by design and reported openly.
K_DISP = 1.5 (same k as ATR Swing Detection, per Origin_Point_Detection.md rule 2).
DELIBERATE OMISSION: Efficient Price 4H+ precondition not applied (circular dependency;
see Event_Model.md).
"""
import numpy as np
import pandas as pd

K_DISP = 1.5
DISP_BARS = 3


def detect_origin_points(df: pd.DataFrame, atr: pd.Series, lookback: int = 12) -> list:
    o, h, l, c, t = (df[x].values for x in ("open", "high", "low", "close", "time"))
    n = len(df)
    a = atr.values
    out = []
    for i in range(lookback, n - DISP_BARS):
        if np.isnan(a[i]):
            continue
        need = a[i] * K_DISP
        # ---- BUY: sweep of lows
        ref = l[i - lookback:i].min()
        if l[i] < ref and l[i] <= l[i + 1:i + 1 + DISP_BARS].min():
            disp = h[i + 1:i + 1 + DISP_BARS].max() - l[i]
            closed_back = (c[i:i + 1 + DISP_BARS] > ref).any()
            if disp >= need and closed_back:
                out.append({"direction": "BUY", "origin_index": i, "origin_time": int(t[i]),
                            "lower_bound": float(l[i]), "upper_bound": float(h[i]),
                            "swept_ref": float(ref), "zone_type": "FULL_5M",
                            "detection_method": "displacement_based"})
        # ---- SELL: sweep of highs
        ref_h = h[i - lookback:i].max()
        if h[i] > ref_h and h[i] >= h[i + 1:i + 1 + DISP_BARS].max():
            disp = h[i] - l[i + 1:i + 1 + DISP_BARS].min()
            closed_back = (c[i:i + 1 + DISP_BARS] < ref_h).any()
            if disp >= need and closed_back:
                out.append({"direction": "SELL", "origin_index": i, "origin_time": int(t[i]),
                            "lower_bound": float(l[i]), "upper_bound": float(h[i]),
                            "swept_ref": float(ref_h), "zone_type": "FULL_5M",
                            "detection_method": "displacement_based"})
    return out


def widen_15m(df: pd.DataFrame, origin_index: int) -> tuple:
    """WIDENED_15M construction: the three 5m bars of the enclosing 15m bracket."""
    t0 = int(df["time"].iloc[origin_index])
    bracket_start = t0 - (t0 % 900)
    m = (df["time"] >= bracket_start) & (df["time"] < bracket_start + 900)
    seg = df[m]
    return float(seg["low"].min()), float(seg["high"].max())
