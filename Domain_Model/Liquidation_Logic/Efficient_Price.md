<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Efficient Price

## Metadata
- Path: Domain Model > Liquidation Logic > Efficient Price
- Market scope: FX spot (retail)
- Depends on: Inefficiency (Imbalance), Mitigation, Liquidity Sweep, Liquidity Pools (the
  pre-existing pool this entry describes as becoming unblocked)
  (NOTE: this creates a real conceptual cycle with Liquidity Sweep, which depends on this entry
  for its precondition. Intentional — see Domain_Model/Event_Model.md for the acyclic software
  implementation via Events/Trackers/Evaluators.)
- Depended on by: Liquidity Sweep (generalizes its precondition), Strategy library entries that
  check whether both mitigation and gap-fill conditions are satisfied together before treating a
  setup as valid (e.g. Liquidate to Rebalance, which uses the phrase "mitigated and efficient" in
  its own source material to describe exactly this combined check)
- Status: Draft — core rule defined and confirmed (full-fill required, no partial-fill exception)

## Definition (computable)
Efficient Price is a derived state assigned to a price region when its associated Inefficiency
has reached FULLY_FILLED AND its associated origin_point (tracked by Mitigation) has reached
MITIGATED. This is fully testable against the two component states — see Trigger Condition below.

## Epistemic Status (per the Epistemic Status standard)
- **Definition above (CALCULATED)**: `FULLY_FILLED AND MITIGATED` is a deterministic function of
  two other tracked states. Not in question.
- **Model interpretation (INFERRED)**: under this system's strategy model, once both conditions
  hold, the prior setup is considered resolved and no longer treated as an active price objective
  — the pre-existing liquidity pool at that structural level (per Liquidity Pools — it was always
  there, not created by this entry) is no longer entangled with unresolved business from the prior
  move, and becomes available as a clean target for a future Liquidity Sweep. This is this
  system's causal story for *why* the state matters, not a directly observable fact — a
  three/two-state computation doesn't, by itself, prove anything about market maker behavior or
  institutional interest.
- **Strategy hypothesis (HEURISTIC, UNVALIDATED)**: a resolved structural level (EFFICIENT) may be
  treated as eligible for classification as a future liquidity target, and — per the corrected
  mechanism below — the pool doesn't need to be rediscovered, since it was already there.
- **Validation status**: UNVALIDATED. Whether "EFFICIENT" actually predicts anything about future
  price behavior (vs. being a plausible-sounding but inert label) hasn't been checked against
  labeled historical data — see the Validation folder.

## Model Interpretation, in detail
Correction to an earlier version of this entry: efficiency does NOT cause new liquidity pools to
form. The liquidity pool (resting stops and breakout orders, per Liquidity Pools) already exists
at the structural level in question — it's the ordinary consequence of that level being a
structural high/low in the first place. What efficiency describes is the region losing its
*prior* entanglement: while an inefficiency or an unmitigated origin_point still sits at that
level, the pool there is, under this model, "occupied" by unresolved business from the previous
move, not yet a clean target. Once both resolve, the pre-existing pool is, under this model,
unobstructed and becomes the next viable target for a Liquidity Sweep — the pool wasn't created by
becoming efficient, it was revealed/activated by no longer being blocked. All of this is Model
Interpretation (INFERRED), not a restatement of the computable Definition above.

Concretely, in a bearish leg: the impulsive down-move happened because there wasn't enough
liquidity at the intervening prices to fill all resting orders, so price ran to find it —
leaving an inefficiency (unfilled orders sitting in the gap, waiting for price to return with
new participants) and an unmitigated origin_point (the market maker's own leftover position).
Once both are resolved, what remains at the highs of that bearish leg is the ordinary trailing
buy-side liquidity (stops from trapped shorts, breakout buy orders) that was always going to sit
there structurally — now with nothing else in the way.

## Second cause of gap formation (not this entry's concern)
Per Inefficiency's Edge Cases, a gap can also form during genuinely sparse-liquidity periods
(session turnover, dead hours) without any sweep/reversal behind it. This entry's Liquidity
Sweep-driven mechanism above is the primary case; the sparse-liquidity case is a recognized
exception, not separately modeled here.

## Market Model Assumptions
- Ties directly to the Inferred nature of "institutional interest" established in Liquidity
  Pools' Observed vs. Inferred section — efficiency is a statement about the model's own
  assumption resetting, not a claim about anything directly observed in order flow.
- Assumes the associated Inefficiency and the associated origin_point, when they co-occur (per
  their existing Relationships sections), are evaluated together as a pair tied to the same
  originating Liquidity Sweep instance — not independently.

## Inputs / Variables
- associated_inefficiency: an Inefficiency instance tied to a given Liquidity Sweep
- associated_origin_point: the Mitigation instance tied to the same Liquidity Sweep
- efficient_price_state: EFFICIENT | INEFFICIENT (derived, not independently set)

## Trigger Condition
IF associated_inefficiency.state == FULLY_FILLED AND associated_origin_point.mitigation_state ==
MITIGATED → efficient_price_state = EFFICIENT
ELSE → efficient_price_state = INEFFICIENT

Resolved: "revisited" requires FULLY_FILLED specifically, not a partial fill/approach
combination. Confirmed against your own trading experience — partial fills that never complete
do occur, but are treated as exceptions, and this rule is deliberately not built around
exceptions.

## Process / State Transition
INEFFICIENT (default state following a Liquidity Sweep) → [associated_inefficiency reaches
FULLY_FILLED] AND [associated_origin_point reaches MITIGATED], in either order → EFFICIENT
(terminal for this specific inefficiency/origin_point pair, until a new Liquidity Sweep
re-establishes a new pair at/near the same region)

## Output / Result
- A given price region (defined by its paired inefficiency + origin_point) is tagged EFFICIENT
  or INEFFICIENT
- Once EFFICIENT, the region's pre-existing liquidity pool (per Liquidity Pools — it was always
  there) is no longer entangled with the prior sweep's unresolved business, and becomes available
  as a clean target for a future Liquidity Sweep. This is a change in the pool's availability, not
  the pool's creation.
- This generalizes what Liquidity Sweep's precondition was already checking for at one specific
  timeframe (4H+) into a reusable concept applicable at any timeframe

## Edge Cases
- Partial resolution (inefficiency FULLY_FILLED but origin_point only PARTIALLY_MITIGATED, or
  vice versa) does NOT count as efficient under the current rule — the region stays INEFFICIENT
  until both sides are fully resolved
- A new Liquidity Sweep occurring at/near an already-EFFICIENT region, before any new
  inefficiency forms there, targets the pre-existing pool directly — no special handling needed
- Multi-timeframe overlap (a region efficient on one timeframe while an unresolved pair still
  exists at an overlapping location on a different timeframe) is not addressed here (see Open
  Questions)

## Relationships
- Directly generalizes the "no unmitigated imbalance on 4H+" language in Liquidity Sweep's
  precondition — that precondition can now be restated as "Efficient Price == EFFICIENT on the
  4H+ timeframe in question," rather than being a separate, standalone check
- Composed of: Inefficiency.FULLY_FILLED + Mitigation.MITIGATED, evaluated as a pair
- Unblocks: the pre-existing Liquidity Pool at the same structural level (per Liquidity Pools),
  which was already there and is not created by this entry

## Open Questions / Deliberately Deferred
- Multi-timeframe overlap handling not yet addressed. Checked the FVG reference implementation
  you shared for this — it's single-timeframe only and doesn't address cross-timeframe
  reconciliation, so it doesn't resolve this one; still genuinely open.
