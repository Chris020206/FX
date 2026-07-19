<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: RECONCILIATION PENDING**
>
> - Zone vocabulary here predates FULL_5M / WIDENED_15M / REFINED_HTF_PUSH. The REFINED_HTF_PUSH construction is not described by any detection method in this folder.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Origin Point Detection

## Metadata
- Path: Detection Methods > Origin Point Detection
- Market scope: FX spot (retail)
- Produces: OriginPoint objects (see Object_Schemas/OriginPoint.schema.json)
- Depends on: Liquidity Sweep (an origin_point only exists relative to a confirmed sweep),
  Inefficiency (primary qualifying-impulse rule), ATR Swing Detection (fallback qualifying-impulse
  rule and zone-width reasoning)
- Depended on by: Mitigation, Efficient Price, Liquidity Sweep (which previously only referenced
  origin_point narratively)
- Status: Draft — zone boundary convention confirmed (full wick range); double-licky candle
  handling and lower/higher-timeframe tiers now specified; sizing safeguard threshold adopted as
  default pending possible revision

## Definition
An origin_point is the specific candle (and its price zone) that marks where a market maker's
leftover position from a confirmed Liquidity Sweep is presumed to have been established — the
last candle on the swept side, immediately before the impulsive reversal leg begins. This entry
formalizes what was previously only defined narratively in Liquidity Sweep ("the last opposing
candle before the impulse") into a precise, computable rule with explicit handling for the cases
that narrative definition couldn't resolve on its own.

Epistemic status: the candle/zone identification below is CALCULATED (deterministic, given the
rules stated). The claim that this zone represents a market maker's actual leftover position is
INFERRED — see Efficient_Price.md and Mitigation.md, and the Epistemic Status standard.

## Required Input
- A confirmed SWEEP classification from Liquidity Sweep (i.e., current_price entered
  opposing_pool.zone_bounds and subsequently CLOSED back outside it, per that entry's Trigger
  Condition) — origin_point detection never runs independently of a confirmed sweep
- The candle sequence spanning from the last candle still within/before opposing_pool.zone_bounds
  through the candles of the impulsive reversal leg, on the timeframe the sweep was identified on
  (origin_point's own timeframe can be lower than the sweep's reference_timeframe — e.g. a 1m
  origin_point within an H1-identified sweep, matching how these are typically read in practice)

## Qualifying Impulse Definition
The reversal leg following a confirmed sweep must qualify as "impulsive" before an origin_point
is marked at all — not every confirmed sweep necessarily produces a strong enough move to
identify one cleanly. Two rules, tried in order:

1. **Primary rule (gap-based)**: IF the reversal leg produces a qualifying Inefficiency (per
   Inefficiency's own detection rule — a 3-candle gap exceeding ATR(14) on the relevant
   timeframe) → the leg qualifies as impulsive, and origin_point is anchored to that
   Inefficiency's c1 (per Inefficiency's own note that origin_point is analogous to its c1).
2. **Fallback rule (no gap formed)**: IF no qualifying gap forms, but price displaces at least
   swing_threshold (k × ATR(n), the same parameters as ATR Swing Detection: k=1.5, n=14) within
   3 consecutive candles closing in the reversal direction → the leg still qualifies as
   impulsive, using this displacement rule instead of a gap.
3. IF neither rule is satisfied → no origin_point is marked for this sweep. The sweep is still a
   valid SWEEP per Liquidity Sweep's own criteria, but this system does not track a leftover
   position for it (Mitigation has nothing to track in this case).

## Candidate Selection Rule
Given a qualifying impulsive leg (by either rule above), the origin_point candle is the LAST
candle, immediately preceding the first candle of that impulsive leg, whose close is still on the
pre-reversal (swept) side of opposing_pool's near boundary. If several consecutive candles are all
on the swept side before the impulse begins (a choppy pre-reversal stretch), the origin_point is
the one closest to the impulse — not the first one in that run — since it's the position
established right before the move away, per the original explanation of the mechanism.

## Zone Boundaries
**Resolved and confirmed**: origin_point.zone = the FULL high-to-low range (wick to wick) of the
selected candle, not body-only. Confirmed against your own trading practice.
- lower_bound = origin candle's low
- upper_bound = origin candle's high

See Double-Licky Candle Handling below for the case where the "selected candle" itself isn't a
single clean candle and needs refinement via a lower timeframe.

