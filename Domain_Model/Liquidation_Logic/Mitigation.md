<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: SUPERSEDED**
>
> - The introductory prose still describes approach_depth as tiered at 75%/50%. Later sections in the same file carry the corrected 25%/50% calibration. The introduction is the stale half.
> - Does not yet state the first-contacted-edge measurement convention or the threshold-price formula now fixed in main_Tier_1_Examples_v3.xlsx (Definitions sheet).
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Mitigation

## Metadata
- Path: Domain Model > Liquidation Logic > Mitigation
- Market scope: FX spot (retail)
- Depends on: Liquidity Sweep, Origin Point Detection (defines the origin_point zone this entry tracks against)
- Depended on by: Liquidity Sweep (precondition check), Strategy library entries defining re-entry logic
- Status: Approved — core concept and state machine unchanged; approach_depth threshold recalibrated against 11 real GBP/JPY examples (see Calibration Evidence), replacing the earlier unvalidated 75%/50% guess

## Definition (computable)
Mitigation tracks whether a given origin_point (see Origin Point Detection) reaches a terminal
closed state — either via price returning toward it (tracked continuously via approach_depth,
tiered at 75%/50%), or via the position being treated as closed at a worse loss further along
the original direction. This state machine (UNMITIGATED → PARTIALLY_MITIGATED → MITIGATED) is
fully computable from price data and the origin_point zone alone.

## Epistemic Status (per the Epistemic Status standard)
- **State machine and approach_depth above (CALCULATED)**: whether price has returned into a
  given zone, and by how much, is a direct read of price data against a defined boundary.
- **Model interpretation (INFERRED)**: this system's strategy model interprets that returning
  price as the market maker closing its own leftover position from the original sweep. This is
  this system's explanation for *why* price might return to the level — retail candle data alone
  cannot confirm which participant held a position, whether it was a market maker specifically,
  or that the return is causally connected to the original sweep rather than coincidental.
- **Strategy hypothesis (HEURISTIC, UNVALIDATED)**: because of the interpretation above, price is
  expected to have an increased tendency to return to an unmitigated origin_point specifically
  (not just any prior price level), and once mitigated, that specific incentive for price to
  return is expected to no longer apply.
- **Validation status**: UNVALIDATED. Not yet checked against labeled historical data — see the
  Validation folder.

## Definition, in detail
Mitigation is the closing of a position the market maker opened while sweeping an opposing liquidity pool (see Liquidity Sweep), which was left open ("unmitigated") after the reversal into the target pool. A position is mitigated either by being cut further along the original direction at a worse loss, or by price returning toward the origin_point so the position can be closed there. Mitigation is not binary — a return that only partially reaches the origin_point (e.g. 50% retracement, or a close approach without fully entering the zone) still counts as engaging with mitigation, just incompletely. All of the market-maker-position framing here is Model Interpretation (INFERRED), per above — not a restatement of the computable state machine.

This is a distinct concept from Liquidity Pools/Liquidity Sweep: those describe closing *retail* stop orders by force. Mitigation describes the market maker closing its *own* leftover position from a prior sweep — a different party, a different mechanism, and a different reason price might return to a level.

## Market Model Assumptions
- Assumes the market maker's leftover position from a Liquidity Sweep is not directly observable
  in spot FX (same Observed vs. Inferred caveat as Liquidity Pools) — its existence and location
  are inferred from the origin_point left by the sweep, not confirmed from order-flow data.
- Assumes price returning to an origin_point can be driven by this incentive specifically,
  separate from and in addition to any ordinary liquidity pool that might independently exist
  at the same level.

## Inputs / Variables
- origin_point: inherited from Liquidity Sweep (the reversal candle marking where the leftover
  position was opened)
- mitigation_state, one of:
  - UNMITIGATED — position still open, no return to origin_point yet
  - PARTIALLY_MITIGATED — price has approached or partially entered the zone around origin_point
    without fully closing the position there
  - MITIGATED — position closed, either by (a) being cut further along the original direction at
    a worse loss, or (b) price returning to origin_point and the position being closed there
- approach_depth (a.k.a. fill_ratio): how far price returned toward origin_point when engaging
  with mitigation, measured wick-to-wick from the entry side of the zone (the boundary price
  re-enters from) toward the far side. 0% = barely touched the zone; 100% = fully reached the
  far boundary. This is the inverse of your own convention (high=1/low=0 fixed to the candle,
  where a buy-context trigger at "0.75" means price fell to the level 75% of the way up from the
  low — a shallow retracement). Both describe the same thing; fill_ratio is used internally
  because higher = deeper = stronger reads more naturally, but the two are simple mirror images
  (fill_ratio = 1 − your_level).
  - fill_ratio meeting or exceeding the entry threshold (see Calibration Evidence) →
    MEETS_THRESHOLD — the point at which mitigation is considered meaningfully engaged, not just
    a coincidental pass-by
  - fill_ratio below the threshold → engaging but not yet meaningful

