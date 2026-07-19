<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Epistemic Status Standard

## Purpose
Every claim in this system — in Domain Model concept docs, Detection Methods, or Strategy Library
rules — carries an implicit claim about how well-grounded it is. Up to this point, that groundedness
was inconsistently stated: some entries flagged it explicitly (Liquidity Pools' Observed vs. Inferred
section), others quietly asserted causal/interpretive claims as if they were plain fact (early
Efficient Price and Mitigation language — see Backlog Notes history). This document fixes that by
giving every entry one required, consistent way to tag a claim's status.

## The Label Set
Every claim, rule, or output field should carry exactly one of these labels:

- **OBSERVED** — directly present in the data itself (e.g. "candle 3's low is 1.2713"; "price
  closed above 1.2700"). Nothing is inferred; it's a read of the raw series.
- **CALCULATED** — a deterministic function of observed data, with no interpretive judgment (e.g.
  ATR(14); a three-candle gap's gap_bounds; whether a candle CLOSE crossed a stated boundary).
  Calculated claims are as solid as Observed ones — they just require a defined formula rather
  than being a raw field.
- **INFERRED** — a claim about something not directly present in retail candle data, derived by
  applying this system's model to what IS observed (e.g. "this is buy-side liquidity"; "this
  origin_point represents a market maker's leftover position"). Inferred claims are the system's
  interpretation, not a direct read — see Model Interpretation below.
- **ASSUMED** — a stated precondition or working premise adopted for the model to function, not
  itself derived from data (e.g. "a nested multi-timeframe nested structure exists"; "orders are
  concentrated by proximity, not identical price"). Assumptions are not claims about what's true
  in a given instance — they're the ground rules the model operates under.
- **HEURISTIC** — a rule of thumb carried over from trading experience, not yet backed by a
  formal calculation or dataset (e.g. Fugazi Wednesday; the 4H-liquidation-direction bias in
  Liquidate to Rebalance). Heuristics are explicitly soft — see SOFT_CONFLUENCE in the Strategy
  Library's rule_type tagging, which is the execution-layer counterpart of this label.
- **VALIDATED** — has been checked against labeled historical data (per the Validation folder)
  and shown to hold up. Nothing in this system currently carries this label — it doesn't exist
  yet, because the trading journal doesn't exist yet. This label is aspirational until stage 3.
- **UNVALIDATED** — the default state for anything not yet checked against data. Nearly
  everything in this system is currently UNVALIDATED, including well-reasoned INFERRED claims.
  Being UNVALIDATED is not a criticism — it's an honest statement of where the project is.

## Relationship to the Four-Layer Reasoning Framework
Rather than running two separate tagging systems, the four-layer distinction below is the
*reasoning process* that determines which single label above applies — not a second, parallel
tag every entry needs. When writing or reviewing a claim, ask which layer it belongs to:

1. **Geometric/data observation** — what is directly measurable in the candle series. Maps to
   OBSERVED or CALCULATED.
2. **Model interpretation** — what this system's specific trading framework claims that
   observation *means* (e.g. "this gap represents unresolved order-flow imbalance"). Maps to
   INFERRED, and should be written as an interpretation, not restated as if it were the
   observation itself.
3. **Strategy hypothesis** — a claim about tendency or increased likelihood built on top of a
   model interpretation (e.g. "price has an increased tendency to revisit this interval"). Maps
   to HEURISTIC or ASSUMED, depending on whether it's a trader's rule of thumb or a structural
   premise the model needs to function at all.
4. **Validation question** — whether a hypothesis actually improves setup classification or
   expectancy. Maps to VALIDATED or UNVALIDATED, and is the Validation folder's job to answer,
   not something asserted at authoring time.

## Application Rule
When a Domain Model or Detection Method entry states something that isn't a direct OBSERVED or
CALCULATED fact, it should say so using this framing rather than asserting it flatly:

- Bad: "The pool becomes unobstructed."
- Better: "Model interpretation (INFERRED, UNVALIDATED): the pool becomes unobstructed."

This doesn't mean every sentence needs an inline tag — that would make the documents unreadable.
It means: (a) causal/interpretive language should read as interpretation, not fact, through word
choice and framing, and (b) each entry's Output/Result or Definition section should include a
brief epistemic-status note for its core claims, so an AI (or a future reader) can tell which
category governs on the FIRST question. This is being retrofitted into existing entries — see
Backlog Notes for tracked progress.

## Confidence and Provenance (a separate, complementary axis)
Epistemic status (above) answers "what KIND of claim is this." A separate concern is "HOW
confident are we, and where did the value come from" — this matters even for two INFERRED claims
of the same kind, since one may be based on a session high with an unambiguous source, and
another on a fuzzy discretionary read. Every computed/detected object should carry, alongside its
epistemic status:

- `confidence`: a float, not just a category — how strong is this instance's evidence
- `source_method`: which Detection Method produced it (e.g. "ATR_SWING_HIGH", "PREVIOUS_DAY_HIGH")
- `model_version`: which version of the calibration/logic produced it, so behavior changes are
  traceable to a specific version bump, not silently absorbed

This is defined more fully in Object_Schemas — every schema there includes these fields.
