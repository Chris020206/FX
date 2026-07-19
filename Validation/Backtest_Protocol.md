# Backtest Protocol

## Metadata
- Path: Validation > Backtest Protocol
- Status: Current — rewritten 2026-07-19; dataset now exists, protocol updated accordingly
- Supersedes: the pre-dataset draft, which stated no historical GBPJPY data had been sourced

## Purpose
Defines how historical data is replayed through the full pipeline before the system is trusted.
The goal is initially classification accuracy, not profit prediction. See `Metrics.md`.

---

## The dataset

Ten 5-minute GBPJPY CSV files, UNIX timestamps, forming a clean non-overlapping chronological
partition. Verified 2026-07-19: no leakage between tiers.

| Tier | Range | Candles | Role |
|---|---|---|---|
| Tier 3 | 2025-02-02 → 2025-07-11 | ~32,900 | Fully reserved. Never opened. Final code test. |
| Tier 2 | 2025-07-13 → 2026-02-13 | ~43,400 | Held out. Blind validation. |
| Tier 1 | 2026-02-15 → 2026-07-13 | ~30,300 | Calibration. Rules were built here. |

### Two documented properties of this partition

**1. The tiers run backwards in time.** Calibration is on the *most recent* data; the final
reserved test is on the *oldest*. This is the reverse of conventional train-old / test-new
practice. It is defensible — the recent regime is the one being traded — but it means Tier 3
results will partly measure regime drift rather than rule quality alone. Record this as a known
property of any Tier 3 result rather than discovering it afterwards.

**2. Tier 1 is under-labeled.** All twelve Tier 1 examples fall between 2026-05-28 and 2026-07-10,
inside a single one of the three Tier 1 files. The other two files — roughly 20,000 candles
covering 2026-02-15 to 2026-05-22 — are calibration-tier data with no labels drawn from them.

The second point is directly actionable. RF-001 and RF-003 both rest entirely on T1-010, a single
example, and cannot be resolved from it. Labeling the unused Tier 1 span is the only way to grow
that sample **without spending Tier 2**. Do this before touching held-out data.

### Tier discipline
- Tier 2 is opened once, after freeze, and the result is recorded whatever it says.
- Tier 3 is not opened until a code implementation exists and Tier 2 has been scored.
- Re-tuning after seeing Tier 2 converts Tier 2 into calibration data. If that happens, say so in
  the Decision Log and treat Tier 3 as the only remaining held-out set.

> The existing 38-candidate scan in `DATASET/csv/Tier 2/Blind Detection Result Tier 2/` predates
> the v3 corrections and the current thresholds. It is void as a scoring artifact and must not be
> counted as Tier 2 having been spent.

---

## Protocol

```
Historical price data (UNIX timestamps, UTC+0)
→ Detection Methods (ATR Swing, Session Level, Inefficiency, Origin Point)
→ Zone construction (FULL_5M | WIDENED_15M | REFINED_HTF_PUSH)
→ Threshold evaluation (per Tier 1 Rulebook §4.2)
→ Strategy Engine (StrategyCandidate generation, hard rule evaluation)
→ AI assessment (per AI_Policy/Output_Schema.md)
→ Compare against labels (per Labeling_Guide.md)
```

Using the *exact* same code path as live operation is the point. A separate backtest-only
implementation would test something other than what actually runs.

### Preconditions before a scored run
1. Ruleset frozen — zero open rule flags. **Currently 5 open. Not met.**
2. Every calibration parameter carries a recorded `model_version`.
3. The 15:50 window is numerically defined (RF-005). Without it, the fifth condition of the
   rulebook's rule set is not implementable and any run encodes an undocumented assumption.

### Data handling
CSV files carry raw UNIX timestamps. Do not open them in a spreadsheet application — Google
Sheets and Excel auto-format the timestamp column as a duration and corrupt it silently. Read
them programmatically.

---

## Open Questions / Deliberately Deferred
- No replay infrastructure exists. This is a protocol specification, not an implementation.
- Sample size / statistical significance requirements not yet defined.
- Spread, slippage and execution modeling not addressed — consistent with classification-first.
