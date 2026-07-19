# Next Step

**One unit of work at a time. Short-lived by design — replace this file when the step closes.**
Long-range plan: `ROADMAP.md`.

---

## Current step: M1 — Port the Pine detector to Python

- **Opened:** 2026-07-19
- **Status:** `IN PROGRESS` — port implemented and self-run; gate blocked on the
  TradingView box comparison (trader) and the label-set answer. See
  `Implementation/M1_PORT_NOTES.md`.
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

### Acceptance gate — pre-committed, do not adjust
1. Run against `DATASET/csv/Tier 1/FX_GBPJPY, 5m, 24 may - 13 july.csv`.
2. Compare boxes against the Pine's output on TradingView over the same span.
3. **Pass:** every box matches on origin bar, both bounds, direction, and V2 flag. Any mismatch
   is listed individually with its bar timestamp — never reported as a percentage.
4. Emit roughly **3.2 boxes/day** in-window. **If output exceeds ~10/day, the port is wrong** —
   stop and diagnose rather than filtering afterwards.
5. Recall against the twelve labelled examples is reported but is **not** the gate. The gate is
   agreement with the Pine.

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
- [ ] Gate run, result recorded (pass or fail, unadjusted) *(steps 1 & 4 done —
  3.28 boxes/day in-window; steps 2–3 need the Pine's TradingView boxes from the trader)*
- [ ] Divergences from Pine listed individually in the PR
- [ ] `ROADMAP.md` M1 row updated
- [ ] This file replaced with the next step
