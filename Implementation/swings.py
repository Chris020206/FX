"""swings.py — ATR-based ZigZag structural point detection.

Implements: Detection_Methods/ATR_Swing_Detection.md
  swing_threshold = k * ATR(n), k=1.5, n=14, Wilder's smoothing.
  A new provisional extremum is marked when price moves swing_threshold beyond the most recent
  confirmed extremum in the opposite direction; it confirms when price reverses by
  swing_threshold again. The most recent point is always PROVISIONAL.

Output: list of dicts {index, time, price, kind: HIGH|LOW, state: CONFIRMED|PROVISIONAL}
"""
import pandas as pd

K_MULT = 1.5  # model_version: ATR_Swing_Detection.md


def detect_swings(df: pd.DataFrame, atr: pd.Series, k: float = K_MULT) -> list:
    highs, lows, times = df["high"].values, df["low"].values, df["time"].values
    n = len(df)
    pts = []
    # seed: direction unknown; track running extremes until first threshold move
    trend = 0  # +1 rising leg (tracking a high), -1 falling leg (tracking a low)
    ext_i = 0
    for i in range(1, n):
        thr = atr.iloc[i] * k
        if pd.isna(thr):
            # before ATR warm-up, still track extremes
            if highs[i] >= highs[ext_i] and lows[i] <= lows[ext_i]:
                ext_i = i
            elif highs[i] > highs[ext_i] and trend >= 0:
                ext_i = i
            elif lows[i] < lows[ext_i] and trend <= 0:
                ext_i = i
            continue
        if trend == 0:
            if highs[i] >= lows[ext_i] + thr:
                trend, ext_i = 1, i
            elif lows[i] <= highs[ext_i] - thr:
                trend, ext_i = -1, i
            else:
                if highs[i] > highs[ext_i]:
                    ext_i = i if highs[i] > highs[ext_i] else ext_i
                if lows[i] < lows[ext_i]:
                    ext_i = i
            continue
        if trend == 1:
            if highs[i] > highs[ext_i]:
                ext_i = i
            elif lows[i] <= highs[ext_i] - thr:
                pts.append({"index": ext_i, "time": int(times[ext_i]), "price": float(highs[ext_i]),
                            "kind": "HIGH", "state": "CONFIRMED"})
                trend, ext_i = -1, i
        else:
            if lows[i] < lows[ext_i]:
                ext_i = i
            elif highs[i] >= lows[ext_i] + thr:
                pts.append({"index": ext_i, "time": int(times[ext_i]), "price": float(lows[ext_i]),
                            "kind": "LOW", "state": "CONFIRMED"})
                trend, ext_i = 1, i
    # trailing provisional point
    if trend != 0:
        pts.append({"index": ext_i, "time": int(times[ext_i]),
                    "price": float(highs[ext_i] if trend == 1 else lows[ext_i]),
                    "kind": "HIGH" if trend == 1 else "LOW", "state": "PROVISIONAL"})
    return pts
