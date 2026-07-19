> **UPDATE 2026-07-19 (later same day): partially superseded by the window definition.**
>
> The 15:50 window has since been fixed at 15:40–16:10 Europe/London, DST-tracking, with a
> Variation 2 mitigation bound of 19:00. That closes RF-005 and changes two conclusions below:
>
> - **§3 T1-008** — resolved. Its 15:35 crossing is *pre-window* and therefore ineligible. The
>   first in-window crossing is 15:40, matching the recorded entry. No prior-touch policy needed.
> - **§3 T1-010 / §4** — the RF-001 entanglement resolves in favour of keeping **50%**. The 17:10
>   crossing at 61.4% falls inside the 19:00 Variation 2 bound, so the example qualifies at 50%
>   and the argument for lowering to 25% does not survive.
> - **§5** — still open, but narrowed. An activation rule is *still required*, because a
>   Variation 2 zone forming inside the window registers 100% penetration on its own formation
>   candle and would qualify instantly without one. Rules B and C remain indistinguishable.
> - **§3 T1-005** — unchanged and still contested. The window does not rescue it.
>
> See `GBPJPY_1550_Model_Tier_1_Rulebook_v1.2.docx` for the current ruleset.

# RF-004 — Prior Touch Window Policy: Analysis

- Date: 2026-07-19
- Status: **Analysis only. No rule adopted. Requires your decision.**
- Data: `DATASET/csv/Tier 1/FX_GBPJPY, 5m, 24 may - 13 july.csv`, raw 5m bars, UTC+0
- Method: zone bounds, thresholds and directions taken verbatim from `main_Tier_1_Examples_v3.xlsx`;
  penetration recomputed from raw OHLC per Tier 1 Rulebook §4.2

---

## 1. The question, restated

v3 flags T1-008 because the applicable threshold was crossed at 14:35, before the recorded 14:40
trade. Framed as "does an earlier qualifying touch invalidate, preserve, or reset eligibility?"

Working the data, that framing turns out to be a symptom rather than the disease. The real missing
rule is upstream: **there is no definition of when a zone becomes eligible in the first place.**

Without one, the origin candle trivially registers 100% penetration — the zone *is* that candle,
so it fully penetrates itself. Every example then "crosses threshold" at formation. T1-008's 14:35
is not a special case; it is the first instance where the consequences became visible.

The Pine script already carries an activation gate. The Domain Model does not. `context.md`
records this as "a new state introduced without an object contract". This analysis confirms that
gap is load-bearing.

## 2. Candidate rules tested

| Rule | Definition |
|---|---|
| **A** | No gate. Skip the origin bar only, then take the first threshold cross. |
| **B** | Zone activates after one bar with **zero contact** with the zone (either side). |
| **C** | Zone activates after price **fully departs in the trade direction** (BUY: bar low > upper bound). |

Scored against v3's recorded `First applicable-threshold time`, exact match to the bar.

| Rule | Exact matches |
|---|---|
| A — no gate | **1 / 12** |
| B — zero-contact bar | **10 / 12** |
| C — directional departure | **10 / 12** |

Rule A is eliminated. An activation gate is required, not optional.

**B and C produce identical output on all twelve examples.** Tier 1 cannot distinguish them. They
diverge only where price exits the zone on the wrong side before returning, which does not occur
here. Choosing between them requires more labeled data — see §5.

## 3. The two rows that fail, and why they matter

Both B and C fail on the same two examples. Neither failure is a bug in the rule; each exposes a
separate problem in the label set.

### T1-005 (2026-07-03, BUY, zone 215.222–215.292, 7.0 pips)

Price never leaves the zone between formation and the recorded entry.

```
14:20  origin candle                       pen 100.0%   contact
14:25  high 215.306 (just above zone)      pen  81.4%   contact
14:30  low  215.275                        pen  24.3%   contact
14:35  low  215.284                        pen  11.4%   contact
14:40  low  215.275                        pen  24.3%   contact
14:45  low  215.274   <- v3 entry          pen  25.7%   contact
14:55  first bar fully outside the zone
```

Continuous contact throughout. v3 records 14:45 as the first applicable-threshold crossing, but
14:25 reached **81.4%** — more than three times the threshold — twenty minutes earlier. Recording
14:45 as "first" requires discarding 14:25, and no rule in the project discards it.

Under any activation gate that makes the other eleven examples work, T1-005 does not qualify at
all. Under no gate, it qualifies at 14:25, not 14:45.

**Implication: T1-005 is currently marked `Rule-qualified = YES`. On this analysis it should be
`RESEARCH_FLAG`.** That moves the rule-qualification rate from 7/11 to **6/11 (55%)**.

