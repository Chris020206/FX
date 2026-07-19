<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Liquidity Pools

## Metadata
- Path: Domain Model > Liquidation Logic > Liquidity Pools
- Market scope: FX spot (retail)
- Depends on: Buy Order Liquidation, Sell Order Liquidation, Order Types, Reference Level, Internal and External Liquidity
- Depended on by: Liquidity Sweep, (future) Sweep detection
- Status: Draft — zone width and equal-highs tolerance now defined; PASSIVE depth estimation explicitly deferred to Strategy library

## Definition
A liquidity pool is a price zone where a concentration of resting and conditional orders is expected, made up of both orders that will become aggressive (market) orders on trigger and passive orders that provide the opposing side those aggressive orders fill against.

## Market Model Assumptions
- In a centralized/exchange model, some of this concentration may be directly observable via order-book data.
- In the decentralized spot FX market, total order flow across all participants cannot be observed from a single data source. A liquidity pool in this context is therefore an inferred concept (see Observed vs. Inferred below), built from visible price structure and typical participant behavior — not a direct read of the order book.
- This entry treats the two order-flow roles below as distinct because they affect a pool's behavior differently. Conflating them — describing a pool simply as "orders that will execute as market buys/sells" — was a known accuracy gap in the previous version of this entry.

## Inputs / Variables
- zone_bounds: [price_low, price_high], centered on structural_reference, with a total width of
  0.5 × ATR(14) (same ATR parameters as ATR Swing Detection; this is a calibration
  default, pending validation)
- equal_tolerance: two Reference Levels count as "equal highs/lows" if within 0.25 × ATR(14) of
  each other (using ATR Swing Detection's equal-highs handling)
- order_role, one of:
  - AGGRESSIVE_BOUNDED — stop-market orders from existing open positions; size for this role is
    capped by existing open interest at that level
  - AGGRESSIVE_UNBOUNDED — breakout entry orders (new positions opened on trigger); not capped by
    existing open interest, size depends on how many new participants act at the level
  - PASSIVE — resting limit orders (entries, take-profits) that do not trigger on price arrival but
    are available to be matched against; this is the liquidity that AGGRESSIVE orders execute into
- side: buy-side | sell-side
- structural_reference: a CONFIRMED Reference Level (or cluster of equal ones, per
  equal_tolerance), of whichever level_type is contextually appropriate — see Reference Level for
  the full set of types (ATR swing points, session highs/lows, PDH/PDL, consolidation boundaries,
  etc.). This entry no longer assumes ATR-swing detection specifically; any Reference Level type
  can anchor a liquidity pool.

## Trigger Condition
IF current_price enters zone_bounds:
- AGGRESSIVE_BOUNDED and AGGRESSIVE_UNBOUNDED orders on the triggered side fire as market orders
  (subject to stop-market vs. stop-limit behavior defined in Buy/Sell Order Liquidation)
- PASSIVE orders on the opposing side do not fire; they are consumed by the aggressive orders as
  counterparty liquidity

## Process / State Transition
DORMANT (structural reference exists, no price interaction) → PRICE_APPROACHING → ACTIVATED
(current_price within zone_bounds) → AGGRESSIVE orders trigger against PASSIVE orders →
PARTIALLY_CONSUMED | FULLY_CONSUMED → DORMANT (if further structural reference remains) | INVALIDATED

## Output / Result
- Buy-side liquidity (activated): AGGRESSIVE_BOUNDED orders from short-position stop-losses +
  AGGRESSIVE_UNBOUNDED breakout buy orders execute as market buys, filling against PASSIVE
  sell-side limit orders resting in the zone
- Sell-side liquidity (activated): mirror of the above (long-position stop-losses + breakout sell
  orders, filling against PASSIVE buy-side limit orders)
- Magnitude of the resulting burst is a function of AGGRESSIVE order count/density AND available
  PASSIVE order depth — not concentration alone. This corrects an earlier version of this entry,
  which implied concentration alone determines burst size.

## Edge Cases
- Insufficient PASSIVE depth: if aggressive orders outnumber available passive liquidity at the
  zone, price moves through/past the zone rather than absorbing cleanly at it (part of what
  produces the displacement described in Liquidity Sweep)
- Partial activation: price clips the edge of zone_bounds without reaching enough of the
  concentration to fully consume it
- The existence of a visible pool does not imply any participant intentionally caused price to
  reach it — this describes a structural tendency, not a claim about intent

## Relationships
- Sources: Buy Order Liquidation, Sell Order Liquidation (AGGRESSIVE_BOUNDED role)
- Anchored to: structural highs/lows defined in Internal and External Liquidity
- Produces: the activation event modeled in Liquidity Sweep
- A single pool may simultaneously be internal liquidity relative to a larger structure and
  external liquidity relative to a smaller one — see Internal and External Liquidity > Relative
  Nature

## Observed vs. Inferred Liquidity
- Observed liquidity: orders directly visible through a specific data source (e.g., broker-level
  order-flow data, where available).
- Inferred liquidity: an estimated concentration of orders based on visible price structure and
  typical participant behavior (equal highs/lows, consolidation boundaries, common stop
  placement), used when direct order-flow data is unavailable — the default case in decentralized
  spot FX.
- Any algorithmic implementation of this entry should tag its output with which of these two modes
  produced it, since confidence and reliability differ substantially between them.

## Open Questions / Deliberately Deferred
- Structural reference detection and equal-highs tolerance are resolved (see Inputs / Variables
  and Reference Level/ATR Swing Detection).
- PASSIVE order depth estimation remains explicitly out of scope for this entry. It requires
  historical reaction data (e.g. average displacement following past sweeps of similar
  structures), which only exists once the trading journal (stage 3) is populated. This is a
  Strategy library concern, not a Domain Model fact — noted here so the dependency isn't
  lost, not because it's expected to be resolved in this entry.
