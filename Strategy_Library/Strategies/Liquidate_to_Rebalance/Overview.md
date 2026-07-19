<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Liquidate to Rebalance — Overview

## Metadata
- Path: Strategy Library > Strategies > Liquidate to Rebalance
- Instrument: GBP/USD (source model), applicability to GBP/JPY not yet confirmed
- Timeframe: 4H-anchored (06:00 / 10:00 / 14:00 UK candle cadence)
- Source: Golden Horizon Capital, "Liquidate_to_Rebalance__GBPUSD__1_.pdf"
- Status: Skeleton — relevance map and stated rules transcribed from source; Entry Model detail
  (step 7 of the source checklist references "whichever entry model accustomed to," which is not
  yet defined anywhere in this library), Trade Management, and Risk are placeholders

## Relevance Map (Domain Model)
**Uses:**
- Liquidity Sweep — the Asia range high/low sweep around London open, and the [10:00] 4H
  candle's high/low sweep after [14:00] open, are both instances of this pattern
- Internal and External Liquidity — the exception case (Asia range's internal liquidity being
  cleared while its high/low stays intact, when a higher-timeframe pool like PDH/L or PWH/L is
  liquidated instead) is a direct application of this entry
- Mitigation — the London-open volume from the 07:00–10:00 bracket remaining unmitigated is the
  central mechanism the whole model is built around
- Inefficiency (Imbalance) — the model explicitly names this ("Ineff") and requires it be marked
  out and checked for fill
- Efficient Price — the model's overall aim, stated in its own terms ("mitigated and efficient"),
  is exactly this entry's definition
- Liquidity Pools — PDH/L, PWH/L, and Asia range high/low are all liquidity pools per that entry's
  definition
- Reference Level, specifically via Detection_Methods/Session_Level_Detection.md — Asia range
  high/low, PDH/L, PWH/L, and the [10:00]/[14:00] 4H candle extremes are all SESSION_HIGH/LOW,
  PREVIOUS_DAY_HIGH/LOW, PREVIOUS_WEEK_HIGH/LOW, and CANDLE_HIGH/LOW level_types respectively

**Explicitly does NOT use:**
- ATR Swing Detection — this model anchors entirely to fixed session-based reference points, not
  ATR-based swing/ZigZag points. **This was previously flagged as an unreconciled conflict**
  (Structural Point Detection's swing logic vs. this model's fixed reference points) — now
  resolved: these were never competing definitions of one thing, they're two different
  Detection Methods (ATR Swing Detection and Session Level Detection) that both implement the same
  Reference Level interface. This model simply uses one and not the other; no reconciliation was
  needed once that distinction existed. See Reference_Level.md and Session_Level_Detection.md.

## Blocking Dependency
Session_Level_Detection.md (which this strategy depends on entirely for PDH/L, PWH/L, and Asia
range) is itself Draft, not Approved, pending a resolved daily/weekly candle rollover convention
(GMT/BST handling, which broker convention for "previous day"). This strategy's Entry Model cannot
be considered computable until that's fixed — see that entry's Open Questions, and Backlog Notes.

## Applicable General Rules
- Pre-News Scalp Rule — not directly applicable as written (this model isn't a scalp), but the
  source PDF has its own overlapping news exclusion (Rule 1 below) that should probably be
  reconciled with Pre-News Scalp Rule rather than kept as a fully separate rule. Not yet done.

## Context / Bias Rules
Tagged by rule_type: HARD_GATE | PARAMETERIZED_KL_INSTANCE | SOFT_CONFLUENCE

- [HARD_GATE] No trades on major news days: Inflation Rate (US/UK), GDP Growth, NFP (source Rule 1)
- [HARD_GATE] Invalid if PDH/L is liquidated before [14:00] (source Rule 2)
- [HARD_GATE] Invalid if Asia range High/Low is NOT liquidated (source Rule 3)
- [HARD_GATE] Liquidation must occur before rebalance/mitigation fill (source Rule 4) — this is
  a direct, explicit statement of Mitigation's own assumed causal order
- [PARAMETERIZED_KL_INSTANCE] Run Liquidity Sweep detection on Asia range high/low, specifically
  expected in the back half of the [06:00] 4H candle, between 07:00–10:00 UK
- [PARAMETERIZED_KL_INSTANCE] Run Liquidity Sweep detection on the [10:00] 4H candle's high/low,
  expected after [14:00] 4H open
- [SOFT_CONFLUENCE — tentative] "Direction a 4H candle high/low is liquidated generally indicates
  subsequent direction" — stated with hedge words ("more often than not," "generally") in the
  source, so this reads as a bias/confluence factor rather than a hard gate. Flagged as tentative
  since you haven't confirmed this classification.

## Entry Model
Source PDF's checklist (steps 1–7) is essentially a worked pre-entry filter, transcribed here:
1. Check for major news (Inflation, NFP, GDP Growth)
2. Check if PDH/L has been liquidated before [14:00]
3. Check if Asia range High/Low has been liquidated, opposite direction of inefficiency
4. Check [10:00] 4H close for inefficiency; mark "4H Ineff" if present
5. At [14:00] open, set an alert at the [10:00] 4H candle's high/low
6. When alert triggers: has the inefficiency been filled already? (liquidation must precede fill)
7. "Whichever entry model accustomed to must be fulfilled" — this references an entry model that
   is NOT defined anywhere in this library yet. Placeholder; needs your input.

## Trade Management
Not yet defined. Placeholder only.

## Risk
Not yet defined. Placeholder only.

## Open Questions / Deliberately Deferred
- Resolved: fixed session-based reference points vs. ATR-swing methodology — see Blocking
  Dependency above; they're separate Detection Methods under the Reference Level interface, not
  competing definitions needing reconciliation
- Daily/weekly candle rollover convention — genuinely blocking (see Blocking Dependency above)
- Reconciling this model's Rule 1 (news exclusion) with the General Rules Pre-News Scalp Rule
- Confirming the SOFT_CONFLUENCE classification on the 4H-liquidation-direction bias statement
- Entry Model step 7's referenced (but undefined) entry model
- Trade Management, Risk — fully open
- Applicability to GBP/JPY (source model is GBP/USD) not yet confirmed
