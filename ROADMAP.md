# Roadmap

Long-range plan. Intended to stay true for months — it describes *modules and their gates*, not
tasks. For the current unit of work see `NEXT_STEP.md`, which is short-lived by design.

Module map follows `Architecture.md`'s components. A module is DONE only when its gate passes.

---

## Status at a glance

| # | Module | State | Blocked by |
|---|---|---|---|
| M0 | Repo hygiene & guardrails | **DONE** 2026-07-19 | — |
| M1 | Detection engine | not started | — |
| M2 | Entry engine | logic validated, unwired | M1 |
| M3 | Trade management | **specification missing** | trader input |
| M4 | Backtest & evaluation | protocol written, no code | M1, M2, M3 |
| M5 | Historical examples DB | not started | M4 |
| M6 | AI reasoning layer | policy complete, no code | M5 |
| M7 | Live data & execution | not started | M4 green |
| M8 | Companion interface | not started | M6 |

---

## M1 — Detection engine
**Goal.** Port `Detection_Methods/order_blocks_v2 (26.07.17).pine` to Python, line by line.
**Explicitly not.** Inventing, improving, or inferring detection logic. This is translation.
**Gate.** On a Tier 1 span, the Python emits the same boxes as the Pine on TradingView: same
origin bars, same bounds, same bull/bear, same Variation-2 classification. Disagreements are
enumerated individually, not summarised as a percentage.
**Watch.** Pine's label set is 13 events / 17 examples; `main_Tier_1_Examples_v3.xlsx` has 12.
Establish which is authoritative before treating either as ground truth.

## M2 — Entry engine
**Goal.** Feed M1's zones into the existing validated entry logic (`Implementation/pipeline.py`):
activation, threshold + tolerance, window, crossing semantics, invalidation.
**Gate.** Reproduces every rule-qualified Tier 1 entry, exact to the bar, from M1 output alone.
**Note.** This logic already passes when given correct zones by hand. M1 is what it lacks.

## M3 — Trade management
**Goal.** Stop-loss, breakeven, take-profit, and the intraday-only rule.
**This is not a coding milestone yet.** `Take profit notes.md` is twelve days of discretionary
reasoning, not rules — it contains, verbatim, "I cant find a formal reason to exit it at a still
winning point". Themes present but unformalised:
- intraday-only close
- structural exit: when a 4H candle takes the prior 4H low, the prior 4H high is treated as safe
- targets: inefficiencies (D/4H/1H), equal highs, previous-day internal liquidity
- breakeven rules (referenced, never stated)
- `Structural_Continuation_Break_Detection.md` exists (Draft, 4 verified examples) and is likely
  the formal version of the structural exit
**Gate for the specification step.** Every one of the twelve labelled trades has a stated exit
rule, or is explicitly recorded as "no rule — discretion", with no third category.
**Gate for the code step.** Reproduces those exits on Tier 1.

## M4 — Backtest & evaluation
**Goal.** Replay harness per `Validation/Backtest_Protocol.md`, using the same code path as live.
Metrics per `Validation/Metrics.md`: rule-qualification rate, entry-time fidelity, precision and
recall reported separately, never blended.
**Precondition.** Ruleset frozen — RF-003 closed, T1-005 decided, the four UNVALIDATED parameters
supported by out-of-sample evidence.
**Gate.** Tier 1 fully reproduced. Only then is Tier 2 opened, once.

## M5 — Historical examples database
**Goal.** Queryable store of labelled examples, schema per `Validation/Labeling_Guide.md`'s
two-axis taxonomy. Unblocks `AI_Policy/Retrieval_Rules.md` step 5.
**Gate.** Retrievable by strategy and by structural similarity; round-trips the twelve Tier 1 rows.

## M6 — AI reasoning layer
**Goal.** Implement `AI_Policy/` — Responsibilities, Output_Schema, Retrieval_Rules. Already the
most completely specified part of the project.
**Gate.** Every `evidence`/`concerns` item cites a real `source_field`; no HARD_GATE result is ever
contradicted; epistemic status is never upgraded. Adversarially tested, not assumed.

## M7 — Live data & execution
**Goal.** Live feed, economic calendar, order placement.
**Precondition.** M4 green on Tier 2 *and* Tier 3. Nothing goes live on Tier 1 evidence.

## M8 — Companion interface
**Goal.** The human-in-the-loop surface. Several decisions (e.g. no automated bank-holiday check)
depend on a person checking before action — this module is where that assumption lives.

---

## Principles that outlive any milestone
1. Tier discipline. Tier 2 spent once; Tier 3 stays out of the repo until M4.
2. Gates are pre-committed and never adjusted to pass.
3. Specification beats inference. Search the repo before concluding something is undocumented.
4. Epistemic labels are preserved end to end.
5. Hard rules stay in code; the AI explains, it does not decide.