I have not changed v3. This is a finding for you to confirm or reject — you may have a
discretionary reason for treating the 14:25 excursion as part of formation rather than as a
mitigation touch, and if so that reason is itself the missing rule.

### T1-010 (2026-06-03, BUY, zone 214.721–214.848, 12.7 pips)

Here the zone *is* cleanly left, and then returned to.

```
15:05  low 214.793   pen 43.3%   <- v3 stops here, records "threshold not reached" at 50%
15:20 – 16:00        nine consecutive bars entirely outside the zone
16:05  low 214.792   pen 44.1%   contact resumes
16:10  low 214.770   pen 61.4%   <- crosses 50%
16:15  low 214.746   pen 80.3%
16:20  low 214.734   pen 89.8%
16:30  low 214.700   pen 115.7%  (through the zone)
```

**T1-010 does reach its 50% threshold — at 16:10.** v3 records the threshold as not reached
because the search stopped around 15:05.

This has a direct consequence for RF-001. That flag asks whether REFINED_HTF_PUSH should use 25%
or 50%, and its stated evidence is "the example would qualify at 25%". That statement is only
true if eligibility ends before 16:10. If eligibility extends to 16:10, the example qualifies at
50% as well, and RF-001 has no discriminating evidence at all.

**RF-001 cannot be resolved before RF-005 (the window definition).** The threshold question and
the expiry question are entangled in the only example available for either.

## 4. What this changes about flag ordering

The rulebook currently advises resolving RF-004 first. The data suggests a different order:

```
RF-005 (window + expiry)          <- everything else depends on this
   |
   +-- RF-004 (activation / prior touch)   <- reframed: define activation, not just prior touch
   |
   +-- RF-003 (REFINED_HTF_PUSH applicability)
           |
           +-- RF-001 (REFINED_HTF_PUSH threshold)   <- undecidable until RF-005 and RF-003 close

RF-002 (margin tolerance)   <- independent, can proceed in parallel
```

RF-005 was raised as a documentation gap. It is actually the root dependency.

## 5. Options for RF-004, for your decision

I am not choosing between these.

| Option | Rule | Effect on Tier 1 |
|---|---|---|
| **1. Directional departure** (C) | Zone eligible once a bar's low is above the upper bound (BUY) / high below the lower bound (SELL). | 10/12 exact. Fails T1-005. Structurally the cleanest: matches the idea that the zone is left behind and then revisited. |
| **2. Zero-contact bar** (B) | Zone eligible once any bar has no overlap with the zone at all. | 10/12 exact. Identical output here. Looser — permits activation via the wrong side. |
| **3. Departure by margin** | As (1) but requiring a minimum distance, e.g. 0.5× zone width or a fixed pip value. | Untested. Would need calibration and adds a parameter. Might rescue T1-005 if the margin is small, at the cost of a fitted constant. |
| **4. Bar-count gate** | Zone eligible N bars after formation regardless of price. | Untested. Crude, but parameter-light and immune to the continuous-contact case. |

On the prior-touch half specifically — once activation exists, T1-008's 14:35 cross becomes a
genuine first cross after a genuine activation at 14:25, and the recorded 14:40 entry is simply
one bar late. Under options 1 or 2, T1-008 resolves to `YES` with a rule-derived entry of 14:35,
and the discrepancy with the recorded 14:40 is a historical-vs-rule difference of the ordinary
kind, not a research case.

**This means RF-004 may close by adopting an activation rule, without ever needing a
prior-touch-specific policy.** The flag as written may be asking the wrong question.

## 6. Recommended next step, and why it comes first

Both surviving rules score identically. Two of twelve examples are contested. RF-001 and RF-003
rest on a single example each. The sample is too small to settle any of this.

`Backtest_Protocol.md` notes that all twelve Tier 1 labels come from a single one of the three
Tier 1 files. Roughly **20,000 candles of calibration-tier data (2026-02-15 to 2026-05-22) carry
no labels**. Labeling that span would grow the sample, distinguish rules B and C, and give RF-001
and RF-003 more than one case each — **without spending Tier 2**.

That is the cheapest available move and it is a prerequisite for closing four of the five flags.

## 7. Reproducibility

Zone bounds, directions and thresholds are v3 verbatim. Penetration is computed as
`(upper − bar_low) / (upper − lower)` for BUY and `(bar_high − lower) / (upper − lower)` for SELL,
per Rulebook §4.2, using bar extremes rather than closes. Whether extremes or closes are correct
is itself open under RF-002; using closes would change the timing of several crossings and has not
been tested here.
