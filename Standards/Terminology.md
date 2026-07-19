<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Terminology Standard

## "Liquidation" — strategy usage vs. margin usage
This system uses "liquidation" throughout to mean a stop order (or cluster of them) triggering
and executing. That is NOT the only meaning of the word in retail FX, and the two should not be
confused by a future developer, model, or data source reading these documents.

- **Strategy liquidation** (this system's usage, throughout Buy Order Liquidation, Sell Order
  Liquidation, Liquidity Pools, Liquidity Sweep): the execution of clustered protective or
  forced-closing stop orders around a designated price region, triggered by price reaching a
  level — an event about price and resting orders, independent of any single account's equity.
- **Margin liquidation** (NOT modeled anywhere in this system currently): a broker-initiated
  forced closure of a position caused by insufficient account equity to support it. This can
  happen at a price level unrelated to where any stop was placed, and is driven by account-level
  equity/margin, not by price reaching a specific resting order.

Every Domain Model entry using "liquidation" is using the strategy sense. This document exists so
that sense is stated once, explicitly, rather than assumed. Entries are not being renamed
(Buy Order Liquidation / Sell Order Liquidation keep their names) to avoid another cross-reference
rename cascade, per the same reasoning that led to keeping Liquidity Sweep's name rather than
renaming it after the Market-Wide Liquidation Process merge — the cost of renaming stable,
already-approved entries outweighs the benefit here, given the meaning is now stated explicitly
in this standard.
