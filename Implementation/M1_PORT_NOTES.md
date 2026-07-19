# M1 Port Notes — Pine v2.2 → Python

Date: 2026-07-19. Branch: `M1—port-the-pine-detector-to-python`
(NEXT_STEP.md names `m1-detection-port`; the repo owner requested this name instead).

## Files

| File | Role |
|---|---|
| `pine_port.py` | Line-by-line port of `Detection_Methods/order_blocks_v2 (26.07.17).pine`. Comments reference Pine line numbers. |
| `run_pine_port.py` | Runner: Tier 1 CSV in, box list + gate numbers out. Refuses Tier 2/3 paths. |
| `output/pine_port_boxes.csv` | Every box the port created on the gate file, one row each, for box-by-box comparison against TradingView. |

Everything behavioral is carried: pivot detection (K=2), min-zone gate (0.75×ATR),
impulse gate (1.5×ATR close-to-extreme within 3 bars), pending candidates,
dual-tagged rejection, stacked backfill (off, but implemented), the Variation 2
path with strict `actEdge` activation, wick activation, wick mitigation at 25%
fill, same-bar mitigation guard, per-side 30-box cap, day-boundary cleanup,
3 h max-age cleanup, and the Europe/London windows. Display-only constructs
(colors, borders, `box.set_right`, `extendBars`, alerts) are dropped; the
visibility pass is kept only to record the "shown in display window" flag that
the 3.2/day metric counts.

## Semantics the Pine source does not spell out — decisions taken, to verify at gate time

1. **`ta.pivothigh/pivotlow` tie handling.** Implemented as a *strict* extreme on
   both sides (an exactly-equal high/low within K bars on either side rejects the
   pivot). TradingView does not document tie behavior precisely. If the
   TradingView comparison shows mismatches, check the mismatched bars for
   equal-extreme neighbors first.
2. **`ta.atr(14)` seeding.** RMA (Wilder), seeded with the SMA of the first 14
   true ranges, NaN before bar 14; first bar's TR is high−low. NaN ATR makes the
   zone/impulse gates reject, mirroring Pine's na-comparison-is-false semantics.
   Only affects the first 14 bars of the file (May 24, out of any window).
3. **Session boundaries.** Bar open time in `[start, end)` — end-exclusive on
   open times, taken from the v2Window tooltip ("1605 is needed to include the
   candle opening at 16:00"). Applied to both windows.
4. **Timestamps.** CSV is epoch seconds; Pine `time` is ms. The 3 h age bound is
   compared in seconds. Day boundary is calendar day in Europe/London (Pine uses
   `sessionTZ` because `useSessionFilter` is on).
5. **Execution order** preserved exactly: V2 detection → pending re-check →
   pivot creation → activation/mitigation (bull then bear) → day cleanup → age
   cleanup → visibility, once per bar on bar-close values.

## Self-run on the gate file (gate steps 1 and 4)

`DATASET/csv/Tier 1/FX_GBPJPY, 5m, 24 may - 13 july.csv` — 10,307 bars, 36 days
with display-window bars.

- Boxes created: 980 (530 bull / 450 bear, 38 with the isV2 origin-timing flag)
- Shown in display window: 118 → **3.28/day** (Pine header reference ~3.20 on its
  ~30k-candle calibration span; gate hard bound <10/day — passed)
- Max on a single day: 7

## Recall vs `main_Tier_1_Examples_v3.xlsx` (reported, NOT the gate)

9/9 FULL_5M labels reproduced with exact origin bar, exact bounds, correct
direction (T1-001, -002, -005, -006, -007, -008, -009, -011, -012). T1-008
arrives via the pending/delayed-gate path. Out of detector scope by
construction: T1-003, T1-004 (WIDENED_15M — the Pine builds single-candle 5m
zones only, per its own mitigation tooltip) and T1-010 (REFINED_HTF_PUSH;
labelled "Detector origin detected: NO").

## Gate status — pre-committed gate NOT yet passed

| Step | Status |
|---|---|
| 1. Run on the Tier 1 span | DONE |
| 2–3. Box-by-box match vs Pine on TradingView | **BLOCKED — needs the trader to run the Pine on the same span and supply its boxes** (`output/pine_port_boxes.csv` is the comparison artifact; mismatches to be enumerated individually) |
| 4. ~3.2/day, hard bound <10/day | DONE — 3.28/day |
| 5. Label recall reported, not gated | DONE — 9/9 FULL_5M |

## Flagged, not changed (per NEXT_STEP.md scope rule)

Nothing in the Pine logic looked wrong during translation. The two verification
points above (pivot ties, session boundary) are uncertainties in *TradingView's*
semantics, not suspected defects in the Pine.

## Open questions for the trader (pre-committed in NEXT_STEP.md)

1. **Label set.** The Pine header cites 13 labelled OB events / 17 known
   examples (including a Jun 11 Variation-2 case); `main_Tier_1_Examples_v3.xlsx`
   has 12 rows and no Jun 11 row. Which set is authoritative for M1 reporting?
2. **Repo hygiene discrepancy — RESOLVED 2026-07-19.** `CHANGES_2026-07-19.md`
   Addendum 3 recorded Tier 3, `dataset main - repaired.csv` and the old
   `candidates_tier1_full.csv` as deleted, but the deletions were never
   committed. The repo owner moved Tier 3 out of the local folder and
   authorised the commit; all five files are now removed from git. Tier 3 is
   physically absent, as `Standards/Decision_Log.md` requires.
