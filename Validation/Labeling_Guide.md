# Labeling Guide

## Metadata
- Path: Validation > Labeling Guide
- Status: Current — rewritten 2026-07-19 against `main_Tier_1_Examples_v3.xlsx`
- Supersedes: the "Valid setup, won / lost" taxonomy used up to 2026-07-17
- Authority: `main_Tier_1_Examples_v3.xlsx` (Definitions sheet), then the Tier 1 Rulebook

## Why this was rewritten
The previous label set collapsed two independent axes into one. It asked whether a setup was valid
and whether it made money, and had no way to express the case that turned out to matter most:
*the setup was real, and the current formal rules cannot reproduce it.* Four of eleven Tier 1
historical trades are in exactly that position. A taxonomy without a slot for them forces you to
either discard real evidence or quietly loosen a rule to fit it.

v3 solved this by splitting the record into two independent groups of fields. This guide adopts
that split as the project standard.

---

## The two axes

Every labeled example carries both. They are recorded separately and must never be merged.

### Axis 1 — Historical setup outcome
What actually happened, as originally observed and traded.

| Value | Meaning |
|---|---|
| `VALID_ENTRY` | A real setup by the discretionary read; a trade was taken or would have been |
| `INVALID` | Not a setup, correctly not traded |
| `AMBIGUOUS` | Genuinely unclear on later review |

This axis is **immutable once recorded**. It is historical fact and does not get revised when a
rule changes. Preserve it even when the present formal rule cannot reproduce it.

### Axis 2 — Rule qualification
What the current operational ruleset reproduces exactly.

| Value | Meaning |
|---|---|
| `YES` | All deterministic conditions satisfied at the exact threshold |
| `NO` | Deterministic conditions failed |
| `RESEARCH_FLAG` | Historical evidence conflicts with the current rules — an open question, not a verdict |

Never promote a near miss to `YES` without an adopted tolerance rule. `RESEARCH_FLAG` exists so
that near misses stay visible instead of being rounded into agreement.

### The combination is the signal
| Historical | Rule-qualified | Reading |
|---|---|---|
| `VALID_ENTRY` | `YES` | Rules reproduce reality. 7 of 12 Tier 1 rows. |
| `VALID_ENTRY` | `RESEARCH_FLAG` | **The productive cell.** Rules are incomplete. 4 rows: T1-004, T1-007, T1-008, T1-010. |
| `VALID_ENTRY` | `NO` | Rules actively contradict a real setup. Currently empty — if this ever fills, stop and re-derive. |
| `INVALID` | `NO` | Correctly rejected. 1 row: T1-003. |
| `INVALID` | `YES` | False positive. Currently empty. This is the cell Tier 2 exists to populate. |

---

## Trade outcome is a third, separate field
Profit and loss is recorded but is **not** part of either axis. T1-011 is a fully rule-qualified
valid setup that lost. A valid setup losing is normal variance, not evidence the detection logic
is wrong, and teaching the system otherwise would corrupt it. This was the one correct instinct in
the previous label set and it is retained here.

## Detection error vs. data error
Both remain distinct from the axes above, because their fixes are unrelated:
- **Detection error** — the engine produced an incorrect structure (a level in the wrong place, a
  zone that should not have been confirmed). A code bug.
- **Data error** — bad, missing, or delayed price data caused an incorrect read. A provider issue.

Neither is a strategy failure and neither should be labeled as one.

---

## Required fields per labeled example
Mirrors the v3 worksheet columns, which are now the schema.

**Identity and context**
`Label ID`, `Date`, `Direction`, `Variation`

**Historical record (immutable)**
`Historical setup outcome`, `Historical trade taken`, `Historical entry time`, trade outcome

**Detection**
`Detector origin detected`, `Detector-reported timeframe`, `Origin time`, `Origin timeframe`

**Zone construction**
`Zone refinement` (FULL_5M | WIDENED_15M | REFINED_HTF_PUSH), `Reference timeframe`,
`Zone source bars`, `Exact lower bound`, `Exact upper bound`

**Threshold**
`Applicable threshold`, `Calculated threshold price`, `Threshold met`,
`First OB touch time (0%)`, `First applicable-threshold time`

**Rule evaluation**
`Rule-qualified entry`, `Rule-derived entry time`, `Any earlier qualifying threshold`,
`Earlier qualifying threshold time`, `Confidence`, `Reason code`, `Research flags`, `Notes`

### Two fields that are easy to skip and should not be
- **`First OB touch time (0%)`** is recorded separately from the threshold time on purpose. The
  gap between them is the quantity RF-004 turns on.
- **`Any earlier qualifying threshold`** is what surfaced T1-008. If it is not computed for every
  row it will not be computed for the row where it matters.

## Time basis
All recorded times are **UTC+0**. Do not convert to London local. See Tier 1 Rulebook §2.

---

## Open Questions / Deliberately Deferred
- No storage mechanism exists. This is a taxonomy, not a database schema. The v3 worksheet is
  currently the store.
- Screenshot storage and format not specified.
- `AMBIGUOUS` on axis 1 is defined but unused — no Tier 1 row needed it yet.
