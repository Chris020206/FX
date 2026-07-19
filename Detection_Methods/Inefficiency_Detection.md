<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Inefficiency Detection

## Metadata
- Path: Detection Methods > Inefficiency Detection
- Market scope: FX spot (retail)
- Produces: InefficiencyInstance objects (see Object_Schemas)
- Depends on: ATR Swing Detection (shared ATR(14) basis for the minimum size threshold)
- Depended on by: Inefficiency (Domain Model concept), Origin Point Detection (primary
  qualifying-impulse rule)
- Status: Approved

## Definition
This is the concrete algorithm for detecting an Inefficiency (see Domain_Model/Liquidation_Logic/
Inefficiency.md for what the concept means and why it matters). This entry only defines how to
compute one from a candle series.

## Inputs / Variables
- c1, c2, c3: three consecutive candles, using OHLC (High/Low relevant, Open/Close of c1/c3
  irrelevant to the gap itself)
- gap_bounds: the resulting unfilled interval, direction-dependent (see Detection Rule)
- min_gap_size = ATR(14) on the timeframe the gap forms on, using the same ATR parameters as ATR
  Swing Detection (period 14, Wilder's smoothing)
- Scope restriction: only evaluated on the Daily, 4H, and 15m timeframes (per Inefficiency's own
  Market Model Assumptions — lower timeframes are treated as noise for this model's purposes)

## Detection Rule
IF c3.low > c1.high AND (c3.low - c1.high) > min_gap_size → BULLISH inefficiency exists;
gap_bounds = [c1.high, c3.low]
IF c1.low > c3.high AND (c1.low - c3.high) > min_gap_size → BEARISH inefficiency exists;
gap_bounds = [c3.high, c1.low]
IF neither condition holds (wick ranges overlap, or the gap doesn't exceed min_gap_size) → no
inefficiency is recorded, regardless of how large c2's range was

Worked example: c1 (bearish) O=5, H=10, L=1, C=2. c2 (bullish, the impulse candle) O=2, L=1,
H=15, C=14. c3 (bullish) O=14, L=13. Since c3.low (13) > c1.high (10), this is a candidate BULLISH
gap with gap_bounds = [10, 13] — recorded as a genuine inefficiency only if (13 - 10) exceeds
min_gap_size for the timeframe in question.

Reference basis: this ATR(14) minimum-size rule mirrors a public TradingView Fair Value Gap
indicator you shared for inspiration, whose default "auto minimum gap size" mode uses exactly
ta.atr(14) — independent confirmation that the ATR-based approach used throughout this system is
a reasonable, industry-consistent choice here too.

## Process / State Transition
FORMED (gap_bounds established on c3's close) → OPEN (unfilled) →
  [price later trades into gap_bounds] → PARTIALLY_FILLED (fill_depth tracked, continuous
  measure — same pattern as Mitigation's approach_depth) → FULLY_FILLED (price has fully
  retraced through gap_bounds)

## Output / Result
An InefficiencyInstance object: gap_bounds, direction, source timeframe, state
(OPEN/PARTIALLY_FILLED/FULLY_FILLED), fill_depth. Epistemic status: CALCULATED — the gap's
existence and bounds are a deterministic function of the three candles and the stated threshold,
not an interpretation. (Its meaning — "unfilled institutional interest" — is a separate INFERRED
claim; see Inefficiency's Model Interpretation section.)

## Edge Cases
- Nested/overlapping inefficiencies during multi-leg impulsive moves are tracked as independent
  instances, not merged or reconciled into a single gap. This matches the reference
  implementation's approach (each detected gap tracked independently) and avoids unneeded
  complexity from attempting to merge overlapping zones.
- A gap can be partially filled and then price can resume the original direction without ever
  reaching FULLY_FILLED — expected, not an error state.
- Not adopted from the reference implementation: an optional volume-based confirmation filter and
  an optional EMA trend-alignment filter. Volume filtering doesn't reliably transfer to spot FX
  (broker-reported volume in a decentralized OTC market isn't true consolidated volume). The
  trend-alignment filter is closer to a Strategy Library confluence factor than a detection rule,
  so it's left out here.

## Relationships
- Feeds: Origin Point Detection's primary (gap-based) qualifying-impulse rule — c1 in this
  pattern is the candidate origin_point candle when this rule is the one that fires
- Implements the concrete algorithm for: Domain_Model/Liquidation_Logic/Inefficiency.md

## Open Questions / Deliberately Deferred
- None remaining at the algorithmic level. Multi-timeframe overlap (a gap relevant on one
  timeframe interacting with structure on another) is tracked as an Efficient Price open question.
