<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Liquidity Sweep

## Metadata
- Path: Domain Model > Liquidation Logic > Liquidity Sweep
- Market scope: FX spot (retail)
- Depends on: Liquidity Pools, Internal and External Liquidity, Reference Level, Efficient Price
  (NOTE: this creates a real conceptual cycle with Efficient Price, which itself depends on
  Liquidity Sweep transitively via Mitigation/Inefficiency. This is intentional and correctly
  reflects a genuine feedback loop — see Domain_Model/Event_Model.md for how this is implemented
  as acyclic software via Events/Trackers/Evaluators, without needing to force this Markdown
  dependency into an artificially one-directional shape.)
- Depended on by: Mitigation, Inefficiency (context), Origin Point Detection, Strategy library entries defining bias/entry logic
- Status: Approved

## Definition
A liquidity sweep is a deliberate, directional push through a liquidity pool that triggers the resting/conditional orders there, followed by a reversal back through the level toward an opposing liquidity target. If price enters the pool's zone and simply continues through without reversing, that's not a sweep — it's just ordinary price movement through the level, already covered by Liquidity Pools' own activation logic.

## Market Model Assumptions
- Assumes a two-sided structure: an ultimate target liquidity pool (e.g. buy-side liquidity above
  an efficient bearish structure) and an opposing pool the market maker sweeps through first
  (sell-side liquidity below) in order to both trigger stops and accumulate a position at a
  discount before reversing into the target. This is the mechanism your explanation described; it
  is adopted as a working model, not verified from directly observable order flow (same Observed
  vs. Inferred caveat as Liquidity Pools). "Efficient" here is deliberate, not decorative — the
  target pool only becomes a live target once the structure it sits above/below is EFFICIENT (see
  Efficient Price). An inefficient structure still has unresolved business (unfilled orders,
  unmitigated positions) that takes priority over becoming a fresh sweep target.
- A precondition for treating any specific instance as a valid setup (not just a valid pattern
  in the abstract): on a 4H+ timeframe, Efficient Price must equal EFFICIENT for any prior
  opposing sweep's inefficiency/origin_point pair in the relevant region — i.e. no unresolved
  imbalance from a prior sweep. If that precondition fails, this entry does not define what
  happens next — it's out of scope for this framework, not an unhandled case.

## Inputs / Variables
- target_pool: the liquidity pool ultimately being driven toward (per Liquidity Pools)
- opposing_pool: the liquidity pool swept through first, opposite side from target_pool
- reference_timeframe: timeframe the target/opposing structure is defined on
- sweep_duration: number of candles from entering opposing_pool's zone_bounds to reversing back
  through it
- origin_point: see Detection_Methods/Origin_Point_Detection.md for the formal specification
  (candidate selection, zone boundaries, confirmation/invalidation rules). Referred to elsewhere
  as an "order block" — this entry avoids that term per preference, calling it the origin point
  instead.

## Trigger Condition
IF current_price enters opposing_pool.zone_bounds (per Liquidity Pools' Trigger Condition) AND
current_price subsequently CLOSES back outside opposing_pool.zone_bounds on the boundary it
entered from → classify as SWEEP
IF current_price enters opposing_pool.zone_bounds and continues, closing beyond the far side of
zone_bounds without ever closing back outside the near boundary → classify as CONTINUATION (not
a sweep — just price passing through the level, per Liquidity Pools' own activation logic)
Resolved ambiguity: a wick-only retrace back through the near boundary, or any intra-zone
back-and-forth that never produces a candle CLOSE outside the near boundary, does not count as
a reversal. Until a close-based reversal or a close-based continuation occurs, the instance stays
in ZONE_ENTERED — undetermined, not defaulted to either classification.

Sweep vs. Grab sub-classification (duration-based, distinct price-action signatures):
IF sweep_duration == 1 candle, with a large wick and small body → GRAB
IF sweep_duration > 1 candle, including consolidation beyond the level before reversing → SWEEP
  (in the narrower sense some frameworks use "sweep" for the multi-candle case specifically —
  this entry treats GRAB as a sub-type of SWEEP rather than a separate top-level category, since
  both satisfy the core Trigger Condition above)

## Process / State Transition
PRECONDITION_CHECK (Efficient Price == EFFICIENT for prior sweeps on 4H+? if no → OUT_OF_SCOPE)
→ ZONE_APPROACHING (opposing_pool) → ZONE_ENTERED (per Liquidity Pools' Trigger Condition) →
REVERSAL_CONFIRMED (price closes back through zone_bounds) → ORIGIN_POINT_MARKED →
IMPULSE_TOWARD_TARGET → (target_pool reached — see Liquidity Pools ACTIVATED state)

## Output / Result
- A directional bias is established: SWEEP at opposing_pool implies bias toward target_pool
- An origin_point is marked at the reversal candle, becoming a reference level for later re-entry
  (see Mitigation)
- The impulsive reversal candle(s) typically leave an Inefficiency (Imbalance) adjacent to
  origin_point — see that entry for the formal gap definition; this entry no longer restates it
  narratively
- The position(s) opened during the impulsive push into opposing_pool (i.e., the market maker's
  accumulated exposure used to fund the reversal) may remain open past the reversal — this
  leftover exposure is the subject of the Mitigation entry, not this one

## Edge Cases
- Precondition failure (Efficient Price != EFFICIENT for a prior sweep's pair on 4H+): this
  entry does not model what happens; treated as no-trade / out of scope by design, not an
  omission
- Partial-reversal ambiguity: resolved (see Trigger Condition — undetermined until a close-based
  outcome occurs, not defaulted either way)
- GRAB vs. SWEEP boundary at exactly 1 vs. 2 candles is a clean rule but hasn't been tested
  against real GBP/JPY data for whether it actually separates two behaviorally distinct cases
- Thin opposing liquidity: even a small number of resting orders in opposing_pool can produce
  large price displacement if there isn't much liquidity to absorb them — displacement size
  isn't purely a function of how many orders were there
- Broker internalization: if a large share of the orders being triggered are internalized by
  market-maker brokers rather than routed to the wider market, the public price impact may be
  smaller than the raw order count at that level would suggest

## Relationships
- Built on: Liquidity Pools (zone_bounds and activation logic that this pattern's trigger/reverse
  condition is layered on top of), Internal and External Liquidity (defines which pool is the
  higher-timeframe target vs. lower-timeframe opposing pool)
- Feeds: Mitigation (the leftover-position concept described in Output / Result), Inefficiency
  (the gap typically left by the reversal impulse)

## Open Questions / Deliberately Deferred
- Time-of-day filter: explicitly out of scope for this Domain Model entry. Whether a
  given session/time window is valid for this pattern is a Strategy library concern (your
  trading rules), not a market fact — the same reasoning applied to PASSIVE order depth in
  Liquidity Pools. The specific rules (session brackets, "3Fifty," Asia session liquidation
  rule, etc.) are being drafted as Strategy library entries; this Trigger Condition should
  consume that filter as an external input once it exists, rather than defining it here.
- Formal origin_point detection: resolved — see Detection_Methods/Origin_Point_Detection.md.
- Partial-reversal ambiguity: resolved (see Trigger Condition / Edge Cases).
