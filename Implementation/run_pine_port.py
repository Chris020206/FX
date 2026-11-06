"""Run the Pine v2.2 port over a Tier 1 CSV and report the M1 gate inputs.

Usage:
    python Implementation/run_pine_port.py "DATASET/GBPJPY SPOT/Tier 1/FX_GBPJPY, 5m, 24 may - 13 july.csv"

Outputs:
    Implementation/output/pine_port_boxes.csv   — every box the port created,
        with origin bar time (UTC and London), bounds, direction, V2 flag,
        detection path, and lifecycle events, for box-by-box comparison against
        the Pine's TradingView output (gate steps 2-3).
    stdout — in-window boxes/day (gate step 4 sanity bound) and recall against
        the twelve labelled examples (reported, NOT the gate — gate step 5),
        enumerated individually.

Tier discipline: refuses to run on any path containing "Tier 2" or "Tier 3".
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pine_port import Bars, Detector, SESSION_TZ

REPO = Path(__file__).resolve().parent.parent
LABELS_XLSX = REPO / "DATASET" / "GBPJPY SPOT" / "main_Tier_1_Examples_v3.xlsx"
OUT_CSV = Path(__file__).parent / "output" / "pine_port_boxes.csv"


def load_bars(path: Path) -> Bars:
    t, o, h, l, c = [], [], [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            t.append(int(row["time"]))
            o.append(float(row["open"]))
            h.append(float(row["high"]))
            l.append(float(row["low"]))
            c.append(float(row["close"]))
    return Bars(t, o, h, l, c)


def fmt(ts) -> str:
    if ts is None:
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def fmt_london(ts) -> str:
    if ts is None:
        return ""
    return (datetime.fromtimestamp(ts, tz=timezone.utc)
            .astimezone(SESSION_TZ).strftime("%Y-%m-%d %H:%M"))


def load_labels():
    import openpyxl
    wb = openpyxl.load_workbook(LABELS_XLSX, data_only=True)
    ws = wb["Tier 1 Labels"]
    header = [c.value for c in ws[1]]
    labels = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        labels.append(dict(zip(header, row)))
    return labels


def main(csv_path: str) -> None:
    p = Path(csv_path)
    if "tier 2" in str(p).lower() or "tier 3" in str(p).lower():
        sys.exit("REFUSED: tier discipline — this runner does not touch Tier 2/3 data.")

    bars = load_bars(p)
    boxes = Detector(bars).run()

    OUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["direction", "origin_time_utc", "origin_time_london",
                    "top", "bot", "is_v2", "path", "created_time_utc",
                    "activated_time_utc", "removed_reason", "removed_time_utc",
                    "shown_in_display_window"])
        for ob in sorted(boxes, key=lambda x: (x.origin_time, not x.is_bull)):
            w.writerow(["bull" if ob.is_bull else "bear",
                        fmt(ob.origin_time), fmt_london(ob.origin_time),
                        f"{ob.top:.3f}", f"{ob.bot:.3f}",
                        int(ob.is_v2), ob.path, fmt(ob.created_time),
                        fmt(ob.activated_time), ob.removed_reason,
                        fmt(ob.removed_time), int(ob.shown_in_window)])

    # ── summary / gate step 4 ────────────────────────────────────────────────
    days_with_session = set()
    for i in range(bars.n):
        if bars.in_window(i, (15 * 60 + 15, 16 * 60 + 15)):
            days_with_session.add(bars.london_date(bars.t[i]))
    shown_per_day = defaultdict(int)
    for ob in boxes:
        if ob.shown_in_window:
            shown_per_day[bars.london_date(ob.origin_time)] += 1
    n_days = len(days_with_session)
    n_shown = sum(shown_per_day.values())
    v2_count = sum(1 for ob in boxes if ob.is_v2)

    print(f"bars: {bars.n}  span: {fmt(bars.t[0])} .. {fmt(bars.t[-1])} UTC")
    print(f"days with a display-window bar: {n_days}")
    print(f"boxes created: {len(boxes)}  (bull {sum(ob.is_bull for ob in boxes)}, "
          f"bear {sum(not ob.is_bull for ob in boxes)}, isV2 {v2_count})")
    if n_days:
        print(f"boxes shown in display window: {n_shown}  "
              f"=> {n_shown / n_days:.2f}/day  (Pine header reference: ~3.20; "
              f"gate hard bound: <10/day)")
        worst = max(shown_per_day.values(), default=0)
        print(f"max shown on a single day: {worst}")

    # ── recall vs labels — reported, NOT the gate ────────────────────────────
    print("\nRecall vs main_Tier_1_Examples_v3.xlsx (reported per gate step 5; "
          "the gate is agreement with the Pine, not this):")
    by_origin = defaultdict(list)
    for ob in boxes:
        by_origin[ob.origin_time].append(ob)
    for lab in load_labels():
        lid = lab["Label ID"]
        refinement = lab["Zone refinement"]
        hh, mm = str(lab["Origin time UTC+0"]).split(":")
        origin_dt = lab["Date"].replace(hour=int(hh), minute=int(mm),
                                        tzinfo=timezone.utc)
        origin_ts = int(origin_dt.timestamp())
        want_bull = lab["Direction"] == "BUY"
        if refinement != "FULL_5M":
            print(f"  {lid}: OUT OF SCOPE for this detector ({refinement} — the "
                  f"Pine builds single-candle 5m zones only)")
            continue
        match = [ob for ob in by_origin.get(origin_ts, [])
                 if ob.is_bull == want_bull]
        if not match:
            print(f"  {lid}: MISS — no {'bull' if want_bull else 'bear'} box "
                  f"with origin {fmt(origin_ts)} UTC")
            continue
        ob = match[0]
        lo, hi = float(lab["Exact lower bound"]), float(lab["Exact upper bound"])
        bounds_ok = abs(ob.bot - lo) < 1e-6 and abs(ob.top - hi) < 1e-6
        print(f"  {lid}: {'HIT' if bounds_ok else 'HIT origin, BOUNDS DIFFER'} — "
              f"origin {fmt_london(origin_ts)} London, box [{ob.bot:.3f}, "
              f"{ob.top:.3f}] vs label [{lo}, {hi}], path={ob.path}")

    print(f"\nbox list written: {OUT_CSV}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         str(REPO / "DATASET" / "GBPJPY SPOT" / "Tier 1" /
             "FX_GBPJPY, 5m, 24 may - 13 july.csv"))
