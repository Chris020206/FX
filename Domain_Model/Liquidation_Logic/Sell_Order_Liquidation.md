<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Sell Order Liquidation

## Metadata
- Path: Domain Model > Liquidation Logic > Sell Order Liquidation
- Market scope: FX spot (retail)
- Depends on: Order Types, Market Model (STP vs. Market Maker)
- Depended on by: Liquidity Sweep, Liquidity Pools
- Status: Approved

## Definition
Sell order liquidation is the closing of a short position by executing a buy, transferring the notional exposure and realizing profit or loss as the difference between entry and exit price.

**Terminology note**: "liquidation" here means a stop order triggering and executing — not
broker-initiated margin liquidation from insufficient account equity, which is a different event
this system does not model. See Standards/Terminology.md.

## Market Model Assumptions
- STP/ECN model: the buy order is routed to a liquidity provider; counterparty is external.
- Market Maker model: broker is the counterparty; internal fill, no external order book interaction necessarily occurs.
- No asset borrowing/lending model applies here (unlike equity short-selling). A short position in spot FX is a notional exposure recorded in the account ledger, not a borrowed asset that must be returned — this corrects an earlier version of this entry that used the equity short-selling model.
- Applies to both broker models; differences noted in Edge Cases.

## Inputs / Variables
- entry_price, stop_price, direction = short
- order_type: stop-market | stop-limit
- position_size

## Trigger Condition
IF order_type == stop-market AND current_price >= stop_price → trigger unconditional market buy
IF order_type == stop-limit AND current_price >= stop_price → place limit buy at stop_price (may not fill if price gaps above stop_price)

## Process / State Transition
OPEN → TRIGGERED → (stop-market: MARKET_ORDER_SENT | stop-limit: LIMIT_ORDER_PLACED)
→ FILLED (full or partial) | UNFILLED (stop-limit gap case)
→ CLOSED

## Output / Result
- Position size reduced to zero (or partially, on partial fill)
- Realized P&L = (entry_price − fill_price) × position_size
- If unfilled: position remains open, unprotected, exposed further to adverse movement

## Edge Cases
- Slippage: fill_price may differ from stop_price
- Partial fill: insufficient opposing liquidity at stop_price fills only part of position_size
- Stop-limit gap-through: order never fills, position stays open past intended stop
- Market Maker model: broker may internalize at its own quoted price rather than routing externally

## Relationships
- Mirror concept: Buy Order Liquidation
- Aggregates into: Liquidity Sweep
- Feeds: Liquidity Pools (a cluster of these triggered orders is one source of sell-side liquidity)

## Open Questions / Deliberately Deferred
- None for this entry.
