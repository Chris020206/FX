<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Inefficiency (Imbalance)

## Metadata
- Path: Domain Model > Liquidation Logic > Inefficiency (Imbalance)
- Market scope: FX spot (retail)
- Depends on: typically forms as a byproduct of Liquidity Sweep's impulsive reversal
- Depended on by: Liquidity Sweep (Output/Result), Origin Point Detection (primary rule),
  Mitigation (origin_point context), Efficient Price, Strategy library entries using "fill the
  gap" logic
- Status: Approved
- Detection method: see Detection_Methods/Inefficiency_Detection.md for the concrete algorithm

## Definition
An inefficiency (also called an imbalance, or "Fair Value Gap" in some frameworks — the term is
cosmetic, the mechanism is what matters) is a three-candle price structure where the wick range
of the first candle and the wick range of the third candle do not overlap, leaving a price
interval that was skipped over rather than traded through. It is the same underlying concept as
"imbalance"; this entry treats the two words as synonyms, per your clarification.

## Epistemic Status (per the Epistemic Status standard)
- **Geometric observation (CALCULATED)**: a three-candle non-overlap of the stated size exists at
  a specific price interval. This part is not in question — it's a deterministic read of the data.
- **Model interpretation (INFERRED)**: this system's strategy model interprets that gap as
  representing unresolved order-flow imbalance — orders that could not be matched at the time,
  because price ran through the interval too quickly for participants to trade there. This is
  this system's explanation for *why* the gap formed; it is not directly observable from candle
  data alone (a three-candle non-overlap doesn't, by itself, prove which participants were or
  weren't able to trade, or why).
- **Strategy hypothesis (HEURISTIC, UNVALIDATED)**: price has an increased tendency to later
  revisit this interval, because the model interpretation above implies unfinished business there.
- **Validation status**: UNVALIDATED. This hypothesis has not yet been checked against labeled
  historical data (see Validation folder) — it is the specific claim that "fill the gap" logic
  should eventually be tested against, once the trading journal (stage 3) exists.

## Market Model Assumptions
- Resolved scope: this entry applies specifically to the Daily, 4H, and 15m timeframes. A gap
  technically forms on any timeframe (the geometric pattern is scale-invariant), but a 1m-chart
  gap is backed by substantially less buy/sell pressure than the same pattern on Daily or 4H, and
  is treated as noise for this model's purposes, not a meaningful inefficiency.
- Does not assume the inefficiency was caused by a Liquidity Sweep specifically — any sufficiently
  aggressive directional impulse can produce one. It is, however, the expected byproduct of the
  impulsive reversal described in Liquidity Sweep's Process/State Transition, which is why the two
  entries are linked. See Edge Cases for the other recognized cause.

## Output / Result
A gap_bounds interval, tagged OPEN / PARTIALLY_FILLED / FULLY_FILLED (see Detection Method for the
concrete state machine). This is the formal version of what Liquidity Sweep's Output/Result
section describes as leaving "inefficient price."

## Edge Cases
- Second recognized cause of gap formation, distinct from the Liquidity Sweep case: during
  periods of genuinely sparse liquidity (e.g. session turnover, "dead hours"), price can jump and
  trade sporadically simply to find enough participants to match orders, leaving a gap as a
  byproduct — without any directional sweep/reversal pattern behind it. This is treated as an
  exception, not a second primary mechanism; the Liquidity Sweep-driven case remains this system's
  main concern. No separate detection logic is defined for this case.
- A gap can be partially filled and then price can resume the original direction without ever
  reaching FULLY_FILLED — expected, not an error state.

## Relationships
- Commonly forms adjacent to Liquidity Sweep's origin_point: the origin_point is analogous to c1
  in this pattern, and the impulsive reversal candle is analogous to c2 (see Origin Point
  Detection's primary qualifying-impulse rule, which uses this directly).
- Feeds Mitigation indirectly: an unmitigated origin_point and an adjacent unfilled inefficiency
  frequently co-occur, since both are produced by the same impulsive move.
- Feeds Efficient Price: FULLY_FILLED is one of that entry's two required conditions.

## Open Questions / Deliberately Deferred
- Multi-timeframe overlap (a gap relevant on one timeframe interacting with structure on another)
  is tracked as an Efficient Price open question, not duplicated here.
