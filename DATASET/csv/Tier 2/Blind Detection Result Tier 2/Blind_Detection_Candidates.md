<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: SUPERSEDED**
>
> - VOID as a scoring artifact. This scan was produced before the v3 corrections, under the earlier thresholds and the earlier REFINED_15M naming, and before the four research flags were opened.
> - Tier 2 blind validation requires a frozen ruleset. Rules are not frozen. Re-run after the research flags are closed; do not score these 38 candidates.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Blind Detection Results — 3:50 Scalp Candidates (Held-Out Data)

**Dataset**: GBP/JPY 5m, 2025-07-13 → 2026-02-13 (43,442 candles, zero overlap with calibration data)
**Detection basis**: Origin Point Detection + Mitigation (fill_ratio ≥ 25%, wick-to-wick zones),
3:50 window filter (mitigation 15:35–16:20 UK for variation 1; origin formation 15:40–16:00 UK for
variation 2), intraday-only, BST/GMT transition handled (Oct 26, 2025).
**Context**: the origin+mitigation pattern alone matched 626 times across the dataset; the time
window filter reduced it to these 38.

All times UK. "Var" = variation: 1 = origin formed earlier, mitigated in-window; 2 = origin formed
in-window, mitigated later same day.

## How to cross-reference
For each row, mark the **Your verdict** column with one of:
- **MATCH** — corresponds to a real setup you'd marked (note time differences if any)
- **NEAR** — right day/setup, but my times/zone are off from yours (please note yours)
- **FP** — false positive, not a real setup by your read
- Leave blank if unsure / needs a closer look

Then list any **missed setups** (known-good dates NOT on this list) in the section at the bottom —
those are the most valuable results of this whole test.

