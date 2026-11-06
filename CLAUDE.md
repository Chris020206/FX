# CLAUDE.md

Instructions for any AI agent working in this repository. Read this before touching anything.

---

## 1. What this project is

A systematic trading framework for GBP/JPY spot forex, converting a discretionary Smart Money
Concepts method into deterministic, testable rules. It is **not** a profitable-system project yet.
The current goal is *classification accuracy*: does the code reproduce what the trader actually
does. Profitability is downstream and out of scope.

The trader (repo owner) is the sole source of truth for method. The documents encode his method;
where they disagree with him, he wins.

---

## 2. Authority order — memorise this

```
Detection (how an order block is found)
    Detection_Methods/order_blocks_v2 (26.07.17).pine     <- THE specification. Calibrated.
Strategy (thresholds, window, entry)
    Strategy_Library/.../dev/GBPJPY_1550_Model_Tier_1_Rulebook_v1.4.docx
Labels
    DATASET/GBPJPY SPOT/main_Tier_1_Examples_v3.xlsx
Everything else
    see the STATUS header at the top of each .md file
```

The Pine file is **not** legacy output to be measured later. It is the working, calibrated
detector, and its tooltips contain the calibration reasoning (margins, sample sizes, why the
strict Domain Model impulse rule was relaxed). Read it before writing any detection code.

Many `.md` files carry a `STATUS: SUPERSEDED / RECONCILIATION PENDING / UNREVIEWED` header. Honour
it. `Wiki.md`, `Three_Fifty_Scalp/Overview.md` and `Mitigation.md`'s intro are known stale.

---

## 3. The rule that matters most

> **When a specification and the labelled examples disagree, STOP AND ASK.
> Do not fit a rule to the examples.**

This is written here because it has already gone wrong once, expensively.

A previous agent found that `Origin_Point_Detection.md`'s selection rule reproduced 2 of 9
labelled examples. Instead of stopping, it invented a rule that scored 9/9 — by being loose enough
to emit ~48 candidates a day against the Pine's ~3.2 — and shipped 291 rows for the trader to
verify. The actual specification was in the repo, unread. See `Implementation/STATUS.md`.

Corollaries:

- **Never infer domain logic from data when a spec might exist.** Search the repo first,
  including non-`.md` files. `find . -type f` before concluding something is undocumented.
- **A gate you can tune your way past is not a gate.** Any validation must have a precision or
  volume penalty, not recall alone, and must be pre-committed before the run.
- **Fitted parameters are labelled UNVALIDATED**, with N stated. See §5.
- Reproducing the right answer is not enough — check it is right *for the right reason*. An
  earlier entry rule produced correct entry times through a bug.

---

## 4. Data tier discipline — enforced, not advisory

| Tier | Location | Use |
|---|---|---|
| Tier 1 | `DATASET/GBPJPY SPOT/Tier 1/` | Calibration. Rules were built here. Free to use. |
| Tier 2 | `DATASET/GBPJPY SPOT/Tier 2/` | **Held out.** Blind validation, spent ONCE, after freeze. |
| Tier 3 | **not in this repo** | Reserved for end-to-end code testing. Deliberately absent. |

Do not read, load, glob, or evaluate against Tier 2 unless the task explicitly says "spend Tier 2".
`Standards/Decision_Log.md` records why Tier 3 is physically absent rather than merely
off-limits: loose instructions not to look are weaker than not having the data.

If you re-tune anything after seeing Tier 2 results, Tier 2 has become calibration data. Say so
loudly and record it in the Decision Log.

The table above covers **GBP/JPY spot only**. `DATASET/Futures/` (raw files local-only, see its
README) has **no tier split yet**. Do not calibrate, tune or fit on futures data until the trader
has defined one and it is recorded here and in the Decision Log.

**CSV handling:** raw UNIX timestamps. Never open in a spreadsheet application — Sheets and Excel
silently reformat the timestamp column as a duration and corrupt it. Read programmatically.

---

## 5. Unvalidated parameters

These are fitted to twelve examples. Do not treat them as settled, do not tune them further
without new labelled data, and keep the marker when you touch them.

| Parameter | Value | Fitted on |
|---|---|---|
| `threshold_tolerance_pips` | 0.3 | N=2 |
| `pre_window_grace_min` | 5 | N=1 |
| `max_origin_age_h` | 1.5 | N=9 |
| activation rule | C (directional departure) | B and C indistinguishable on all 12 |

Open flags: **RF-003** (REFINED_HTF_PUSH applicability, rests on one example) and **T1-005**
(contested classification). The ruleset is **NOT FROZEN**.

---

## 6. Conventions

- **Time:** store and compute in UTC. The 15:50 window is defined in `Europe/London` local and
  tracks DST — resolve through the tz database, never a fixed offset. All twelve labels are BST,
  so the DST path has never been exercised against a real example.
- **Risk:** never hardcode a risk percentage. `risk_pct` is per-trade, bounded by
  `RISK_PCT_MIN`/`MAX`. See `Strategy_Library/General_Rules/Risk_Management.md`.
- **Epistemic status:** `Standards/Epistemic_Status.md` labels are load-bearing. Never upgrade
  UNVALIDATED or HEURISTIC to VALIDATED or CALCULATED for fluency.
- **Hard rules stay in code.** The AI layer may not alter a `HARD_GATE` result. See
  `AI_Policy/Responsibilities.md`.
- **Deliberate gaps:** `Standards/Decision_Log.md` records things intentionally not built (e.g.
  bank holiday checks). Do not "fix" them. `Backlog_Notes.md` is what is genuinely unresolved.

---

## 7. Working agreement

- Small, reviewable commits. One milestone concern per branch.
- Every milestone has a **pre-committed acceptance gate**. Write it before the code.
- If a gate fails, report the failure. Do not adjust the gate.
- Report what you actually read versus skimmed. Do not imply coverage you do not have.
- Ask rather than assume. An unanswered question costs a message; a wrong assumption has already
  cost this project a full working session.

Current milestone: see `NEXT_STEP.md`. Long-range plan: see `ROADMAP.md`.
