"""pipeline.py — origin -> activation -> entry, per Rulebook v1.4.

ENTRY SEMANTICS (v1.4, corrected):
  A CROSSING is required: the bar must reach the threshold when the previous post-activation
  bar had not. Mere presence beyond the threshold during the window does NOT trigger.
  The crossing is eligible if it occurs within [window_open - GRACE, window_close].
  Entry is clamped to window_open (a pre-window crossing enters at 15:40, not earlier).

  v1.3 used state semantics ("price beyond threshold during window"), which fired 163 of 291
  candidates at window open on stale breaches. See VALIDATION_REPORT.md §6.

Parameters below are UNVALIDATED (fitted to Tier 1). See PARAMETERS.md.
"""
import datetime, zoneinfo
import pandas as pd

LON = zoneinfo.ZoneInfo("Europe/London")
PIP = 0.01
TOL = 0.3 * PIP          # Rulebook v1.4 4.2, UNVALIDATED
DEPTH_FULL5M = 0.25      # Rulebook v1.4 4.1, FIXED
GRACE_MIN = 5            # Rulebook v1.4 2.4, UNVALIDATED (behavioural, fitted to T1-008)
MAX_ORIGIN_AGE_H = 1.5   # Rulebook v1.4 2.5, UNVALIDATED


def window_bounds_utc(day):
    w0 = datetime.datetime(day.year, day.month, day.day, 15, 40, tzinfo=LON)
    w1 = datetime.datetime(day.year, day.month, day.day, 16, 10, tzinfo=LON)
    return int(w0.timestamp()), int(w1.timestamp())


def run_strategy(df: pd.DataFrame, origin_points: list) -> list:
    o, h, l, c, t = (df[x].values for x in ("open", "high", "low", "close", "time"))
    n = len(df)
    out = []
    for op in origin_points:
        lo, up, d, i0 = op["lower_bound"], op["upper_bound"], op["direction"], op["origin_index"]
        rng = up - lo
        thr = (up - rng * DEPTH_FULL5M + TOL) if d == "BUY" else (lo + rng * DEPTH_FULL5M - TOL)
        day = datetime.datetime.fromtimestamp(int(t[i0]), datetime.timezone.utc).date()
        w0, w1 = window_bounds_utc(day)
        if (w0 - int(t[i0])) / 3600 > MAX_ORIGIN_AGE_H:
            continue
        eligible_from = w0 - GRACE_MIN * 60
        active = False
        prev_hit = False
        entry = None
        cross_i = None
        for i in range(i0 + 1, n):
            if t[i] > w1:
                break
            if not active:
                if (l[i] > up) if d == "BUY" else (h[i] < lo):
                    active = True
                continue
            if (c[i] < lo) if d == "BUY" else (c[i] > up):
                break                       # INVALIDATED before entry
            hit = (l[i] <= thr) if d == "BUY" else (h[i] >= thr)
            if hit and not prev_hit and eligible_from <= t[i] <= w1:
                cross_i = i
                j = i
                while t[j] < w0:            # clamp to window open
                    j += 1
                entry = j
                break
            prev_hit = hit
        if entry is not None:
            out.append({**op, "entry_index": entry, "entry_time": int(t[entry]),
                        "cross_time": int(t[cross_i]), "threshold_price": thr,
                        "pre_window_cross": bool(t[cross_i] < w0)})
    return out
