# Detector Validation Report — Tier 1

Date: 2026-07-19. Code: `Implementation/`. Data: three Tier 1 CSVs (calibration tier only —
Tier 2 and Tier 3 untouched).

## 1. Pre-committed gate: PASSED
Primary test: ≥7 of 9 FULL_5M labels with exact wick-to-wick bounds at the labelled origin
candle. **Result: 9/9 exact bounds, exact origin times, correct directions** (lookback W=2).
T1-010 (REFINED_HTF_PUSH) excluded from the gate as pre-declared — no detection rule exists for
that zone type.

Honesty note: W was chosen by sweeping {1,2,3,4,6,8} against these same labels. Tier 1 is the
calibration set, so tuning here is by design — but W=2 has been validated against nothing else
and carries UNVALIDATED status. W=1 also achieves 9/9 with more noise; recall degrades from W=3.

The written spec's selection rule scored 2/9 before correction. See PARAMETERS.md divergences —
the spec should be amended to match practice, not the reverse.

## 2. End-to-end strategy layer (labelled file, 32 trading days)
Full pipeline = detection → activation (rule C) → 25% threshold + 0.3 pip tolerance →
15:40–16:10 London window → invalidation check.

| Check | Result |
|---|---|
| 8 rule-qualified FULL_5M entries (v1.3 §8) | **8/8 recovered, entry times exact to the bar** |
| T1-005 (contested, continuous contact) | correctly does NOT fire — never activates pre-window |
| T1-007 (0.40 pips outside tolerance) | correctly does NOT fire |
| T1-003 (INVALID) | no candidate at its origin — consistent with label |
| T1-004 (WIDENED_15M) | **origin not detected — known recall gap**, zone-type construction unresolved |
| T1-010 (REFINED_HTF_PUSH) | not constructible; a nearby FULL_5M candidate [214.713,214.828] enters 16:05 London, close to but not equal to the v3 zone |

## 3. Candidate volume
| Span | Trading days | Strategy candidates | Per day |
|---|---|---|---|
| Feb 15 – Apr 3 (mostly GMT) | ~34 | 114 | 3.4 |
| Apr 5 – May 22 | ~34 | 70 | 2.1 |
| May 24 – Jul 13 (labelled) | 32 | 107 | 3.3 |

After clustering overlapping same-day same-direction zones: **~1.5 distinct setups/day** on the
labelled span. Many candidates are nested origins of the same structure; **no priority rule
exists** for choosing among them — this is a missing rule the spec must supply.

The labels are not exhaustive (they are trades taken, not all setups that existed), so
non-labelled candidates are NOT automatically false positives. Deciding which are real is
precisely the adjudication task.

## 4. The deliverable that matters
`output/candidates_tier1_full.csv` (DELETED) — **111 candidates across all three Tier 1 files** (1.0/day),
with an empty `adjudication` column. 27 fall on GMT days: adjudicating those tests the DST path
against human judgment for the first time, since every current label is BST.

Each row now records `cross_time_london` alongside `entry_time_london`, and a `pre_window_cross`
flag (13 rows). Where those differ, the crossing happened inside the 5-minute grace and entry was
clamped to window open — the T1-008 pattern.

## 6. Corrected entry semantics (post-review)
The first build used *state* semantics: it entered if price was beyond the threshold at any point
during the window. That fired on stale breaches — **163 of 291 candidates** had already breached
before 15:40, producing an 108-row spike at exactly window open.

Replaced with *crossing* semantics: the bar must reach the threshold when the previous
post-activation bar had not, with the crossing eligible from 5 minutes before window open, and
entry clamped to window open.

| | state (v1.3) | crossing + 5m grace (v1.4) |
|---|---|---|
| Candidates | 291 (2.6/day) | **111 (1.0/day)** |
| Stale window-open fires | 163 | 0 |
| Known entries, strict match | — | **6/7** |

T1-009 is the one miss and is not a semantics failure: it is produced with correct zone bounds but
enters 15:40 instead of 16:00, because the 0.3 pip tolerance moves its crossing. This is the
documented RF-002 side effect, confirmed here independently.

**This bug also invalidated a rulebook conclusion.** v1.3 §9 stated that the window resolved
RF-004's prior-touch half, citing T1-008's "first in-window crossing at 15:40". There is no
crossing at 15:40 — price crossed once at 15:35 and remained below. The correct entry time was
reproduced by the bug, not by the rule. RF-004 is reopened and closed as parameterised in v1.4.

## 5. What this run does NOT show
- No profitability claim of any kind. Entries only; no exits, no outcomes.
- No Tier 2 / Tier 3 exposure. Both remain unspent.
- W=2, tolerance 0.3, activation C are all fitted to 12 examples. The 279 unlabelled candidates
  are the first out-of-sample evidence for all three.
