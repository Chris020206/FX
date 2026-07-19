<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Buy Order Liquidation

## Metadata
- Path: Domain Model > Liquidation Logic > Buy Order Liquidation
- Market scope: FX spot (retail)
- Depends on: Order Types, Market Model (STP vs. Market Maker)
- Depended on by: Liquidity Sweep, Liquidity Pools
- Status: Approved

## Definition
Buy order liquidation is the closing of a long position by executing a sell, transferring the notional exposure and realizing profit or loss as the difference between entry and exit price.

**Terminology note**: "liquidation" here means a stop order triggering and executing — not
broker-initiated margin liquidation from insufficient account equity, which is a different event
this system does not model. See Standards/Terminology.md.

## Market Model Assumptions
- STP/ECN model: the sell order is routed to a liquidity provider; the counterparty is external and may be another trader, bank, or LP inventory.
- Market Maker model: the broker itself is the counterparty; "matching" is internal and no external order book interaction necessarily occurs.
- This entry applies to both; where they differ, it's noted in Edge Cases.

## Inputs / Variables
- entry_price, stop_price, direction = long
- order_type: stop-market | stop-limit
- position_size

## Trigger Condition
IF order_type == stop-market AND current_price <= stop_price → trigger unconditional market sell
IF order_type == stop-limit AND current_price <= stop_price → place limit sell at stop_price (may not fill if price gaps below stop_price)

## Process / State Transition
OPEN → TRIGGERED → (stop-market: MARKET_ORDER_SENT | stop-limit: LIMIT_ORDER_PLACED)
→ FILLED (full or partial) | UNFILLED (stop-limit only, if price gapped past limit)
→ CLOSED

## Output / Result
- Position size reduced to zero (or partially, on partial fill)
- Realized P&L = (fill_price − entry_price) × position_size
- If unfilled (stop-limit gap case): position remains open, unprotected

## Edge Cases
- Slippage: fill_price may differ from stop_price, especially stop-market during fast moves
- Partial fill: insufficient opposing liquidity at stop_price fills only part of position_size
- Stop-limit gap-through: order never fills, position stays open past intended stop
- Market Maker model: no true "matching" — broker may internalize at its own quoted price

## Relationships
- Mirror concept: Sell Order Liquidation (short-side equivalent)
- Aggregates into: Liquidity Sweep, when many Buy Order Liquidations cluster at similar stop_price levels
- Feeds: Liquidity Pools (a cluster of these triggered orders is one source of buy-side liquidity)

## Open Questions / Deliberately Deferred
- None for this entry.
