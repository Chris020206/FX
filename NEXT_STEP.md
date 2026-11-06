# Next Step

**One unit of work at a time. Short-lived by design — replace this file when the step closes.**
Long-range plan: `ROADMAP.md`.

---

## Current step: M1 — Port the Pine detector to Python

- **Opened:** 2026-07-19
- **Status:** `IN PROGRESS` — port implemented; gate steps 2–3 RUN 2026-07-26 against the
  Pine's TradingView export (full span, real warmup). Gate scoped to window-live boxes
  (Decision Log 2026-07-26); on that set **32 disagreements remain** → not yet passed. Punch
  list below. See `Implementation/RECONCILIATION_M1.md` and `M1_PORT_NOTES.md`.
- **Owner:** Claude Code
- **Branch:** `M1—port-the-pine-detector-to-python` (owner-requested name; was planned as `m1-detection-port`)

### Task
Translate `Detection_Methods/order_blocks_v2 (26.07.17).pine` (373 lines, v2.2) into Python,
line by line. Read the whole file first, tooltips included — they carry the calibration reasoning.

Structures to carry across, all of which the previous failed attempt lacked:

| Element | Pine value |
|---|---|
| Origin detection | `ta.pivothigh/pivotlow`, `pivotK = 2` — extreme within K bars on **both** sides |
| Min zone size | `minZoneATR = 0.75` x ATR(14) at origin |
| Impulse gate | `dispGateATR = 1.5` x ATR(14) at origin, close-to-origin-extreme, within `dispGateBars = 3` |
| Pending candidates | parked when `dispGateBars > pivotK`, re-checked each bar until the window closes |
| Dual-tagged candles | pivot high AND pivot low on one candle -> reject both |
| Stacked backfill | `stackDepth = 0` (off by default) |
| Variation 2 path | in-window sweep of prior extreme, opposing close, next candle closes beyond full range; bypasses pivot + displacement gates; strict `actEdge` activation |
| Activation | Wick beyond zone edge, `activationBufferATR = 0` |
| Mitigation | Wick, `mitigationFillPct = 25` |
| Max age | 3 h; plus same-calendar-day cleanup |
| Windows | display `1515-1615`, V2 formation `1540-1605`, tz `Europe/London` |

### Explicitly out of scope
Improving, simplifying, or "fixing" the detection logic. Anything that looks wrong gets **flagged
in the PR description, not changed**. Also out of scope: entry, exit, and anything touching Tier 2.

### Acceptance gate — pre-committed; SCOPED 2026-07-26 (see Decision Log)
1. Run against `DATASET/GBPJPY SPOT/Tier 1/FX_GBPJPY, 5m, 24 may - 13 july.csv`.
2. Compare boxes against the Pine's output on TradingView over the same span.
3. **Pass:** every **window-live** box matches on origin bar, both bounds, direction, and V2 flag.
   "Window-live" = the box is visible on ≥1 bar whose open is in 15:15–16:15 Europe/London
   (a Variation-1-safe test — origin-in-window is NOT the criterion, since V1 origins are
   off-session). Off-session divergences are enumerated and accepted as out of scope. Any mismatch
   is listed individually with its bar timestamp — never a percentage.
   *(Original gate required agreement on every box including off-session; scoped 2026-07-26 after
   the run — this is scope refinement, not a pass-manufacturing move, and the port does NOT pass
   even the scoped gate yet. Full 281-row enumeration retained in the CSV.)*
4. Emit roughly **3.2 boxes/day** in-window. **If output exceeds ~10/day, the port is wrong** —
   stop and diagnose rather than filtering afterwards. — DONE, 3.28/day.
5. Recall against the twelve labelled examples is reported but is **not** the gate. The gate is
   agreement with the Pine. — All 9 FULL_5M labels agree box-for-box with the Pine.

### Known open question — RESOLVED 2026-07-19
The Pine header cites 13 labelled OB events and 17 known examples;
`main_Tier_1_Examples_v3.xlsx` has 12 rows. **Trader ruling:
`main_Tier_1_Examples_v3.xlsx` is the authoritative label set.**

**Flag (flag only — nothing changed):** the Pine's Variation 2 path was
calibrated including the Jun 11 case, which v3 excludes deliberately. V2's
evidential support is therefore weaker than the Pine header states — its cited
V2 validation rests partly on an example outside the authoritative set. The
detection logic is untouched; this affects how much weight V2 calibration
claims can carry, and belongs in any future V2 re-validation.

### Definition of done
- [x] Whole Pine file read, tooltips included
- [x] Label-set question answered by the trader — v3 xlsx authoritative; V2 evidence flag recorded above
- [x] Port implemented, no inferred logic
- [x] Gate run, result recorded (unadjusted) — steps 1,4,5 done; steps 2–3 run 2026-07-26,
  scoped gate NOT passed (32 window-live disagreements). See `Implementation/RECONCILIATION_M1.md`.
- [x] Divergences from Pine listed individually — `output/pine_vs_port_reconciliation.csv`
- [ ] `ROADMAP.md` M1 row updated *(done 2026-07-26)*
- [ ] Punch list below closed, then re-run gate
- [ ] This file replaced with the next step

### M1 punch list (window-live disagreements to close before M1 is done)
1. **`isV2` over-flag (26 boxes).** Port sets `isV2` from window membership; the Pine sets it from
   the V2 *creation path*. Fix: assign the port's `isV2` from the creation path, mirroring the
   Pine's `createOB` `barOffset` semantics. **Trace `createOB` + its call sites against
   `pine_port.py` first — the exact delayed/pending-path offset is not yet established; do not
   infer it.** Highest-value fix (one root cause, all in-window).
2. **5 missed boxes + 1 invented box.** Marginal displacement-gate (1.5×ATR) cases, one min-zone
   (0.75×ATR). Read the port's gate arithmetic against the Pine for the four non-marginal ones
   (06-05 14:50, 06-08 13:55, and the two 06-22); the rest are `>=`/ATR-seeding boundary nuances.
   Enumerated in `RECONCILIATION_M1.md`.
3. Re-run the scoped gate after each fix; target full agreement on the window-live set.
