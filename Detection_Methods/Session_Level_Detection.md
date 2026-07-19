<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Session Level Detection

## Metadata
- Path: Detection Methods > Session Level Detection
- Market scope: FX spot (retail), GBP/JPY-relevant session boundaries specified below
- Produces: Reference Level instances of type SESSION_HIGH, SESSION_LOW, PREVIOUS_DAY_HIGH,
  PREVIOUS_DAY_LOW, PREVIOUS_WEEK_HIGH, PREVIOUS_WEEK_LOW, CANDLE_HIGH, CANDLE_LOW
- Depends on: a fixed daily/weekly candle rollover convention (see Open Questions — not yet set)
- Depended on by: Reference Level (as one of its implementing methods); Liquidate to Rebalance
  (Strategy Library) is the primary current consumer
- Status: Draft — methods are well-defined individually; the rollover-convention dependency is a
  real open blocker (see Open Questions), and this entry should not be marked Approved until that
  is resolved, since PDH/PDL/session boundaries are meaningless without it

## Definition
This method produces Reference Levels from fixed calendar/session boundaries rather than from
price-pattern detection (contrast with ATR Swing Detection). Nothing here is a judgment call about
price structure — every level type below is a direct read of a specific, named time window's
high or low. This is why these are CALCULATED, not INFERRED, in the same sense ATR swing points are
CALCULATED: the location is a deterministic function of the data and a stated time window, not an
interpretation.

## Method Assumptions
- Per Backlog Notes, this method's reference points were never meant to compete with or be
  reconciled into ATR Swing Detection — they answer a different question (what happened in a
  specific calendar window) rather than the same question by a different method.
- Requires a resolved timezone/rollover convention to be meaningful at all (see Open Questions).
  Nothing below should be implemented until that's settled, or "previous day" is ambiguous.

## Level Types and Their Definitions
- **SESSION_HIGH / SESSION_LOW**: the highest/lowest price traded within a named session window
  (e.g. the Asia session). Session windows are themselves defined in the Strategy Library's time
  brackets (see Backlog Notes — General Rules time bracket definitions), not in this entry, since
  session boundary conventions vary by broker/strategy.
- **PREVIOUS_DAY_HIGH / PREVIOUS_DAY_LOW (PDH/PDL)**: the highest/lowest price traded during the
  immediately preceding daily candle, per whatever daily-candle rollover convention is in force
  (see Open Questions).
- **PREVIOUS_WEEK_HIGH / PREVIOUS_WEEK_LOW (PWH/PWL)**: same as above, at weekly granularity.
- **CANDLE_HIGH / CANDLE_LOW**: the high/low of one specific, named candle on a specific timeframe
  (e.g. Liquidate to Rebalance's "[10:00] 4H candle high/low"). Identified by timeframe + the
  candle's start_time, not by any pattern-detection logic.

## Detection Rule
For each level type, the rule is a direct MAX/MIN over the relevant window:
- SESSION_HIGH = MAX(high) over all candles within the named session's time window
- SESSION_LOW = MIN(low) over the same window
- PREVIOUS_DAY_HIGH = MAX(high) over the prior daily candle (per rollover convention)
- PREVIOUS_DAY_LOW = MIN(low) over the same candle
- PREVIOUS_WEEK_HIGH / LOW = same, at weekly granularity
- CANDLE_HIGH / CANDLE_LOW = the high/low field of the one named candle directly

## Process / State Transition
FORMING (the window/candle is still open; the level can still change) → CLOSED (the window/candle
has closed; the level is now fixed for that instance) → SUPERSEDED (a new instance of the same
level_type — e.g. the next day's PDH — becomes the current one; the prior instance remains a
historical Reference Level but is no longer "the" current PDH)

confirmation_state mapping: FORMING = PROVISIONAL, CLOSED or SUPERSEDED = CONFIRMED. Note (per
Reference Level's Edge Cases) that this meaning is specific to this method and not directly
comparable to ATR Swing Detection's PROVISIONAL/CONFIRMED, which concerns pattern invalidation,
not window closure.

## Output / Result
A Reference Level object (see schema) for each level type, with source_method identifying which
of the level types above produced it. Epistemic status: CALCULATED for the price/level value
itself; any claim that this level constitutes "liquidity" is a separate INFERRED claim made by
Liquidity Pools, not by this entry.

## Edge Cases
- A session/day/week boundary crossing a weekend or holiday needs explicit handling (e.g. what is
  "previous day" on a Monday?) — not yet resolved, see Open Questions.
- Data provider candle boundaries may not align with the intended session/day boundary (e.g. a
  provider's "daily candle" might roll at a different UTC offset than the convention this system
  wants to use) — this needs to be checked against whatever live data provider is eventually used,
  not assumed.

## Relationships
- Implements: Reference Level (produces SESSION_HIGH/LOW, PDH/PDL, PWH/PWL, CANDLE_HIGH/LOW
  instances)
- Primary consumer: Liquidate to Rebalance (Strategy Library), which anchors its entire model to
  Asia range, PDH/L, and the [10:00]/[14:00] 4H candle extremes — all of which are this method,
  not ATR Swing Detection
- Does NOT compete with ATR Swing Detection — see that entry's Relationships section

## Open Questions / Deliberately Deferred
- **Daily/weekly candle rollover convention is intentionally deferred, not simply unresolved.**
  You confirmed this depends on which live forex data API gets selected (stage 4 of the original
  pipeline) — different providers report daily candles with different rollover conventions (some
  roll at 17:00 EST per interbank convention, others at 00:00 UTC), so fixing this now, before a
  provider is chosen, would risk picking a convention that doesn't match the actual data source.
  Action item for whenever the data provider gets selected: check its candle rollover convention
  as a selection criterion, not an afterthought, then come back and set this parameter. This
  blocks Liquidate to Rebalance's Entry Model until then, by design, not by oversight.
- GMT vs. British Summer Time handling for any UK-clock-based session window is not yet
  formalized — see the broader Time Handling item in Backlog Notes (originally flagged in the
  Thoughts and feedback review).
- Weekend/holiday transition handling for "previous day"/"previous week" is not yet defined.
- Session window boundaries themselves (what exactly counts as "the Asia session") are defined in
  the Strategy Library, not here, and those specific time brackets are still only partially
  formalized (see Backlog Notes).
