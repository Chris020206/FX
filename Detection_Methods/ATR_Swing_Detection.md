<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# ATR Swing Detection

## Metadata
- Path: Detection Methods > ATR Swing Detection
- Market scope: FX spot (retail)
- Produces: Reference Level instances of type ATR_SWING_HIGH, ATR_SWING_LOW, EQUAL_HIGHS_ZONE, EQUAL_LOWS_ZONE
- Depends on: ATR (Average True Range) — standard indicator, not separately defined in this system
- Depended on by: Reference Level (as one of its implementing methods); Internal and External
  Liquidity, Liquidity Pools, Liquidity Sweep consume its output via the Reference Level interface,
  not directly
- Status: Approved (calibration parameters n=14, k=1.5 remain pending backtesting against GBP/JPY history)

## Note on this entry's history
This was previously a Domain Model entry called "Structural Point Detection," treated as *the*
universal definition of a structural high/low. It has been reclassified as one Detection Method
among several (see Reference_Level.md for why) — the content and logic are unchanged, only its
role in the system has been clarified. It no longer defines what a structural point *means*
conceptually (that's Reference_Level.md's job); it only defines this one way of computing one.

## Definition
A structural point (swing high or swing low) is a local price extremum whose reversal magnitude,
measured from the prior extremum, exceeds a volatility-relative threshold. This method defines
that threshold and the associated confirmation logic, producing ATR_SWING_HIGH / ATR_SWING_LOW
Reference Level instances.

## Method Assumptions
- Uses ATR-based ZigZag rather than fixed-percentage or fixed-pip thresholds, so that detection
  scales automatically across timeframes (5M vs. Daily) and across volatility regimes (quiet
  sessions vs. high-impact news), without needing a separately hand-tuned constant for each.
- ATR is calculated using Wilder's smoothing (the original ATR formula), not a simple moving
  average of True Range.
- The specific numeric parameters below are not justified from first principles — they are
  reasonable starting defaults, explicitly flagged for calibration once historical GBP/JPY data
  is available.

## Inputs / Variables
- atr_period (n): 14 (default; calibration parameter)
- atr_smoothing: Wilder's
- swing_multiplier (k): 1.5 (default; calibration parameter)
- swing_threshold = k × ATR(n)
- price_series: OHLC data for the timeframe being analyzed
- last_confirmed_point, current_provisional_point

## Detection Rule
IF price moves swing_threshold beyond the most recent confirmed extremum, in the direction
opposite to the current leg → a new provisional structural point is marked at the extremum
reached before the reversal
IF price continues in the new direction and later reverses by swing_threshold again → the
previous provisional point becomes CONFIRMED

## Process / State Transition
LEG_FORMING → REVERSAL_THRESHOLD_MET → POINT_MARKED (PROVISIONAL) →
  [price continues in new direction] → NEXT_REVERSAL_THRESHOLD_MET → POINT_CONFIRMED
  (the prior provisional point becomes CONFIRMED once its opposite-direction reversal is itself
  confirmed by the same rule)

## Output / Result
- A sequence of Reference Level objects (level_type = ATR_SWING_HIGH or ATR_SWING_LOW), each
  tagged confirmation_state = CONFIRMED or PROVISIONAL per the Reference Level schema
- The single most recent point is always PROVISIONAL until superseded; all earlier points in the
  sequence are CONFIRMED
- Any consumer of these Reference Levels must check confirmation_state — treating a PROVISIONAL
  point as settled fact will misrepresent live analysis, since it can still be invalidated by
  continued price movement
- Epistemic status: CALCULATED (the swing point's price/location is a deterministic function of
  the price series and stated parameters — not an interpretation)

## Edge Cases
- Repainting: the last leg of any ZigZag-style method is inherently provisional; this is expected
  behavior, not a bug, and is why the CONFIRMED/PROVISIONAL distinction exists
- Low-volatility stretches: ATR shrinking to near-zero could produce an oversensitive threshold;
  no floor value is currently defined (open item, low priority)
- Gaps (e.g. weekend open in FX): a single-bar gap larger than swing_threshold will register as
  an instant structural point with no intermediate price action — acceptable for now, not
  specially handled

## Relationships
- Implements: Reference Level (produces ATR_SWING_HIGH / ATR_SWING_LOW / EQUAL_HIGHS_ZONE /
  EQUAL_LOWS_ZONE instances)
- Its swing_threshold value directly defines the "significance" cutoff used in Internal and
  External Liquidity and the equal-highs tolerance used in Liquidity Pools/Inefficiency
- Does NOT compete with Detection_Methods/Session_Level_Detection.md — both produce Reference
  Levels, but of different level_types, for different purposes. Neither should be forced to
  reconcile with the other.

## Open Questions / Deliberately Deferred
- atr_period (14) and swing_multiplier (1.5) are starting defaults, not derived values — flagged
  for backtesting against GBP/JPY history once the trading journal (stage 3) exists
- No floor defined for degenerate low-ATR conditions
