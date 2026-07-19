# Implementation Parameters

All parameters in effect, with provenance. Anything marked UNVALIDATED or DIVERGENT requires
trader review before ruleset freeze.

| Parameter | Value | Provenance | Status |
|---|---|---|---|
| ATR period | 14, Wilder's smoothing | ATR_Swing_Detection.md | FIXED |
| Displacement multiple | 1.5 × ATR within 3 bars | Origin_Point_Detection.md rule 2 | FIXED |
| Sweep reference lookback (W) | **2 bars** | CALIBRATED on Tier 1 labels (see report §2) | UNVALIDATED |
| Zone construction (FULL_5M) | origin candle wick-to-wick | Origin_Point_Detection.md, confirmed | FIXED |
| Threshold depth (FULL_5M) | 0.25 first-contacted-edge | Rulebook v1.3 §4.1 | FIXED |
| Threshold tolerance | 0.3 pips absolute | Rulebook v1.3 §4.2 | UNVALIDATED |
| Activation rule | C (directional departure) | RF-004 open; B ≡ C on Tier 1 | UNVALIDATED |
| Window | 15:40–16:10 Europe/London via tz database | Rulebook v1.3 §2.2 | FIXED |
| Entry semantics | CROSSING (not state) | Rulebook v1.4 §2.4 | FIXED |
| Pre-window grace | 5 min; entry clamped to window open | fitted to T1-008 (n=1) | UNVALIDATED |
| Max origin age | 1.5 h before window open | labels span 20–60 min | UNVALIDATED |
| Efficient Price 4H+ precondition | NOT applied | circular dep., Event_Model.md | **OMITTED** |
| Candidate priority when zones overlap | none — all reported | unspecified in spec | **MISSING RULE** |

## Documented divergences from the written spec
1. **Origin selection.** Origin_Point_Detection.md selects the last candle *before* the impulse
   whose close is on the swept side of an ATR-swing-anchored pool. All 9 FULL_5M labels instead
   mark the **extremum candle itself** — the candle whose wick takes out the prior micro-extreme —
   regardless of its close color (T1-006's origin is bullish). Implemented as observed.
2. **Swept reference.** Pools per Liquidity_Pools.md anchor to k=1.5 ATR swing points. The labels
   sweep **running 2-bar extremes** — internal liquidity far too shallow for k=1.5 to register
   (T1-009's origin high stays below the older session high and takes out only the most recent
   lower high). Implemented as observed; the spec's pool model was not falsified for HTF use,
   only found not to be what the 5m origin selection uses.
3. **5m inefficiency contradiction.** Inefficiency_Detection.md restricts gaps to D/4H/15m, so the
   *primary* gap-based qualifying-impulse rule can never fire at 5m. All FULL_5M origins are
   displacement_based by construction. Either the scope restriction or the primary rule needs a
   trader decision; flagged, not resolved.

## Correction history
- **2026-07-19 (v1.3 build):** entry used *state* semantics — "price beyond threshold during the
  window" — which fired 163 of 291 candidates at window open on breaches that occurred hours
  earlier. Replaced with *crossing* semantics plus a bounded pre-window grace. Candidate volume
  fell 291 → 111 (2.6 → 1.0 per day). The bug also produced T1-008's apparently correct 15:40
  entry by accident; the corrected rule reproduces it deliberately.
