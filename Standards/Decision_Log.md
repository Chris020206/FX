<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Decision Log

## Purpose
This document records deliberate decisions to *not* build something, or to simplify away from an
originally-planned approach — specifically so that a future reader (you, an AI reading this
project fresh, or anyone else) doesn't rediscover the gap, assume it's an oversight, and either
re-solve a problem that was already deliberately set aside, or waste time confused about why a
field/dependency is missing. Every entry states: what was considered, what was decided instead,
why, and what would have to change for the decision to be worth revisiting.

This is different from Backlog_Notes.md, which tracks things still actively unresolved and
expected to change soon. Entries here are considered settled unless a stated trigger condition
occurs.

---

## Decision: No automated bank holiday check

**Date/context**: raised while formalizing Strategy Library General Rules, after researching
whether economic calendar APIs include bank holiday data (they generally don't — that's a
separate product category, e.g. dedicated exchange/market holiday APIs vs. economic-event
calendars).

**What was considered**: implementing "no trades on bank holidays" (originally listed as a hard
rule in the very first General Trading Rules draft of this project) as a computed `HARD_GATE`,
requiring either a dedicated market-holiday API/data source (since UK + Japan holidays are both
relevant for GBP/JPY, and both shift dates yearly) or a hardcoded holiday list (rejected early —
requires manual annual maintenance and fails silently if forgotten).

**What was decided instead**: drop this as a computed rule entirely. No `is_bank_holiday` field,
no holiday-calendar data source, no dependency on economic calendar or exchange-holiday APIs for
this purpose.

**Why**: the `HARD_GATE` pattern exists to gate a system that might otherwise act without a human
looking first. But this system is checked by a person (via the Companion Interface), not acting
autonomously — the person is already the filter. You've stated you would never look at the market
with intent to trade on a bank holiday regardless of what the system says. A computed gate would
be solving a problem that doesn't exist given how this is actually used. "No trades on bank
holidays" becomes an operational habit (you simply don't open the companion that day), not
something the system enforces.

**What this forecloses (acknowledged, not currently relevant)**: if this system ever became more
autonomous — e.g. an unattended alerting system, or automated execution without a human checking
first — a real holiday check would become necessary again, and this decision would need
revisiting at that point, not before. This is explicitly a "far away" consideration per your own
framing, not something to build toward now.

**Known related, smaller exposure (already flagged elsewhere, not a reason to reverse this
decision)**: historical backtesting (Validation/Backtest_Protocol.md) will replay data that
includes holiday-thin trading days unfiltered, which could produce some low-quality candidates
in a backtest run. The existing "Data error" label in Validation/Labeling_Guide.md is sufficient
to absorb this if it comes up — it doesn't justify building holiday detection for live use.

**Trigger to revisit**: the system moves from "checked by a person" to "acts or alerts
autonomously without a person looking first." Absent that, this stays decided.

---

## Decision: A third, reserved data tier held back for testing code (not just rules)

**Date/context**: raised while preparing to test 3:50 Scalp's detection logic against new GBP/JPY
data, once real UNIX-stamped CSVs were ready to go.

**What was considered**: whether the new data being provided for testing should all be used now,
in one pass.

**What was decided instead**: split the new data into two tiers, not one:
1. Data used now, for the "blind detection" test of the documented rules (Option 1 from that
   conversation — independently finding setups using Origin Point Detection, Mitigation, etc.,
   with no hints, then comparing against known-good dates).
2. A further slice held back entirely, not sent yet, reserved specifically for testing the actual
   *code* once it exists (stage 6 of the original pipeline). This is deliberately different from
   tier 1: tier 1 tests whether the documented logic is correct when a person (me) applies it by
   reading charts. It cannot catch bugs introduced when that logic gets translated into running
   code — a subtlety that reads fine in prose can still get mistranslated into an off-by-one error
   or similar. Only a dataset untouched by both calibration and the manual logic test can honestly
   test that translation step later.

**Why the reserved tier isn't just sent now with a "don't look yet" note**: loose instructions not
to look are weaker than genuinely not having the data yet. The reserved slice should not be
uploaded to this project at all until the coding phase exists and is ready to be tested.

**What this means practically**: when more GBP/JPY 5m CSVs are provided from here going forward,
check whether they're meant for (a) the current blind-detection test, or (b) the reserved
code-testing tier, before treating them as available to use. Don't assume all provided data is
immediately fair game.

**Trigger to revisit**: real detection/trade-management code exists and is ready to be tested
end-to-end. At that point, the reserved tier gets used for exactly that, and this decision is
fulfilled rather than reversed.

---

## 2026-07-26 — M1 gate scoped to display-window agreement (not bit-identical)

**What was considered.** The pre-committed M1 gate (`ROADMAP.md`, `NEXT_STEP.md`) required the
Python port to reproduce the Pine's boxes exactly — origin bar, both bounds, direction, `isV2` —
for **every** box over the Tier 1 span, with disagreements enumerated individually. Gate steps 2–3
were run for the first time on 2026-07-26 (full span, real warmup, port fed the Pine's own OHLC;
see `Implementation/RECONCILIATION_M1.md`). Result: 845 boxes agree exactly, **281 disagree**, so
the gate as written does not pass.

**What was decided instead.** The trader ruled that bit-identity on **off-session** boxes is too
strict, because the strategy only ever sees boxes that are **live during the display window**
(visible on ≥1 bar whose open is in 15:15–16:15 Europe/London). The gate is therefore scoped to
that set: the port must reproduce the Pine's boxes (origin, bounds, direction, `isV2`) for every
**window-live** box; off-session divergences are enumerated in
`Implementation/output/pine_vs_port_reconciliation.csv` and accepted as out of scope.

The relevance test is the *live-in-window* criterion, **not** origin-in-window — Variation-1 setups
form before the window and mitigate inside it, so an origin-time filter would wrongly exclude them.

**Why.** Of the 281 divergences, 222 are off-session marginal-gate flicker on boxes the strategy
never displays or trades, and are sensitive to sub-pip feed revisions between the gate CSV and a
live TradingView export. Requiring bit-identity there tests behaviour the strategy does not use.

**Honesty guard — this is scope refinement, not moving the goalposts to pass.** It was decided
*after* seeing results, so it is recorded explicitly here rather than silently edited into the
gate. Crucially, **it does not make M1 pass.** On the scoped (window-live) set there are still
**32 disagreements**: 5 boxes the port misses, 1 it invents (all marginal displacement/min-zone
gate cases), and 26 `isV2` over-flags (one root cause — see below). Those 32 are the M1 punch list;
the original 281-row enumeration is preserved in the CSV and is not deleted.

**What is genuinely established (not waived).** Zero bounds mismatches anywhere (geometry is a
faithful port); all 9 FULL_5M labelled examples agree exactly.

**`isV2` root cause (partially open).** The Pine's emitted `isV2` tracks the V2 *creation path*
(structural sweep pattern), not window membership as its own source comment states; the port sets
`isV2` from window membership and over-flags in-window pivot boxes. Direction is evidenced (23/26);
the exact `barOffset` assignment on the delayed/pending path is **not yet traced** and must be read
from `createOB` against `pine_port.py` before the fix — do not infer it.

**Trigger to revisit.** (a) The `isV2` and displacement-gate punch-list items are fixed and the
window-live set reaches full agreement; or (b) a clean single-feed full-span export removes the
~700 off-session feed-revision bars, at which point the off-session divergence count should be
re-measured rather than assumed.
