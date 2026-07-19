# Metrics

## Metadata
- Path: Validation > Metrics
- Status: Current — rewritten 2026-07-19 against `main_Tier_1_Examples_v3.xlsx`
- Depends on: `Labeling_Guide.md` two-axis taxonomy

## Principle (unchanged)
Classification accuracy comes first. Profit and expectancy metrics are deliberately excluded from
this initial set. Adding profit-based metrics before detection accuracy is validated risks
optimizing for a number confounded by detection errors, data errors, and ordinary variance in
valid-but-losing setups.

---

## Tier 1 — the maturity metric

### Rule-qualification rate
The headline number. Of labeled `VALID_ENTRY` rows, the fraction the current ruleset reproduces
exactly.

```
rule_qualification_rate = count(Rule-qualified == YES) / count(Historical == VALID_ENTRY)
```

**Current: 9 / 11 historical trades = 82%.**  Progression: v3 64% -> v1.2 73% -> v1.3 82%.

This is not a performance measure. It measures how much of your own discretionary read the formal
rules have captured. It is expected to rise as research flags close, and it is the number that
says whether the ruleset is ready to freeze.

### Research-flag concentration
How many open flags, and how many labels each touches.

**Current: 2 open rule flags (RF-003, RF-004) plus 1 parameterised-but-unvalidated (RF-002).**
RF-001 and RF-005 closed 2026-07-19.

A flag resting on a single example cannot be resolved by that example — RF-003 depends entirely on
T1-010, and RF-002's 0.3 pip default is fitted to two examples separated by 0.15 pips. Expanding
the labeled sample is a prerequisite for closing them, not an optional improvement. See
`Backtest_Protocol.md` on unlabeled Tier 1 capacity.

### Parameter validation status
Any parameter shipped as UNVALIDATED must be recorded per run and re-tested when new labels exist.
Currently: `threshold_tolerance_pips = 0.3` (candidates {0.1, 0.3, 0.5}).

### Freeze gate
```
ruleset_frozen = (open rule flags == 0)
```
**Current: NOT FROZEN.** RF-003 and RF-004 open; T1-005 contested. Tier 2 metrics below are
undefined until this passes.

### Entry-time fidelity
Separate from qualification: does the rule-derived entry time match the historical entry time, to
the bar? This catches changes that qualification rate hides. Adopting the 0.3 pip tolerance moved
T1-009's rule entry from 16:00 to 15:40 while leaving its YES status unchanged — a 20-minute shift
invisible to the qualification metric. Track both.

---

## Tier 2 — detection accuracy (blocked)

These require a frozen ruleset. Recorded now so the protocol is fixed before the data is seen.

- **False positives** — a `StrategyCandidate` generated where the label says `INVALID`
- **False negatives (missed setups)** — a labeled `VALID_ENTRY` the system never surfaced
- **Precision / recall**, reported separately, never as a blended score
- **Threshold-timing accuracy** — does the computed `First applicable-threshold time` match the
  manual reading, to the bar
- **Zone-bound accuracy** — do computed `Exact lower/upper bound` match manual construction
- **Zone-type agreement** — does the system pick the same one of FULL_5M / WIDENED_15M /
  REFINED_HTF_PUSH

The last three matter because a candidate can be right for the wrong reason. Matching on the
final verdict while disagreeing on bounds means the agreement is coincidental and will not hold
out of sample.

### Why a blended score is refused
With five open flags, a candidate that fails to match is indistinguishable from a decision not yet
made. A false negative and an unmade rule look identical in aggregate. Reporting them separately
is what keeps that distinction visible.

---

## AI layer metrics
- Agreement between AI assessment and the recorded human decision
- Whether `quality_score` separates `VALID_ENTRY`+won from `VALID_ENTRY`+lost — **not** win/loss
  alone, since a valid setup losing is expected variance
- Stability: does the assessment change given materially identical input
- **Epistemic preservation** — does the AI keep a `RESEARCH_FLAG` as a research flag, or does it
  quietly upgrade it to a qualified setup? This is now an explicit measured metric rather than an
  implied one, because `RESEARCH_FLAG` is the single most corruptible value in the taxonomy.

---

## Parameter versioning
Every measurement run records the `model_version` of every calibration parameter in effect: ATR
period and multiplier, the three zone thresholds, tolerance settings once RF-002 closes, and the
15:50 window once RF-005 closes. Without this, a change in results between two runs cannot be
attributed to a real improvement rather than parameter drift.

## Open Questions / Deliberately Deferred
- No baseline values. What rule-qualification rate is "good enough" to freeze is a judgment call
  and has not been made. 100% is almost certainly the wrong target — it would mean the rules had
  been fitted to every example including the ones deliberately held as research cases.
- No statistical significance requirement defined for Tier 2 sample size.
