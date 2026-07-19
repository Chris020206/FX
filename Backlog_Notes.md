<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Backlog Notes (Combined — Domain Model + Detection Methods + Object Schemas + Strategy Library + AI Policy + Validation)

This file spans the whole system. Every open item from any part of the system should be logged
here, with an urgency note explaining what it blocks (or doesn't) and what it relates to. Items
fully resolved within an entry's own Open Questions section don't need to be duplicated here —
this file is for things worth tracking at a glance across the whole system.

## Urgency Legend
- **BLOCKING** — cannot proceed with the specific downstream thing named until this is resolved
- **HIGH** — not blocking today, but load-bearing for multiple parts of the system; resolve soon
- **MEDIUM** — matters before execution-level logic or backtesting; fine to leave during design
- **LOW** — cosmetic, organizational, or genuinely not reachable yet; safe to ignore for now

---

## Resolved this session (real GBP/JPY data calibration pass)

### Mitigation — fill_ratio entry threshold — RE-RESOLVED WITH REAL DATA
The earlier 75%/50% fill_ratio thresholds (set in an earlier session) were an unvalidated guess.
Checked against 11 real, cross-verified GBP/JPY 5m examples (3:50 Scalp winning examples,
Jun 9 – Jul 13 dataset — see the master OHLC file build process for how much cleanup that took).
Real threshold: ~25% fill_ratio for a single-candle origin zone, ~50% for a widened 15m zone —
zone-width-dependent, not one universal number. 10/11 examples matched cleanly; the one miss
(Jun 25) missed by 2 percentage points, within stated market-imprecision tolerance. See
Mitigation.md's Calibration Evidence section.

---

## Resolved earlier session (structural review pass, per the "Thoughts and Feedback" document)

### Origin_point detection — RESOLVED
Was the single most-flagged BLOCKING item across two separate reviews (our own backlog, and the
external Thoughts and Feedback review, independently). Now formally specified in
Detection_Methods/Origin_Point_Detection.md: required input candles, qualifying impulse
definition (gap-based primary rule, displacement-based fallback), candidate selection rule, zone
boundaries (flagged default, see below), confirmation rule, invalidation rule, multi-candidate
handling, and timestamp behavior. Mitigation and Efficient Price both consume this directly now.

### Reconcile ATR-swing detection vs. Liquidate to Rebalance's fixed session-based levels — RESOLVED
Was HIGH/BLOCKING. Resolved architecturally, not by picking one: created Reference_Level.md as a
common interface, with ATR_Swing_Detection.md and Session_Level_Detection.md as two separate,
non-competing implementations. Liquidate to Rebalance's Overview updated accordingly. This mirrors
the external review's independently-arrived-at recommendation almost exactly.

### Circular dependency (Liquidity Sweep ↔ Efficient Price) — RESOLVED
Confirmed a real two-node cycle exists in the Markdown "Depends on" metadata (in addition to the
three-node loop through Mitigation originally flagged). Resolved via Domain_Model/Event_Model.md's
Event/Tracker/Evaluator separation — the conceptual cycle is real and stays documented as such;
the software implementation is acyclic. Object_Schemas now include SweepEvent, MitigationState,
and EfficiencyState as the three distinct object kinds this pattern requires.

### Causal claims stronger than evidence ("market maker's leftover position," "unfilled
### institutional interest," "the pool becomes unobstructed") — RESOLVED
Created Standards/Epistemic_Status.md (merging the four-layer reasoning framework with a label
taxonomy: OBSERVED/CALCULATED/INFERRED/ASSUMED/HEURISTIC/VALIDATED/UNVALIDATED). Applied to
Efficient_Price.md, Mitigation.md, and Inefficiency.md — each now separates a computable
Definition from a labeled Model Interpretation section, rather than asserting interpretation as
flat fact.

### "Liquidation" terminology ambiguity (vs. margin liquidation) — RESOLVED
Created Standards/Terminology.md; added a disclaimer note to Buy_Order_Liquidation.md and
Sell_Order_Liquidation.md. Files were NOT renamed (would have triggered another full
cross-reference cascade like the Market-Wide Liquidation Process merge) — the meaning is now
stated explicitly instead.

### Folder restructure — DONE
Renamed Knowledge_Library → Domain_Model. Added Object_Schemas/, Detection_Methods/, AI_Policy/,
Validation/, Standards/ as new top-level folders. Did NOT subdivide Domain_Model into six
subfolders as the external review suggested — held off per earlier reasoning (too few files per
category right now to justify it).

### Missing system-level docs (epistemic standard, object schemas, event model, AI policy,
### validation specs) — DONE, first versions
All now exist: Standards/Epistemic_Status.md, Standards/Terminology.md, Object_Schemas/ (7
schemas), Domain_Model/Event_Model.md, AI_Policy/ (3 docs), Validation/ (3 docs). All are
first-pass drafts with their own Open Questions sections — see each individually.

---

## New items introduced by this session's work

### Session Level Detection — daily/weekly candle rollover convention undefined
**Urgency: BLOCKING for Liquidate to Rebalance specifically.** PDH/PDL and "previous day" are
meaningless without a fixed rollover convention (FX brokers vary — some roll at 17:00 EST per
interbank convention, others at 00:00 UTC). This is a new, more precise version of the old
generic "time handling needs to be formalized" item — now localized to exactly where it blocks
something. See Detection_Methods/Session_Level_Detection.md Open Questions.

### Origin Point Detection — zone boundary convention — RESOLVED
**Confirmed: full wick-to-wick candle range.** Also added, from your clarification: double-licky
candle handling (one-level timeframe drill-down, e.g. 15m→5m, with a 50%-of-parent sizing
safeguard), and a Lower-Timeframe (entry-tied) vs. Higher-Timeframe (context/bias-tied, 4H→1H)
tier distinction. See Detection_Methods/Origin_Point_Detection.md.

### Session Level Detection — daily/weekly candle rollover convention — INTENTIONALLY DEFERRED
**Urgency: BLOCKING for Liquidate to Rebalance, deferred by design, not oversight.** You confirmed
this depends on which live forex data API gets chosen later (stage 4). Action item flagged for
that stage: check rollover convention as a selection criterion when picking a provider, then set
this parameter. Not resolvable before that choice is made.

### Time handling (GMT/BST, weekend/holiday transitions) — still not formalized
**Urgency: MEDIUM, cross-cutting.** Originally flagged generically in the architecture review;
now more precisely located inside Session Level Detection's rollover-convention blocker above,
but the broader GMT/BST issue also affects any UK-clock session window referenced anywhere in the
Strategy Library (3:50 Scalp's time window, Liquidate to Rebalance's session brackets, the
still-undefined General Rules time brackets from early in this project).

### AI_Policy and Validation docs are policy specifications, not built systems
**Urgency: LOW for now, by design.** Responsibilities.md, Output_Schema.md, Retrieval_Rules.md,
Labeling_Guide.md, Backtest_Protocol.md, and Metrics.md are all first-draft specs with no actual
implementation behind them yet (no RAG index, no historical examples database, no backtest
infrastructure). This is expected at this stage — flagged so "a document exists" doesn't get
mistaken for "a system exists."

---

## Carried over, unchanged

### ATR Swing Detection — calibration defaults unvalidated
`n=14`, `k=1.5` (and the derived zone-width/equal-tolerance multipliers in Liquidity Pools) are
starting defaults, not derived from data.
**Urgency: LOW** for design work; **BLOCKING** before backtesting or live deployment.

### ATR Swing Detection — no floor for degenerate low-ATR conditions
**Urgency: LOW.** Edge case, not reachable until real data testing begins.

### Liquidity Pools — PASSIVE order depth proxy undefined
Needs historical reaction-magnitude data (trading journal, stage 3) to estimate.
**Urgency: MEDIUM.**

### Liquidity Sweep — GRAB vs. SWEEP 1-candle/2-candle boundary untested
**Urgency: LOW.**

### Efficient Price — multi-timeframe overlap handling undefined
**Urgency: MEDIUM.** Liquidate to Rebalance already operates across multiple timeframes, so this
isn't hypothetical.

### Reconcile Pre-News Scalp Rule vs. Liquidate to Rebalance's own Rule 1 (news exclusion overlap)
**Urgency: MEDIUM.**

### Confirm SOFT_CONFLUENCE classification of the 4H-liquidation-direction bias statement
**Urgency: LOW.**

### Liquidate to Rebalance — Entry Model step 7 references an undefined "entry model"
**Urgency: BLOCKING for that strategy's Entry Model section specifically.**

### Liquidate to Rebalance — Trade Management / Risk undefined
**Urgency: LOW for now, BLOCKING before live.**

### Liquidate to Rebalance — GBP/JPY applicability unconfirmed (source model is GBP/USD)
**Urgency: MEDIUM-HIGH**, given the project's actual target pair.

### Three_Fifty_Scalp — Pre-News Scalp Rule applicability unclear
**Urgency: LOW-MEDIUM.**

### Three_Fifty_Scalp — whether a higher-timeframe Efficient Price precondition applies
**Urgency: MEDIUM.**

### Three_Fifty_Scalp — Entry Model / Trade Management / Risk fully undefined
**Mostly resolved.** Entry Model: fires on Mitigation's meets_threshold, same trigger for both
timing variations, all 12 examples now doubling as verified entry points. Trade Management:
break-even calibrated (12/12, 10–270 min); take-profit revised from a fixed 80%/20% split into a
priority-ordered 3-step decision tree (invalidation exit first via Structural Continuation Break
Detection's new adverse mode, then target-hit, then explicit no-rule/discretion) after reviewing
all 12 examples' notes — Step 1 now verified against real data on all 3 candidate examples (Jun
29, Jul 6, Jun 3). Risk: stop = origin_point far boundary + 3 pips, checked against 11/12 examples
(3.3–13.4 pips, sane); 0.5% sizing and the daily trade cap moved to General_Rules/Risk_Management.md.
**Remaining**: Step 2's individual target-price re-verification, Jul 6's widened-zone stop
convention, and the pre-entry/post-entry firing distinction surfaced by Jun 3 (see Structural
Continuation Break Detection below).

### Structural Continuation Break Detection — now dual-mode, one new open item
**Urgency: LOW for now.** Generalized to a confirmation mode (break-even, 1H/15m, 12/12 examples
checked) and an adverse mode (take-profit invalidation exit, 4H/1H, now 3/3 examples fully
checked). No cap/timeout defined for either mode if the break never arrives; only validated on
GBP/JPY; automated direction detection (an input this method needs but doesn't solve) proved
genuinely unreliable across four different heuristics during calibration — worth remembering this
isn't a solved problem before assuming it elsewhere in the system. New: adverse mode can fire
before trade entry (Jun 3), where it functions as a pre-entry risk flag rather than an exit —
not yet formally distinguished from the post-entry exit case in the method's own output.

### Fugazi Wednesday — no home yet
**Urgency: LOW.** General_Rules currently only contains hard gates; this is explicitly a soft
heuristic and needs a home that doesn't misrepresent it as one.

### Asia session liquidation rule — standalone strategy vs. component of Liquidate to Rebalance
undecided
**Urgency: MEDIUM.**
