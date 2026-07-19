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

[HARD_GATE] Every trade must carry an explicit `risk_pct`, and that value must fall within
`RISK_PCT_MIN` .. `RISK_PCT_MAX`. Position size is then computed from `risk_pct` and that trade's
own stop-loss distance (stop distance is defined per-strategy — e.g. Three_Fifty_Scalp's
origin_point + 3 pips convention).

The gate is on the *presence and bounds* of `risk_pct`, not on a fixed number. A hardcoded
percentage was rejected: different strategies warrant different sizing, and conviction on a given
setup legitimately varies.

| Parameter | Value | Notes |
|---|---|---|
| `RISK_PCT_MIN` | 0.25 | floor |
| `RISK_PCT_DEFAULT` | 0.5 | applied when nothing is specified |
| `RISK_PCT_MAX` | 1.0 | ceiling; requires an explicit override, never silent |

Resolution order: explicit per-trade value -> strategy default (Strategy Library entry) ->
`RISK_PCT_DEFAULT`. Any value above the default must be set deliberately and is recorded on the
trade record with its reason, so that post-hoc analysis can separate "this strategy performs
well" from "I sized up on the ones that happened to work".

[HARD_GATE] Maximum 3 trades per day, across all strategies combined. This is a portfolio-wide
cap, not a per-strategy limit — it only becomes a meaningful constraint once more than one
strategy can generate a setup on the same day (e.g. once Liquidate to Rebalance or others are
also live). A strategy that only fires once a day by its own structure (like Three_Fifty_Scalp)
won't hit this cap on its own.

## Relationships
- Applicable to: any Strategy Library entry that opens positions. Three_Fifty_Scalp's Risk
  section references this rule rather than restating it.

## Open Questions / Deliberately Deferred
- Whether conviction-based sizing above `RISK_PCT_DEFAULT` should require a recorded justification
  from a fixed list, or free text. Free text for now.
- Whether the 3-trade daily cap should scale with `risk_pct` (three 1.0% trades is four times the
  exposure of three 0.25% trades). Currently it does not.
- Whether "3 trades" counts attempts (including ones stopped out quickly) or only fully-managed
  trades through to exit — not yet specified.
- Whether the 3-trade cap resets daily on a fixed session boundary or a rolling 24h window — ties
  into the same daily/weekly rollover convention question already open in Session Level Detection.
