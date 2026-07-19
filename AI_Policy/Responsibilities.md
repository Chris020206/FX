<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# AI Responsibilities Specification

## Metadata
- Path: AI Policy > Responsibilities
- Status: Draft — first version, based on the Architecture.md review and the Thoughts and
  Feedback review's proposed AI may/may not list

## Purpose
Explicitly state what the AI reasoning layer (per Architecture.md component 7) may and may not
do. This exists because Architecture.md already established the core principle — "Hard rules
should remain code. Do not let the AI casually override them" — but didn't formally specify the
full boundary. This document is that specification.

## AI May
- Explain a detected state in plain language, grounded in the specific StrategyCandidate /
  Tracker / Event fields it was given (not free recall)
- Compare a candidate against labeled historical examples (per the Historical Examples Database)
- Identify contradictions between retrieved Domain Model knowledge and the current candidate's
  computed state
- Rank/weight SOFT_CONFLUENCE factors already computed by the Strategy Engine, within the bounds
  the Strategy Engine provides — it may explain and contextualize a weight, not invent one from
  nothing
- Flag missing information (e.g. "mitigation_state is UNMITIGATED but approach_depth data looks
  incomplete for this timeframe")
- Express uncertainty explicitly, including naming which Epistemic Status category (per the
  Epistemic Status standard) a claim falls into
- Ask a clarifying question when retrieved context is genuinely ambiguous, rather than guessing

## AI May Not
- Change a HARD_GATE result. If `hard_rules.valid_day == false`, the AI does not get to argue the
  setup is fine anyway. This is the direct implementation of Architecture.md's "hard rules stay
  in code" principle.
- Fabricate a structure that wasn't actually detected (e.g. inventing a liquidity pool, an
  origin_point, or an inefficiency that isn't present in the Market Analysis Engine's output)
- Calculate a level, threshold, or price from prose description alone when a Detection Method
  exists — if ATR Swing Detection or Session Level Detection should have produced a
  ReferenceLevel, the AI does not compute one itself from raw candles
- Execute orders, or take any action beyond producing an assessment for the Companion Interface
- Convert an UNVALIDATED or HEURISTIC claim into language that reads as VALIDATED or CALCULATED —
  epistemic status must be preserved in the AI's own output, not upgraded for confidence or
  fluency's sake
- Silently resolve a genuine conflict between two Domain Model entries by picking one — it should
  surface the conflict instead (this is the same principle behind why Backlog Notes exists at
  the document level; the AI shouldn't quietly do at inference time what this project explicitly
  tracks and resolves deliberately at authoring time)

## Enforcement Note
This document describes intent, not a technical guarantee. The actual enforcement mechanism is:
(a) hard rules are computed in code and passed to the AI as already-final booleans, never as
editable inputs; (b) the Output Schema (see Output_Schema.md) structurally has no field where a
hard-rule override could be expressed; (c) the Evaluation/Backtesting system (per Architecture.md
component 9) should include a check for whether the AI's assessment ever contradicts a hard-rule
result, as a monitored failure mode, not an assumed impossibility.

## Open Questions / Deliberately Deferred
- No enforcement mechanism has actually been built yet — this is a policy specification, not a
  technical control. Corresponds to Validation's eventual job of checking whether the AI behaves
  as specified here.
