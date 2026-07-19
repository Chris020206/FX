<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: SUPERSEDED**
>
> - The Entry Model fill-ratio table is stale. It reports 12 verified entries; main_Tier_1_Examples_v3.xlsx records 11 historical trades, of which 7 are rule-qualified, 4 research-flagged and 1 invalid.
> - Individual fill ratios disagree with v3's measurements (e.g. Jun 25 listed here as 22.9%; v3 T1-007 measures ~20.5% and does not qualify).
> - Jun 11 is used here as the canonical Variation 2 example. v3 excludes Jun 11 from the dataset entirely. The current Variation 2 case is T1-010 (Jun 3), which is itself research-flagged.
> - All times in this document are UK local. v3 and the Tier 1 Rulebook use UTC+0. Times here read one hour later than the same events in v3 during BST.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# 3:50 Scalp — Overview

## Metadata
- Path: Strategy Library > Strategies > 3:50 Scalp
- Instrument: GBP/JPY (primary), framework general to FX spot
- Timeframe: lower-timeframe scalp, anchored to a 15:40–16:00 UK time window
- Status: Relevance Map, Context/Bias Rules, Entry Model, Risk, and Trade Management (both
  break-even and take-profit) are all defined and checked against real examples. This is the
  first strategy in the project close to fully computable — remaining gaps are narrow: Step 2's
  individual target-price re-verification, Jul 6's widened-zone stop convention, and the
  pre-entry/post-entry firing distinction.

## Relevance Map (Domain Model)
**Uses:**
- Liquidity Sweep — the core pattern this strategy is watching for within the time window
- Mitigation — tracks the origin_point left by the sweep, which is the actual entry reference
- Inefficiency (Imbalance) — expected to co-occur with the sweep, per Liquidity Sweep's Output/Result
- Efficient Price — determines whether a given origin_point/inefficiency pair is still valid
  (unresolved) or already efficient (and therefore no longer a live setup)
- Reference Level (via ATR Swing Detection) — underlies Liquidity Sweep's pool definitions on the relevant
  lower timeframe, and directly used for equal-highs/equal-lows zones in Take-Profit
- Liquidity Pools — inherited automatically since Liquidity Sweep depends on it
- Internal and External Liquidity — used directly by name in Take-Profit's "internal liquidity"
  target type, not just inherited
- Structural Continuation Break Detection — used directly for both the break-even rule
  (confirmation mode) and the take-profit invalidation exit (adverse mode)

**Explicitly does NOT use:**
- Asia session liquidation rule — not relevant; this strategy's time window (15:40–16:00 UK) has
  no relationship to the Asia session or London-open Asia-range dynamics
- Liquidate to Rebalance's 4H cadence logic — different timeframe, different mechanism entirely,
  despite both ultimately relying on Liquidity Sweep + Mitigation underneath

## Applicable General Rules
- Pre-News Scalp Rule — relevance unclear and needs your confirmation: that rule concerns
  positions opened before a 13:30 UK release; 3:50 Scalp operates at 15:40–16:00, after that
  window. Does a later major release (if any exists at that time) trigger the same treatment,
  or is Pre-News Scalp Rule simply inapplicable here? Not resolved — flagged rather than guessed.
- Risk Management — position sizing (0.5% of equity) and the daily trade cap apply here as a
  portfolio-wide rule; see General_Rules/Risk_Management.md rather than this strategy's own Risk
  section, which only covers the stop-loss placement specific to this strategy.

## Context / Bias Rules
Tagged by rule_type: HARD_GATE (must be true/false, no exceptions) | PARAMETERIZED_KL_INSTANCE
(an existing Domain Model pattern run with specific parameters) | SOFT_CONFLUENCE (raises or
lowers conviction, does not gate the trade on its own)

- [PARAMETERIZED_KL_INSTANCE] Run Liquidity Sweep detection with a time filter restricting valid
  sweep/reversal formation to 15:40–16:00 UK time.
