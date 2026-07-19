"""validate_tier1.py — score the detector against the 12 v3 labels.

Gate (pre-committed): on the 9 FULL_5M examples, >=7 exact-bounds matches to proceed.
T1-010 (REFINED_HTF_PUSH) is expected to fail: no detection rule exists for that zone type.
T1-003 should produce NO qualifying candidate (INVALID).
T1-004/T1-003 are WIDENED_15M: detector may find the 5m origin candle; bounds will differ.
"""
import datetime
import pandas as pd
from core import load_csv, atr_wilder
from swings import detect_swings
from detect import detect_origin_points

CSV = "../DATASET/csv/Tier 1/FX_GBPJPY, 5m, 24 may - 13 july.csv"

# lid, date, dir, v3 lower, v3 upper, zone_type, v3 origin time UTC (HH:MM)
LABELS = [
    ("T1-001", "2026-07-10", "SELL", 217.022, 217.090, "FULL_5M", "13:40"),
    ("T1-002", "2026-07-09", "BUY", 217.408, 217.505, "FULL_5M", "13:40"),
    ("T1-003", "2026-07-07", "SELL", 216.735, 216.818, "WIDENED_15M", "11:45"),
    ("T1-004", "2026-07-06", "BUY", 216.595, 216.744, "WIDENED_15M", "13:45"),
    ("T1-005", "2026-07-03", "BUY", 215.222, 215.292, "FULL_5M", "14:20"),
    ("T1-006", "2026-06-29", "BUY", 214.180, 214.369, "FULL_5M", "14:15"),
    ("T1-007", "2026-06-25", "BUY", 213.268, 213.356, "FULL_5M", "13:55"),
    ("T1-008", "2026-06-18", "BUY", 212.877, 212.994, "FULL_5M", "14:10"),
    ("T1-009", "2026-06-10", "SELL", 215.089, 215.170, "FULL_5M", "14:10"),
    ("T1-010", "2026-06-03", "BUY", 214.721, 214.848, "REFINED_HTF_PUSH", "14:50"),
    ("T1-011", "2026-06-02", "BUY", 215.251, 215.323, "FULL_5M", "14:20"),
    ("T1-012", "2026-05-28", "BUY", 213.818, 213.882, "FULL_5M", "14:00"),
]


def main():
    df = load_csv(CSV)
    atr = atr_wilder(df)
    sw = detect_swings(df, atr)
    ops = detect_origin_points(df, atr, sw)
    print(f"bars={len(df)}  swings={len(sw)}  origin_points={len(ops)}")

    # index origin points by UTC date
    by_date = {}
    for op in ops:
        d = datetime.datetime.utcfromtimestamp(op["origin_time"]).date().isoformat()
        by_date.setdefault(d, []).append(op)

    # label-side check first: does the candle at v3 origin time have the v3 bounds?
    tmap = {int(r.time): (r.low, r.high) for r in df.itertuples()}

    full5, exact, tick = 0, 0, 0
    print(f"\n{'ID':7s} {'type':16s} {'label-candle':12s} {'detected@time':>13s} {'bounds':>7s}  detail")
    print("=" * 100)
    for lid, date, d, vlo, vup, zt, hm in LABELS:
        day = datetime.datetime.fromisoformat(date + "T" + hm + ":00+00:00")
        ts = int(day.timestamp())
        lc = tmap.get(ts)
        label_ok = lc is not None and abs(lc[0] - vlo) < 1e-9 and abs(lc[1] - vup) < 1e-9
        cands = by_date.get(date, [])
        hit = next((op for op in cands if op["origin_time"] == ts and op["direction"] == d), None)
        near = None
        if hit is None:
            near = min(cands, key=lambda op: abs(op["origin_time"] - ts), default=None)
        if zt == "FULL_5M":
            full5 += 1
        status = "MISS"
        detail = ""
        if hit:
            blo, bup = hit["lower_bound"], hit["upper_bound"]
            if abs(blo - vlo) < 1e-9 and abs(bup - vup) < 1e-9:
                status = "EXACT"
                if zt == "FULL_5M":
                    exact += 1
            elif abs(blo - vlo) <= 0.011 and abs(bup - vup) <= 0.011:
                status = "TICK"
                if zt == "FULL_5M":
                    tick += 1
            else:
                status = "TIME-ONLY"
                detail = f"got [{blo:.3f},{bup:.3f}] want [{vlo:.3f},{vup:.3f}]"
        elif near:
            dt_min = (near["origin_time"] - ts) / 60
            detail = f"nearest cand {dt_min:+.0f}min dir={near['direction']} [{near['lower_bound']:.3f},{near['upper_bound']:.3f}]"
        else:
            detail = "no candidates that day"
        print(f"{lid:7s} {zt:16s} {'ok' if label_ok else 'MISMATCH':12s} {status:>13s} {'':>7s}  {detail}")

    fp_days = {}
    for dd, ops_d in by_date.items():
        fp_days[dd] = len(ops_d)
    counts = pd.Series(fp_days)
    print(f"\nFULL_5M exact: {exact}/{full5}   within-1-tick extra: {tick}")
    print(f"candidates/day over {len(counts)} active days: mean {counts.mean():.1f}, max {counts.max()}")
    print("\nGATE (>=7/9 FULL_5M exact):", "PASS" if exact >= 7 else "FAIL")


if __name__ == "__main__":
    main()
