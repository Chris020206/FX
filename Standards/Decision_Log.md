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
