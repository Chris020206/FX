<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Risk Management

## Metadata
- Path: Strategy Library > General Rules > Risk Management
- Status: Confirmed — portfolio-wide, not strategy-specific
- Note: originally drafted inside Three_Fifty_Scalp's Risk section, then moved here once it
  became clear both rules only make sense across multiple strategies, not within a single
  once-a-day setup. Same reasoning as Pre_News_Scalp_Rule's placement.

## Rules

[HARD_GATE] Position size = 0.5% of account equity per trade, sized from that trade's own
stop-loss distance (stop distance is defined per-strategy — e.g. Three_Fifty_Scalp's origin_point
+ 3 pips convention).

[HARD_GATE] Maximum 3 trades per day, across all strategies combined. This is a portfolio-wide
cap, not a per-strategy limit — it only becomes a meaningful constraint once more than one
strategy can generate a setup on the same day (e.g. once Liquidate to Rebalance or others are
also live). A strategy that only fires once a day by its own structure (like Three_Fifty_Scalp)
won't hit this cap on its own.

## Relationships
- Applicable to: any Strategy Library entry that opens positions. Three_Fifty_Scalp's Risk
  section references this rule rather than restating it.

## Open Questions / Deliberately Deferred
- Whether "3 trades" counts attempts (including ones stopped out quickly) or only fully-managed
  trades through to exit — not yet specified.
- Whether the 3-trade cap resets daily on a fixed session boundary or a rolling 24h window — ties
  into the same daily/weekly rollover convention question already open in Session Level Detection.