## Calibration Evidence
Checked against 11 real GBP/JPY 5m examples (your own labeled "3:50 Scalp" winning examples,
Jun 9 – Jul 13 dataset, cross-verified OHLC — see Backlog Notes history for how messy getting
clean data for this was). Two different entry thresholds apply depending on which zone convention
is in play, not one universal number:

- **Single origin candle (5m) zone** — entry threshold ≈ **25% fill_ratio** (your "75% of the 5m
  candle," same rule, mirrored convention). 10 of 11 examples met this; the one miss (Jun 25,
  22.9%) missed by only 2 percentage points — within the tolerance you yourself flagged as
  necessary ("the market is not that precise to allow virtually zero tolerance").
- **Widened origin block (15m, per Origin Point Detection's double-licky/refinement handling)** —
  entry threshold ≈ **50% fill_ratio** (your "50% of the 15m candle"). The Jul 6 example (widened
  to the full 14:45–14:55 15m span) measured 48.3% fill_ratio, matching your own note ("filled to
  just about 50%") almost exactly.

The earlier 75%/50% fill_ratio thresholds in this entry were an unvalidated starting guess, made
before any real data existed to check against. They had the right instinct (a two-tier structure)
but the wrong numbers and, more importantly, missed that the correct threshold is zone-width
dependent — a widened 15m zone needs a deeper fill_ratio than a single 5m candle to represent the
same real price distance. This is now corrected using real evidence instead of a guess.

## Trigger Condition
IF an unmitigated origin_point exists AND current_price moves toward it →
  mitigation_state transitions from UNMITIGATED toward PARTIALLY_MITIGATED, tracked via
  approach_depth
IF current_price fully reaches/clears origin_point OR the position is otherwise closed at a
  worse loss further along the original direction → mitigation_state becomes MITIGATED

## Process / State Transition
UNMITIGATED → (price approaches origin_point) → PARTIALLY_MITIGATED (fill_ratio tracked;
MEETS_THRESHOLD once fill_ratio ≥ 25% for a single-candle zone or ≥ 50% for a widened zone,
otherwise treated as engaging-but-not-yet-meaningful) → MITIGATED (via return-to-level close, OR
via further-loss close along the original direction — both are terminal, not just the return case)

## Output / Result
- A mitigation_state and fill_ratio (with its MEETS_THRESHOLD flag) for any given origin_point
- This state feeds directly into Liquidity Sweep's precondition check: an UNMITIGATED (or
  below-threshold PARTIALLY_MITIGATED) imbalance on 4H+ is exactly what disqualifies a new sweep
  setup from being valid, per your original explanation
- MEETS_THRESHOLD is also expected to be the direct input to Three Fifty Scalp's Entry Model —
  the point at which mitigation becomes an actionable entry signal, not just a tracked state

## Edge Cases
- Resolved: fill_ratio entry threshold is zone-width dependent — 25% for a single 5m origin
  candle, 50% for a widened 15m block — per Calibration Evidence above, not one universal number.
- Resolved: a position mitigated via further loss (cut along the original direction) vs. via
  return-to-level are both treated as the same terminal MITIGATED state, with no distinction
  made at the output level. No current use case requires separating them; revisit only if
  Strategy library logic later needs the distinction.

## Relationships
- Consumes: origin_point from Liquidity Sweep
- Feeds back into: Liquidity Sweep's own precondition ("no unmitigated imbalance on 4H+")
  — meaning Mitigation and Liquidity Sweep are mutually dependent: a sweep produces a
  mitigation-tracked origin_point, and whether that origin_point is mitigated determines whether
  a future sweep is even a valid setup

## Open Questions / Deliberately Deferred
- Resolved: origin_point is now formally defined via Detection_Methods/Origin_Point_Detection.md.
- Resolved: fill_ratio entry thresholds (25% single-candle / 50% widened) now backed by 11 real
  examples rather than an unvalidated guess. Sample size caveat: 11 examples, one dataset, one
  pair — worth re-checking once more examples or other pairs are available, per your own note
  that you can supply more (though you've said they're "pretty much the same thing," so this may
  already be a representative sample).
- Two double-licky examples (Jul 6, Jul 7) still need the exact sub-candle origin selection
  confirmed before they can be added to the calibration set — tracked in Backlog Notes.
