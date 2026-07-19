# Implementation Status — DETECTION PARKED

Date: 2026-07-19

## Read this before using anything in this folder

| Layer | File | Status |
|---|---|---|
| Strategy / entry layer | `pipeline.py` | **VALIDATED.** Given correct zones, reproduces every rule-qualified Tier 1 entry with exact times, correctly rejects T1-005 and T1-007. |
| Detection layer | `detect.py`, `swings.py` | **FAILED. Do not use.** Retained only as a record of what was tried. |

## Why detection failed
`detect.py` was written by reverse-engineering the twelve labelled examples, because the author
did not read `Detection_Methods/order_blocks_v2 (26.07.17).pine` — which was in the project the
whole time and *is* the calibrated detection specification.

The reverse-engineered rule reaches 9/9 label recall only by emitting ~48 origin candidates per
day. The Pine emits ~3.2. The gap is explained by three filters the Pine has and `detect.py` does
not:

| | Pine v2.2 | detect.py |
|---|---|---|
| Origin | `ta.pivothigh/pivotlow`, K=2 — extreme on *both* sides | 2-bar backward extreme only |
| Min zone size | 0.75 x ATR | none |
| Displacement | 1.5 x ATR, close-to-origin-extreme | high-low range |
| Dual-tagged candles | rejected as chop | not handled |
| Variation 2 | dedicated path | not implemented |

Its output file (`output/candidates_tier1_full.csv`) has been deleted. It was not adjudicable.

## The lesson, recorded deliberately
The validation gate that "passed" measured recall only, with no precision penalty, on a parameter
free to be tuned against the same labels. A gate like that cannot fail. See `CLAUDE.md`.

## What replaces it
Port the Pine to Python line by line (Milestone M1). Do not infer detection logic from examples.
