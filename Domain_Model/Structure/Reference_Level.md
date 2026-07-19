<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Reference Level

## Metadata
- Path: Domain Model > Price Structure > Reference Level
- Market scope: FX spot (retail)
- Depends on: none directly — this is an interface/abstraction, not itself a detection method
- Depended on by: Internal and External Liquidity, Liquidity Pools, Liquidity Sweep, all Detection
  Methods (ATR Swing Detection, Session Level Detection, Origin Point Detection)
- Status: Approved
- Object schema: see Object_Schemas/ReferenceLevel.schema.json

## Definition
A Reference Level is any price point or extremum that other Domain Model concepts (structural
ranges, liquidity pools, sweeps) can anchor to. This entry exists specifically to correct an
earlier design mistake: this system previously tried to force one detection method (ATR-based
swing/ZigZag) to serve as the single universal definition of "structural point," when in fact
several genuinely different methods are all producing the same *kind* of thing for different
purposes. Reference Level is the common interface all of them implement, so downstream concepts
can consume "a reference level" without caring which method produced it.

## Why this exists (the problem it fixes)
The original Structural Point Detection entry defined ATR-based ZigZag swing detection and was
treated as *the* definition of a structural high/low. But the Liquidate to Rebalance strategy
anchors to Asia range high/low, previous-day high/low, previous-week high/low, and specific 4H
candle extremes — none of which are ATR-swing points, and none of which should be forced to
become one. These are not competing definitions of the same thing that need to be reconciled into
one method. They are different reference-level types, each useful in different contexts, and
each already fully well-defined by its own rule (a session boundary, a candle extreme, a swing
threshold). Liquidity Pools already implicitly treated "swing high," "equal highs," and "session
high" as different structural_reference types without forcing them into one detector — this entry
just makes that pattern explicit and formal instead of implicit.

## Inputs / Variables
Every Reference Level, regardless of which Detection Method produced it, carries:
- id: unique identifier
- level_type: which kind of reference level this is (enum — see below)
- price: the level's price value
- timeframe: the timeframe it was identified on
- start_time: when the level's underlying data (e.g. the session, the candle, the swing leg) began
- confirmation_state: CONFIRMED | PROVISIONAL (meaning varies by source_method — see each
  Detection Method for what confirmation means in that context)
- source_method: which Detection Method produced this instance (see Detection Methods folder)
- validity_period: how long this level remains a live reference before being superseded or
  expiring (method-dependent; e.g. a session high is valid until that session's range is
  superseded, an ATR swing point is valid until invalidated per its own rule)
- confidence: per the Epistemic Status standard, a float rather than a bare category
- observability: OBSERVED | CALCULATED | INFERRED, per the Epistemic Status standard — a session
  high is CALCULATED (directly derived from the data with no interpretive judgment); its
  classification as "liquidity" is a separate, INFERRED claim made by Liquidity Pools, not by this
  entry

## Level Types (extensible enum)
- ATR_SWING_HIGH / ATR_SWING_LOW — produced by Detection_Methods/ATR_Swing_Detection.md
- SESSION_HIGH / SESSION_LOW — produced by Detection_Methods/Session_Level_Detection.md (e.g.
  Asia session range)
- PREVIOUS_DAY_HIGH / PREVIOUS_DAY_LOW (PDH/PDL) — produced by Detection_Methods/Session_Level_Detection.md
- PREVIOUS_WEEK_HIGH / PREVIOUS_WEEK_LOW (PWH/PWL) — produced by Detection_Methods/Session_Level_Detection.md
- CANDLE_HIGH / CANDLE_LOW — a specific candle's extreme (e.g. the [10:00] 4H candle in Liquidate
  to Rebalance) — produced by Detection_Methods/Session_Level_Detection.md
- EQUAL_HIGHS_ZONE / EQUAL_LOWS_ZONE — a cluster of near-equal highs/lows within the tolerance
  defined in Liquidity Pools/Inefficiency — produced by Detection_Methods/ATR_Swing_Detection.md
  (uses the same equal_tolerance parameter)
This list is extensible — new Detection Methods can introduce new level_type values without
requiring changes to this entry or to anything that consumes Reference Levels generically.

## Trigger Condition
Not applicable at this entry's level — each Detection Method defines its own trigger/creation
condition. This entry only defines the shape every result must conform to.

## Output / Result
A Reference Level object (see schema) that downstream entries (Internal and External Liquidity's
structural_range, Liquidity Pools' structural_reference, Liquidity Sweep's opposing_pool/target_pool
anchoring) can consume without needing to know or care which Detection Method produced it.

## Edge Cases
- Two Detection Methods can, in principle, produce overlapping or coincident Reference Levels
  (e.g. a session high that happens to coincide with an ATR swing high). No merging/deduplication
  logic is defined here — each is tracked as its own independent Reference Level with its own
  source_method, consistent with how Inefficiency handles overlapping gaps (tracked independently,
  not merged).
- confirmation_state's meaning is method-dependent and NOT interchangeable across level_types — a
  PROVISIONAL ATR swing point and a session-based level currently being formed are both
  "unconfirmed" in a loose sense, but for different structural reasons. Consumers should not treat
  confirmation_state as directly comparable across level_types without checking source_method.

## Relationships
- Every downstream entry that previously said "structural point" or "structural reference" now
  means "a Reference Level, of whichever level_type is contextually appropriate" — Internal and
  External Liquidity, Liquidity Pools, and Liquidity Sweep have been updated to reflect this.
- Detection Methods are the only things that create Reference Level instances; this entry never
  creates one directly.

## Open Questions / Deliberately Deferred
- No cross-method deduplication/reconciliation logic when two methods produce coincident levels.
- Whether some level_types should be preferred over others when multiple apply to the same
  price/time (e.g. is a session high a stronger reference than a coincident ATR swing high?) —
  not addressed; likely a Strategy library concern (which level_type a given strategy actually
  cares about) rather than a Domain Model fact.
