<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Pre-News Scalp Rule

## Metadata
- Path: Strategy Library > General Trading Rules > Pre-News Scalp Rule
- Market scope: FX spot, GBP/JPY-oriented
- Depends on: none from Domain Model — this is a position-management rule, not a market
  mechanism
- Status: Confirmed hard rule (applies under all circumstances, per original framing)
- Note: this is the first Strategy library entry. No formal Strategy entry template has been
  agreed yet (that was a Domain Model concept) — this uses a lightweight version of the
  same structure for consistency, pending an actual Strategy template discussion.

## Rule
Any position opened during the London session prior to 13:30 UK time, on a day with a major
news release scheduled at 13:30 (e.g. interest rate decisions), must be treated as a scalp and
closed before the news release occurs.

## Rationale
Major 13:30 UK releases (commonly interest rate decisions, among others) can produce volatility
that invalidates the basis a pre-news position was opened on. Treating any such position as a
scalp — closed before the release rather than held through it — avoids exposure to that
event-driven move regardless of the position's original intended timeframe.

## Trigger Condition
IF a position is opened during the London session AND current_date has a major news release
scheduled at 13:30 UK time → position.intended_duration is overridden to SCALP, and the position
must be closed before 13:30

## Open Questions / Deliberately Deferred
- Exact list of "major news" categorized here vs. general news-day exclusions (the Liquidate to
  Rebalance model separately excludes Inflation/GDP/NFP days entirely) — not yet reconciled
  against this rule; may be the same list or a narrower one specific to 13:30 releases.
- Whether this applies only to GBP/JPY-relevant releases (UK, and JPY/BoJ-relevant) or any major
  release regardless of currency relevance.
