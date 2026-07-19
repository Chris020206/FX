"""core.py — data loading and ATR.

Implements: ATR per Detection_Methods/ATR_Swing_Detection.md
  - period 14, Wilder's smoothing
All timestamps UTC (raw UNIX in CSVs). Never open CSVs in a spreadsheet app.
"""
import pandas as pd
import numpy as np

ATR_PERIOD = 14  # model_version: per ATR_Swing_Detection.md, Status: Approved


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns=str.lower)[["time", "open", "high", "low", "close"]].copy()
    df["time"] = df["time"].astype(np.int64)
    df = df.sort_values("time").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df


def atr_wilder(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    """True range with Wilder's smoothing (RMA). First `period` values are a simple mean seed."""
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    prev_c = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    atr = np.full(len(tr), np.nan)
    if len(tr) < period:
        return pd.Series(atr, index=df.index)
    atr[period - 1] = tr[:period].mean()
    alpha_keep = (period - 1) / period
    for i in range(period, len(tr)):
        atr[i] = atr[i - 1] * alpha_keep + tr[i] / period
    return pd.Series(atr, index=df.index)