| # | Date        | Var | Direction | Origin (OB) |       Origin Zone |    Mitigation | Fill | Your verdict + notes |
|---|-------------|-----|-----------|-------------|-------------------|---------------|------|----------------------|
| 1 | 2025-07-17  |  1  |   bearish |       15:10 | 199.065 – 199.181 |         15:40 | 0.72 | FP: 15:10 is not a valid OB. However, notice 15:25 OB which is mitigated at 16:00|
| 2 | 2025-07-18  |  1  |   bullish |       07:00 | 199.493 – 199.582 |         16:00 | 0.36 | FP: Personally, i do not find a setup on this date at all.|
| 3 | 2025-07-29  |  1  |   bullish |       14:45 | 197.826 – 197.975 |         15:35 | 0.51 | Match: Origin (OB) at 14:50, Mitigation at 15:50|
| 4 | 2025-08-08  |  1  |   bearish |       12:10 | 198.703 – 198.807 |         16:20 | 0.26 | FP: Not a valid OB. If anything, OB at 15:50, and Mitigation at 15:45|
| 5 | 2025-08-11  |  1  |   bullish |       15:40 | 198.376 – 198.444 |         16:20 | 0.49 | Match: Origin (OB) at 15:45, Mitigation at 16:25|
| 6 | 2025-08-13  |  1  |   bullish |       09:50 | 199.549 – 199.646 |         16:05 | 1.06 | Bland: Reason being, detection of relevant candles is correct, however, note Fill value < 1 meaning mitigation exceeds OB |
| 7 | 2025-08-25  |  1  |   bullish |       14:55 | 198.988 – 199.092 |         15:55 | 0.28 | FP: Simply incorrect.|
| 8 | 2025-09-03  |  2  |   bullish |       16:00 | 198.972 – 199.053 |         16:25 | 0.52 | FP: Simply incorrect.|
| 9 | 2025-09-12  |  1  |   bearish |       15:25 | 200.274 – 200.340 |         16:05 | 0.58 | FP: Simply incorrect.|
| 10 | 2025-09-15 |  1  |   bearish |       15:25 | 200.384 – 200.435 |         15:55 | 0.67 | Match: But loss. |
| 11 | 2025-09-18 |  1  |   bullish |       14:50 | 200.517 – 200.706 |         15:35 | 0.59 | FP: Simply incorrect.|
| 12 | 2025-09-22 |  1  |   bullish |       13:00 | 199.390 – 199.570 |         16:00 | 0.35 | Match:|
| 13 | 2025-09-24 |  1  |   bearish |       13:25 | 199.973 – 200.002 |         15:45 | 1.21 | |
| 14 | 2025-10-08 |  1  |   bullish |       14:05 | 204.547 – 204.658 |         15:55 | 0.34 | |
| 15 | 2025-10-10 |  1  |   bullish |       11:55 | 202.533 – 202.706 |         16:00 | 0.57 | |
| 16 | 2025-10-23 |  1  |   bullish |       06:40 | 203.199 – 203.275 |         16:00 | 0.29 | |
| 17 | 2025-10-31 |  1  |   bullish |       12:35 | 201.849 – 202.096 |         15:50 | 0.42 | |
| 18 | 2025-11-04 |  1  |   bullish |       14:45 | 200.005 – 200.118 |         15:50 | 0.50 | |
| 19 | 2025-11-05 |  2  |   bearish |       15:55 | 201.129 – 201.233 |         16:25 | 0.46 | |
| 20 | 2025-11-06 |  1  |   bullish |       15:00 | 200.510 – 200.749 |         15:35 | 0.75 | |
| 21 | 2025-11-07 |  1  |   bearish |       14:20 | 201.420 – 201.594 |         15:55 | 0.45 | |
| 22 | 2025-11-11 |  1  |   bearish |       14:55 | 202.844 – 202.994 |         15:55 | 0.30 | |
| 23 | 2025-11-17 |  2  |   bearish |       15:55 | 204.354 – 204.512 |         16:30 | 0.47 | |
| 24 | 2025-12-02 |  1  |   bullish |       15:25 | 205.808 – 205.936 |         15:50 | 0.95 | |
| 25 | 2025-12-05 |  1  |   bullish |       14:50 | 207.104 – 207.168 |         15:40 | 0.61 | |
| 26 | 2025-12-09 |  1  |   bearish |       08:55 | 208.582 – 208.711 |         15:55 | 0.33 | |
| 27 | 2025-12-10 |  2  |   bullish |       16:00 | 208.329 – 208.445 |         16:30 | 0.41 | |
| 28 | 2025-12-16 |  1  |   bearish |       13:30 | 207.675 – 207.924 |         16:00 | 0.36 | |
| 29 | 2025-12-23 |  2  |   bullish |       15:40 | 210.578 – 210.657 |         17:10 | 0.38 | |
| 30 | 2025-12-24 |  2  |   bearish |       15:45 | 210.381 – 210.468 |         16:25 | 0.36 | |
| 31 | 2025-12-29 |  1  |   bullish |       08:00 | 210.429 – 210.523 |         15:55 | 0.56 | |
| 32 | 2026-01-07 |  1  |   bearish |       15:30 | 211.216 – 211.309 |         16:15 | 0.44 | |
| 33 | 2026-01-09 |  1  |   bearish |       15:25 | 211.934 – 212.008 |         16:20 | 0.55 | |
| 34 | 2026-01-20 |  1  |   bearish |       10:35 | 212.812 – 212.907 |         15:40 | 0.25 | |
| 35 | 2026-01-26 |  1  |   bearish |       06:10 | 210.772 – 210.897 |         15:55 | 0.61 | |
| 36 | 2026-01-30 |  1  |   bullish |       13:25 | 211.848 – 211.935 |         15:50 | 0.59 | |
| 37 | 2026-02-10 |  2  |   bullish |       15:40 | 210.619 – 210.784 |         17:05 | 0.43 | |
| 38 | 2026-02-13 |  2  |   bullish |       15:45 | 208.259 – 208.439 |         20:25 | 0.56 | |

## Missed setups (known-good dates NOT on the list above)
List each here with date, direction, your origin time/zone, and mitigation time — these tell us
exactly where the documented rules diverge from what your eyes do:

-
-
-

## Notes / anything else observed while cross-referencing

-
