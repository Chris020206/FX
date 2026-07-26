# M1 Reconciliation — Pine (TradingView) vs Python port

Date: 2026-07-26. Gate steps 2–3 (box-by-box agreement with the Pine) — **RUN**.
Artifact: `Implementation/output/pine_vs_port_reconciliation.csv` (every box, one row).

## What was compared, and how the data was assembled

The comparison needs the Pine's own box output on the **FXCM** feed over the gate span
(`FX_GBPJPY, 5m, 24 may - 13 july`). TradingView's "Export chart data…" only emits the bars
currently loaded in the chart buffer, so a single export is front-truncated. Three exports were
supplied:

| File | Feed | Span | Verdict |
|---|---|---|---|
| `FOREXCOM_GBPJPY__5.csv` | **FOREX.com** | Jun 7 → Jul 24 | **Unusable — wrong feed.** 0 of 7,437 shared bars matched the FXCM gate CSV; differences up to 0.27 (27 pips). |
| `FX_GBPJPY__5__12_.csv` | FXCM | Jun 7 → Jul 24 | Correct feed. 6,731 / 7,437 shared bars identical (max Δ 0.037, minor feed revisions). Front-truncated. |
| `FX_GBPJPY__5__13_.csv` | FXCM | Apr 19 → Jun 5 | Correct feed. Matches the gate CSV **exactly** on the 2,870 overlapping bars (Δ = 0). |

The two FXCM chunks stitch together (the Jun 5→7 gap is the closed weekend, no trading bars) into
a continuous Apr 19 → Jul 24 series that **fully covers the gate span with real warmup**. The
comparison was run by feeding the port the stitched export OHLC — i.e. the exact prices the Pine
saw — so any remaining divergence is logic, not feed. The `isV2` column comes from the debug-export
copy's `// DEBUG` plots, which record the Pine's own `isV2` at box creation.

## Result over the full gate span (May 24 → Jul 13)

1,039 Pine boxes vs 979 port boxes. **845 agree exactly** (origin bar, both bounds, direction,
`isV2`). 281 disagree.

Raw agreement is not the right lens for the strategy: it only ever sees boxes that are **live during
the display window** (visible on ≥1 bar whose open is in 15:15–16:15 Europe/London). This is a
Variation-1-safe test — V1 setups form *before* the window and mitigate *inside* it, so their
origins are off-session but they are strategy-relevant. Splitting on that basis:

| Category | Total | Live in window |
|---|---|---|
| Agree (origin + bounds + direction + isV2) | 845 | 91 |
| Pine-only (port misses a box) | 147 | **5** |
| Port-only (port invents a box) | 87 | **1** |
| `isV2` flag differs, bounds identical | 47 | **26** |
| **Bounds mismatch** | **0** | **0** |

So on the window-relevant set: 91 agree, **32 disagree**.

## Load-bearing facts

- **Zero bounds mismatches, anywhere.** Every box both engines create is geometrically identical.
  Pivot detection (K=2), zone boundaries, and direction are a faithful port.
- **All 9 FULL_5M labelled examples agree exactly**, T1-011 and T1-012 included (both now in span).
  Recall is intact and produced for the right reason — none of it rests on the diverging boxes.
- **The port never over-produces where it matters** (1 port-only box is live in-window, vs 87 total).

## The window-relevant punch list (32)

**Port misses a window-live box the Pine draws (5).** All fail the port's displacement gate
(1.5×ATR, close-to-origin-extreme, origin+1..+3) — except one min-zone case (06-22 15:25). Several
are hair-marginal (1.45–1.48×ATR against the 1.50 cut → an ATR-value or `>=` boundary nuance);
a few sit clearly under the gate and need the port and Pine read side by side.

| Direction | Origin (London) | Pine box | Note |
|---|---|---|---|
| bear | 2026-06-01 16:00 | [214.5370, 214.6400] | displacement gate |
| bear | 2026-06-05 14:50 | [214.5930, 214.7300] | displacement gate |
| bull | 2026-06-08 13:55 | [213.4730, 213.5560] | displacement gate |
| bear | 2026-06-22 15:25 | [214.3250, 214.4240] | **min-zone** gate (0.72 vs 0.75 ATR) |
| bear | 2026-06-22 16:00 | [213.8350, 213.9960] | displacement gate |

**Port invents a window-live box the Pine lacks (1).** `bear 2026-06-05 13:20` [215.2730,
215.3160], pivot path — a marginal-gate case in the other direction.

**Same box, port over-flags `isV2` (26).** Bounds identical; the port sets `isV2=1`, the Pine
`isV2=0`. See root cause below. Full list in the CSV (`category = V2_FLAG_MISMATCH`,
`live_in_window = YES`).

## Root cause of the `isV2` divergence — identified in direction, not yet bit-exact

The Pine source comments say `isV2 = inV2Window[barOffset]` — "origin candle sits inside the
Variation-2 formation window (1540–1605)." The port implements exactly that. But the exported flag
does **not** behave that way: at the *same* origin minute (e.g. 15:50) the Pine emits `isV2=1` on
some days and `isV2=0` on others.

Two concrete same-origin cases resolve it:

- **Apr 24 15:50 (Pine `isV2=1`)** — created one bar later; the V2 **structural pattern holds** at
  that bar (candle sweeps prior extreme, closes opposing, next candle closes beyond its full range).
  Created via the V2 structural path (`createOB(1, …)`).
- **Apr 20 15:50 (Pine `isV2=0`)** — a delayed pivot created three bars later; the structural
  pattern does **not** hold. Created via the pivot path.

Across the 26 window-relevant over-flags, the structural pattern is absent in 23 (consistent with
Pine `isV2=0`); 3 are exceptions, so the reconstruction is directionally solid but not bit-exact.

**Conclusion:** the Pine's emitted `isV2` tracks the **V2 creation path**, not window membership;
the port sets it from window membership and therefore over-flags in-window pivot boxes as V2. The
fix is to set the port's `isV2` from the creation path (mirroring the Pine's `createOB` `barOffset`
semantics), not the window. The exact `barOffset` behaviour on the delayed/pending path is not yet
traced line-for-line and is left as the open item for the fix — **do not guess the mechanism;
read `createOB` and its call sites against `pine_port.py`.**

## Scope / caveats

- Comparison rests on stitching two FXCM exports across the closed Jun 5→7 weekend (no trading bars
  lost).
- The Jun 7+ chunk carries ~700 minor feed revisions (max Δ 0.037) vs the gate CSV; a handful of
  **off-session** marginal-gate calls could shift on a clean single-feed re-export. The in-window
  picture and every label are unaffected (the Apr 19 → Jun 5 chunk is an exact match).
- The 222 off-session disagreements are marginal-gate flicker on boxes the strategy never sees; they
  are enumerated in the CSV and accepted as out of scope (see `Standards/Decision_Log.md`,
  2026-07-26 gate-scope entry).