- [HARD_GATE / PARAMETERIZED_KL_INSTANCE — needs your input] Whether this strategy requires
  Efficient Price == EFFICIENT for some higher timeframe as a precondition (mirroring Liquidity
  Sweep's own 4H+ precondition), or whether the 15:40–16:00 window is treated as sufficiently
  short-term that this check doesn't apply. Not yet specified by you — currently unresolved.

## Entry Model
[PARAMETERIZED_KL_INSTANCE] Entry fires when Mitigation's `meets_threshold` becomes true for the
origin_point being tracked — i.e. fill_ratio crosses 25% (single-candle zone) or 50% (widened
zone), per Mitigation.md's Calibration Evidence. This is the same trigger regardless of which
timing variation produced the origin_point:

- **Variation 1**: origin_point forms before the 15:40–16:00 window, mitigation happens inside it
  (the common case — 9 of 12 examples)
- **Variation 2**: origin_point forms inside the window, mitigation happens later, sometimes hours
  later (e.g. Jun 11 — origin_point ~16:00, mitigated 18:20)

No separate entry logic is needed per variation — both produce the same tracked Mitigation object,
and the entry condition is identical either way. All 12 verified examples are, by construction,
already 12 verified entry points:

| Date | Entry (mitigation trigger) | Fill Ratio |
|---|---|---|
| May 28 | 15:50 | 76.6% |
| Jun 2 | 15:50 | 43.1% |
| Jun 3 | 15:50 | 98.2% |
| Jun 10 | 16:00 | 43.2% |
| Jun 11 | 18:20 (variation 2 — origin formed in-window, mitigated later) | 35.1% |
| Jun 18 | 15:40 | 76.9% |
| Jun 25 | 16:15 | 22.9% |
| Jun 29 | 15:45 | 45.0% |
| Jul 3 | 15:45 | 25.7% |
| Jul 6 | 15:45 | 48.3% (widened zone) |
| Jul 9 | 16:00 | 70.4% |
| Jul 10 | 15:45 | 27.9% |

## Trade Management
Break-even and take-profit, formalized from your own historical practice and checked against 12
real GBP/JPY examples (Jun 9 – Jul 13 dataset). Neither was previously a hard rule ("always been
in the air, no hard rules" — your words) — this is the first time either has been made explicit
and checked against data, not a restatement of something already fixed.

### Break-Even
[PARAMETERIZED_KL_INSTANCE] Move stop to break-even at the moment Structural Continuation Break
Detection fires — the next higher-timeframe (1H) candle breaking the entry-hour candle's extreme
in the trade's direction, precise to the 15m sub-candle. See
Detection_Methods/Structural_Continuation_Break_Detection.md for the full mechanism and reasoning
(continuation more common than reversal/double-licky; directional candle formation).

Calibration evidence: tested against all 12 examples, triggered within 10–270 minutes of entry
in every case — no outliers, sane timing for an intraday scalp. Full results:

| Date | Direction | Break-Even Trigger |
|---|---|---|
| May 28 | bullish | 85 min |
| Jun 2 | bullish | 10 min |
| Jun 3 | bearish | 105 min |
| Jun 10 | bearish | 270 min |
| Jun 11 | bullish | 215 min |
| Jun 18 | bullish | 20 min |
| Jun 25 | bullish | 45 min |
| Jun 29 | bullish | 15 min |
| Jul 3 | bullish | 15 min |
| Jul 6 | bullish | 60 min (your own manual check, verified exact to the 5m candle) |
| Jul 9 | bullish | 60 min |
| Jul 10 | bearish | 40 min |

### Take-Profit
Revised from an earlier 80%/20% draft after reviewing all 12 examples in detail against your own
notes (see Take_profit_notes.md history) — the real logic is a priority-ordered decision tree,
not a fixed partial-close split.

**Step 1 [HARD_GATE] — invalidation exit check, evaluated continuously, takes priority over
everything below.** If Structural Continuation Break Detection fires in **adverse mode** (4H/1H)
— the next 4H candle breaking the prior 4H candle's extreme against the trade direction — close
100% immediately. Do not wait to see whether the break resolves into a full reversal or turns out
to be a double-licky candle in hindsight; the break itself is the signal, evaluated at the moment
it fires. Verified against real data on all 3 candidate examples: Jun 29 (fires 22:00 UK, double-
licky outcome only visible an hour later at 23:00 — the early exit was correct regardless of the
later outcome), Jul 6 (fires 22:00 UK, identical shape to Jun 29), and Jun 3 (fires 14:45 UK,
exact to the source notes — this one occurred *before* the 15:50 entry, functioning as a
pre-entry risk flag rather than a post-entry exit; see Structural Continuation Break Detection's
Edge Cases for that distinction, not yet formally resolved).

**Step 2 [PARAMETERIZED_KL_INSTANCE] — if Step 1 hasn't fired, check for a clear target.** Close
100% (not a partial) at whichever of these is reached first:
- An **Inefficiency** fill, at whichever timeframe has one (4H is most common in the reviewed
  examples; sometimes refined to 1H per Origin Point Detection's drill-down logic; occasionally
  Daily)
- An **equal-highs/equal-lows zone** (per Reference Level's EQUAL_HIGHS_ZONE/EQUAL_LOWS_ZONE
  level_type)
- **Internal liquidity** relative to a higher-timeframe range (per Internal and External
  Liquidity), or an **unmitigated origin_point** ("orderblock") beyond the current point — both
  read as "unfinished business" price has a reason to be drawn to

All of the above are filtered by the intraday-only rule — a theoretically valid target that would
only be reached after the trading day ends is discarded in favor of a nearer, less ideal target,
or falls through to no-target handling below. This showed up repeatedly in the reviewed examples
(7 Jul discarding a daily ineff "a long way down," 11 Jun discarding an equal-highs target only
reached the next day, 28 May's target invalidated the same way).

**Step 3 [no rule, by design] — if neither Step 1 nor Step 2 applies, there is no formal
take-profit rule.** The position is closed at trader discretion. This is not a gap to fill later
— your own review of 25 Jun explicitly declined to invent a formal exit reason where none
existed, on the grounds that forcing one would misrepresent what actually happened. That
discipline is preserved here rather than papered over with a rule that wouldn't be honest.

This replaces the entry's earlier 80%/100% framing entirely — closing 80% and leaving a
discretionary runner was never a formal rule, just what tended to happen under Step 3's
discretion; encoding it as a fixed split misrepresented it as more rule-governed than it was.

Not yet numerically calibrated against the full 12-example set the way break-even was — Step 1 is
verified on 1 of 3 candidate examples in full detail; Step 2's target-type distribution matches
the notes qualitatively but individual price levels haven't been independently re-checked against
raw data one by one.

## Risk
[PARAMETERIZED_KL_INSTANCE] Stop-loss = origin_point's far boundary, offset by 3 pips beyond it
(GBP/JPY pip convention: 0.01) — below the origin_point's low for a buy, above its high for a
sell. This sits just past the same boundary Origin Point Detection's own Invalidation Rule uses
to declare the structural premise negated, so the stop and the point where the trade thesis is
actually wrong are effectively the same level, with a small buffer for noise.

Checked against 11 of the 12 examples (single-candle zones; Jul 6's widened-zone case needs its
own distance convention, not yet defined): resulting risk ranged 3.3–13.4 pips, all sane for a
tight scalp, no outliers.

| Date | SL level | Risk (pips) |
|---|---|---|
| May 28 | 213.788 | 4.5 |
| Jun 2 | 215.221 | 7.1 |
| Jun 3 | 214.883 | 3.3 |
| Jun 10 | 215.200 | 7.6 |
| Jun 11 | 213.840 | 8.0 |
| Jun 18 | 212.847 | 5.7 |
| Jun 25 | 213.308 | 11.1 |
| Jun 29 | 214.150 | 13.4 |
| Jul 3 | 215.192 | 8.2 |
| Jul 9 | 217.321 | 8.3 |
| Jul 10 | 217.120 | 7.9 |

Position sizing (0.5% of equity) and the daily trade cap are portfolio-wide, not specific to this
strategy — see General_Rules/Risk_Management.md.

## Open Questions / Deliberately Deferred
- Pre-News Scalp Rule applicability to this window
- Whether a higher-timeframe Efficient Price precondition applies
- Take-profit Step 1 (invalidation exit) now fully verified against all 3 candidate examples
- Pre-entry vs. post-entry firing of Step 1 (Jun 3 fired before entry, functioning as a risk flag
  rather than an exit) isn't formally distinguished yet — same underlying question as Structural
  Continuation Break Detection's own open item on this
- Take-profit Step 2 (target selection) matches the reviewed notes qualitatively but individual
  price levels/timeframes haven't been independently re-checked against raw data one by one
- 18 Jun's suspected-news event (~20:00, ~118 pip move in an hour) — you flagged this as
  unverified; likely the same question as the existing Pre-News Scalp Rule applicability item
  above, not a separate one, but the specific event itself hasn't been confirmed
- Jul 6's widened-zone case needs its own stop-distance convention — the 3-pip-beyond-boundary
  rule was only checked against single-candle-zone examples
- Structural Continuation Break Detection has its own open items — see that entry, notably no
  cap/timeout if the continuation break never arrives (either mode)
