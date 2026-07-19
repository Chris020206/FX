<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Internal and External Liquidity

## Metadata
- Path: Domain Model > Structure > Internal and External Liquidity
- Market scope: FX spot (retail) — framework applies across any timeframe within a single instrument
- Depends on: Reference Level (defines point_A/point_B — typically via ATR Swing Detection for this entry's purposes, though not exclusively), Liquidity Pools (partially — this entry underlies the "structural_reference" input used there)
- Depended on by: Liquidity Pools, Strategy library entries using multi-timeframe context
- Status: Approved

## Definition
Internal and external liquidity are relative classifications of a liquidity pool's location, defined by whether the pool sits inside or outside a given structural range. The classification is not absolute — the same pool can be internal relative to one reference range and external relative to another, smaller one nested inside it.

## Market Model Assumptions
- structural highs/lows (point_A, point_B) are Reference Level instances, typically produced by
  ATR Swing Detection (ATR-based ZigZag, k=1.5, ATR period=14, Wilder's smoothing) for this
  entry's purposes. Only CONFIRMED points should be used to define an active structural_range; a
  PROVISIONAL point may still be invalidated by continued price movement.
- Adopts a multi-timeframe nested-structure framework (associated with Smart Money Concepts / ICT-style analysis) as a working analytical model for this strategy, not as an established mathematical property of markets. An earlier version of this entry stated "financial markets exhibit fractal market structure" as settled fact — that overreaches. True mathematical fractal self-similarity (in the Mandelbrot sense) is a statistical claim about return distributions; it does not guarantee that every structural high/low deterministically contains a smaller structural high/low at every timeframe. This entry uses "nested structure" as a chosen framework, not a proven law.

## Inputs / Variables
- structural_range: an interval [point_A, point_B], where point_A and point_B are structural
  highs/lows on a given timeframe (detection method is an open dependency)
- reference_timeframe: the timeframe the range is defined on (e.g. Daily, 4H, 1H, 15M, 5M, 1M)
- pool_location: the price/zone of a given Liquidity Pool being classified
- range_bounds: [min(point_A, point_B), max(point_A, point_B)]

## Trigger Condition (Classification Rule)
GIVEN a structural_range on a reference_timeframe and a pool_location:
IF range_bounds.min < pool_location < range_bounds.max → pool_location is INTERNAL relative to
structural_range
IF pool_location < range_bounds.min OR pool_location > range_bounds.max → pool_location is EXTERNAL
relative to structural_range
IF pool_location == range_bounds.min OR range_bounds.max → EXTERNAL, by convention (see Market
Model Assumptions: boundary points are treated as the origin of external liquidity, not as still
"inside" the range)

## Process / State Transition
This is a classification function re-evaluated per (structural_range, pool_location) pair rather
than a state machine in the traditional sense. However, structural_range itself changes over time
as new highs/lows form:
RANGE_ESTABLISHED (point_A, point_B set) → RANGE_ACTIVE (classifications computed against it) →
RANGE_INVALIDATED (a new CONFIRMED structural point closes beyond the existing range_bounds) →
RANGE_REDRAWN (the new confirmed point replaces the extreme it broke, forming a new
structural_range)

## Output / Result
- A given pool_location is labeled INTERNAL or EXTERNAL, always relative to a stated reference_range
- Nesting: a pool can hold multiple simultaneous labels across different reference_timeframes (e.g.
  internal to Daily, external to 1H) — any output should carry the reference_timeframe alongside
  the label, never an unqualified "internal/external"

## Edge Cases
- Boundary equality: resolved — treated as EXTERNAL (see Trigger Condition)
- Range invalidation: resolved — invalidation/redraw triggers only on a CONFIRMED structural point
  (never a PROVISIONAL one) closing beyond range_bounds
- Historical labels are NOT retroactively rewritten when a range is redrawn — every
  INTERNAL/EXTERNAL classification is timestamped to whichever structural_range was active at the
  time it was computed, preserving an auditable history rather than silently changing past output
- Significance threshold: resolved — defined by ATR Swing Detection's swing_threshold
  (k × ATR(n)), not a separate rule in this entry

## Relationships
- Consumes: CONFIRMED Reference Levels (typically from ATR Swing Detection)
- Provides the structural_reference input used by Liquidity Pools
- Every reference_timeframe's structural_range is itself potentially INTERNAL relative to a higher
  timeframe's range — a recursive relationship, not a separate rule

## Open Questions / Deliberately Deferred
- None remaining at the conceptual level. Numeric parameters (ATR period, swing multiplier) live
  in ATR Swing Detection and remain flagged there for calibration.