## Double-Licky Candle Handling
A "double-licky candle" (your term) is a single candle on the signal timeframe that itself sweeps
both sides — its wick takes out the swept-side extreme AND its own range already shows part of
the reversal — making the Candidate Selection Rule above ambiguous about which single candle is
"the" origin, since one candle is doing the job of two.

**Worked example (your illustration, 15m):**
```
Candle 1: O=7, L=4, C=5, H=9
Candle 2: O=5, L=3, C=8, H=10
```
Candle 2 undercuts Candle 1's low (3 < 4) — a sweep of the downside — while also closing well up
into what would be reversal territory (C=8, most of the way to H=10). This single candle is
simultaneously the sweep and most of the reversal, so it can't be cleanly split into "swept
candle" vs. "impulse candle" the way the base Candidate Selection Rule assumes.

**Resolution — drill down exactly one timeframe level, no further:**
Refine using the next-lower timeframe's composition of that same candle. Continuing your example,
the 15m Candle 2 above might decompose on the 5m chart as:
```
Candle 1: O=7, L=4, C=5, H=9
Candle 2: O=5, L=3, C=6, H=8
Candle 3: O=6, L=5, C=11, H=13
```
Here, the 5m Candle 2 is the true origin candle — it's the one whose low (3) actually undercuts
the prior low (4), establishing the new extreme; Candle 3 is where the impulsive reversal actually
begins. This mirrors the top-level Candidate Selection Rule exactly, just applied one level down.

**The cutoff (why this doesn't recurse infinitely):** you could keep drilling into the 5m Candle 2
on a 1m chart and find an even more "precise" origin, and then a tick chart below that, with no
natural stopping point. The rule is: **drill down exactly one level, never more** — 15m signal →
5m refinement, stop (do not go to 1m). This is a deliberate, somewhat arbitrary cutoff, same as
this system's other calibration defaults (ATR period, swing multiplier) — chosen for practicality,
not derived.

**Sizing safeguard**: per your note, the refined (5m) zone shouldn't be accepted if it's a
negligible sliver relative to the original (15m) candle — a technically-more-precise but
practically-meaningless zone. Default rule (your first suggested option, adopted since it has a
single clear reference point): the refined zone must be at least 50% of the parent candle's
range; if it's smaller than that, fall back to using the full parent (15m) candle's wick-to-wick
range as the origin zone instead of the smaller 5m one. Your alternative suggestion (require the
child candle's own range to be at least 75% of some reference) is noted as a documented
alternative, not adopted as default — flagged in Open Questions in case you'd rather switch.

Independent confirmation: the AR_Order_Block indicator you linked defines a valid order block via
three conditions — Liquidity Grab, Imbalance formation, No mitigation yet — which is the same
three-part composite this system already requires (a confirmed Liquidity Sweep + a qualifying
Inefficiency + tracked, not-yet-MITIGATED state), independently arrived at.

## Origin Point Tiers: Lower-Timeframe (Entry) vs. Higher-Timeframe (Context)
Your explanation describes two distinct uses of origin_point, not one:

- **LOWER_TIMEFRAME tier** — everything above (15m→5m drill-down, etc.) is this tier: tied
  directly to entries. The origin_point is the actual level a trade is planned around.
- **HIGHER_TIMEFRAME tier** — same underlying principle, applied at 4H→1H instead of 15m→5m
  (never further down than 1H for this tier). This tier is NOT tied to a specific entry — it's
  used to gauge where a continuation or reversal might occur at a broader structural level,
  functioning more like a directional-bias marker than a trade trigger. Two detection paths, per
  your description:
  1. Mark out the 4H Inefficiency directly (manual method), or
  2. Drill to the 1H chart and find the relevant origin candle there — the last candle that
     exceeded the previous low (bullish case) or previous high (bearish case) — using the same
     Candidate Selection Rule as the lower tier, just at 4H→1H instead of 15m→5m, and mark that
     entire candle wick-to-wick.

Both tiers use the same OriginPoint object shape (see schema) but should carry a `tier` field
(LOWER_TIMEFRAME | HIGHER_TIMEFRAME) so downstream consumers don't accidentally treat a
context-only 4H/1H origin_point as if it were an entry-grade signal, or vice versa. This
directly matters for Efficient Price's 4H+ precondition check, which should specifically read
HIGHER_TIMEFRAME-tier origin_points, not LOWER_TIMEFRAME ones.

## Confirmation Rule
- origin_point is created in state PROVISIONAL as soon as it's identified (immediately after the
  qualifying impulse rule is satisfied)
- origin_point transitions to CONFIRMED once the impulsive leg's qualifying condition (gap fully
  formed, or displacement threshold reached) is itself finalized — for the gap-based rule, this
  is when c3 closes (completing the 3-candle pattern); for the displacement rule, this is when
  the third consecutive reversal-direction candle closes
- IF price re-enters and closes back through origin_point.zone (i.e., invalidating the reversal)
  before the qualifying condition finalizes → the candidate origin_point is discarded, never
  reaching CONFIRMED. This is a genuine fakeout case, not an edge case to special-case around.

## Invalidation Rule (distinct from Mitigation's MITIGATED state)
An origin_point, once CONFIRMED, becomes INVALIDATED if a later candle CLOSES beyond the FAR
boundary of its zone (i.e., price fully reclaims through the entire zone, exiting on the opposite
side from where the impulse originated) — not merely returning into the zone, which is Mitigation's
concern instead. This is a structural claim (the level has been fully negated, not just revisited)
and is distinct from MITIGATED (per Mitigation.md, which can be satisfied by a partial or full
return without necessarily closing past the far boundary). An origin_point can reach MITIGATED
without ever reaching INVALIDATED, and in the ordinary case (per your original explanation, where
price returns to close the leftover position) that's exactly what should happen — INVALIDATED is
the harder-negation case where the level stops mattering structurally altogether.

## Multi-Candidate Handling
Only one origin_point is created per confirmed sweep, per the Candidate Selection Rule above (the
closest qualifying candle to the impulse, not every candle on the swept side). If a strategy needs
to consider multiple nested origin_points across timeframes (e.g. a 1m origin_point inside a
larger H1 sweep's own origin_point), those are tracked as separate OriginPoint objects, each with
its own timeframe and associated_sweep_id — no merging logic between timeframes is defined here.

## Timestamp Behavior
- source_candle_start = the open time of the selected origin candle, in UTC (see Standards —
  Time Handling, a separate open item; all timestamps in the object schema are UTC regardless of
  what timeframe/session language a Strategy Library entry uses to describe when to look)
- timeframe = the timeframe the origin candle itself was identified on (may differ from the
  sweep's reference_timeframe, as noted under Required Input)

## Output / Result
An OriginPoint object per the schema, with: id, direction, lower_bound, upper_bound,
source_candle_start, timeframe, tier (LOWER_TIMEFRAME | HIGHER_TIMEFRAME — see Origin Point Tiers
above), detection_method (which of the two qualifying-impulse rules applied), confirmation_state
(PROVISIONAL | CONFIRMED | INVALIDATED — note this is a three-value state here, not the two-value
CONFIRMED/PROVISIONAL used by ATR Swing Detection), and associated_sweep_id linking back to the
Liquidity Sweep instance that produced it.

## Edge Cases
- No qualifying impulse (neither gap nor displacement threshold met): no origin_point is created;
  this is expected, not an error — see Qualifying Impulse Definition, rule 3
- Fakeout before confirmation: candidate discarded, never reaches CONFIRMED — see Confirmation Rule
- Double-licky candles (a single candle sweeping both sides): resolved via one-level drill-down —
  see Double-Licky Candle Handling above

## Relationships
- Created by: a confirmed Liquidity Sweep instance (via associated_sweep_id)
- Consumed by: Mitigation (tracks approach_depth against this zone), Efficient Price (requires
  this entry's MITIGATED-tracked instance to reach MITIGATED as half of its own condition)
- Distinct from: Mitigation's MITIGATED state and this entry's own INVALIDATED state — see
  Invalidation Rule above for how they differ

## Open Questions / Deliberately Deferred
- Sizing safeguard threshold: adopted 50%-of-parent as default per your first suggested option;
  your alternative (75% of the child candle's own range against some reference) is a documented
  option not currently adopted — flag if you'd rather switch.
- Interaction between INVALIDATED (this entry) and MITIGATED (Mitigation) hasn't been tested
  against real price action to see how often they diverge in practice
- Nested multi-timeframe origin_points (e.g. 1m origin_point inside an H1 sweep) are tracked
  independently with no reconciliation logic — same approach as Inefficiency's nested-gap handling
- HIGHER_TIMEFRAME tier's two detection paths (manual 4H Inefficiency marking vs. 1H origin
  candle rule) aren't yet reconciled into one preferred method — both are stated as valid per your
  description, not yet tested against each other for agreement
