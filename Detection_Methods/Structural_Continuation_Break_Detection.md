<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Structural Continuation Break Detection

## Metadata
- Path: Detection Methods > Structural Continuation Break Detection
- Market scope: FX spot (retail), calibrated on GBP/JPY
- Produces: a continuation-confirmation OR invalidation event, depending on which side of the
  entry-hour candle's range is checked. Same mechanism, two uses (see Modes below).
- Depends on: none directly — works on raw OHLC at any two adjacent timeframes (e.g. 1H/15m,
  4H/1H)
- Depended on by: Strategy Library entries needing an objective "is this move safe to treat as
  continuing" or "has this move's safety net just failed" signal. Currently: 3:50 Scalp's
  break-even rule (confirmation mode, 1H/15m) and take-profit invalidation exit (adverse mode,
  4H/1H).
- Status: Draft — mechanism verified against 4 examples in exhaustive manual detail (Jul 6, Jun
  29, Jul 9 for confirmation mode; Jun 29 again for adverse mode), and the confirmation-mode rule
  checked against 12 examples for sane timing; adverse mode checked against 1 example so far

## Definition
Given a higher timeframe (e.g. 1H, or 4H) and its immediate lower timeframe (e.g. 15m, or 1H),
this method detects the specific moment a directional move's structural safety changes — either
confirming it (continuation mode) or breaking it (adverse mode) — based on two observations about
candle behavior:

1. **Continuation is more common than reversal or double-licky sweeps.** If one candle's high
   gets exceeded by a later candle, the more probable next event is that same later candle's own
   high getting exceeded again, rather than a reversal or a double-licky candle sweeping both
   sides. Reversals and double-licky candles happen, and are exactly why price isn't perpetually
   trending — but they're the less common case at any given continuation point. This same logic
   runs in reverse: if a candle's extreme gets broken *against* the trade direction, the more
   probable next event is continuation of that break, not a reversal back in favor — so the break
   itself is a meaningful signal, evaluated at the moment it happens, not with hindsight.
2. **Candles tend to form directionally, one side first.** A bullish candle more often traces
   open → low → high → close; a bearish candle more often traces open → high → low → close. This
   means a higher-timeframe candle's lower-timeframe composition can reveal, before the
   higher-timeframe candle even closes, which side of its range has already "committed."

## Modes
- **Confirmation mode** (used for break-even): checks whether H_next breaks H_entry's extreme in
  the TRADE's favor. Used to confirm the move is safe to lock in profit protection on.
- **Adverse mode** (used for take-profit's invalidation exit): checks whether H_next breaks
  H_entry's extreme AGAINST the trade direction. Used to exit immediately, without waiting to see
  whether the break resolves into a full reversal or turns out to be a double-licky candle in
  hindsight — per observation 1, the break itself is the actionable signal.
- Both modes use the identical mechanical rule below; only which side is being checked changes.

## Detection Rule
Given a directional move (bullish or bearish) already in progress, and a mode (confirmation or
adverse):
1. Identify H_entry — the higher-timeframe candle containing the point of interest (e.g. a trade
   entry).
2. IF H_entry's own high (bullish) / low (bearish) has exceeded the immediately preceding
   higher-timeframe candle's corresponding extreme → the preceding candle's opposite side
   (low, for bullish; high, for bearish) is now considered structurally protected, per observation 1.
3. Track the NEXT higher-timeframe candle (H_next) as it forms, using its lower-timeframe
   composition for precision.
   - Confirmation mode: the event fires at the exact lower-timeframe candle where H_next's
     cumulative high (bullish) / low (bearish) exceeds H_entry's corresponding extreme in the
     trade's favor.
   - Adverse mode: the event fires at the exact lower-timeframe candle where H_next's cumulative
     low (bullish trade) / high (bearish trade) breaks H_entry's corresponding extreme against
     the trade direction.
4. That lower-timeframe candle's timestamp is the detection output — precise to the lower
   timeframe's resolution, not just "sometime in H_next."

Only step 3's condition is required for the detection to fire — step 2 is context/reasoning for
why it's meaningful, not a separate precondition that must be checked. An earlier version of this
rule (during initial confirmation-mode testing) incorrectly required step 2 as a prerequisite,
which produced multi-hour-delayed false results on two examples before being corrected — see
Calibration Evidence.

## Worked Examples (verified against real GBP/JPY data)

**Confirmation mode, Jul 6 (1H/15m)**: 1H candle A (14:00 UK): H=216.835. 1H candle B (15:00 UK,
contains the point of interest): pushes to H=216.891 (exceeds A), closes at 216.845 — A's low is
now protected. 1H candle C (16:00 UK) forms: its first two 15m sub-candles are bearish, its 3rd
reaches H=216.890 (a hair under B's high), its 4th (16:45–17:00 UK) reaches H=216.951 — clears
B's high. Detection fires at 16:45 UK, exact to the 5-minute candle.

**Adverse mode, Jun 29 (4H/1H, precision down to 5m)**: 4H candle (18:00 UK): H=214.769,
L=214.587. 4H candle (22:00 UK) forms: its very first 5m candle (22:00–22:05) already breaks
18:00's low (L=214.472 < 214.587) — detection fires immediately at 22:00 UK. In hindsight, the
last 5m candle of that same 4H period (23:00–23:05) also broke 18:00's high (H=214.781 > 214.769)
— a double-licky outcome. The 22:00 exit signal was correct at the moment it fired regardless of
this later outcome; hindsight revealing a double-licky candle doesn't retroactively make the
earlier exit wrong, since the decision is evaluated against what was knowable when it fired, not
against what happened afterward.

## Output / Result
A timestamp (precise to the lower timeframe) marking the event, plus the higher-timeframe extreme
value that was broken, plus which mode fired. Epistemic status: CALCULATED (the break itself is a
deterministic read of price data against a defined level) for the event; the claim that this makes
the move safe to act on (confirmation) or unsafe to hold (adverse) is a Strategy Hypothesis
(HEURISTIC, UNVALIDATED per the Epistemic Status standard) built on top of the CALCULATED event.

## Calibration Evidence
**Confirmation mode**: tested as a break-even trigger against 12 real GBP/JPY 3:50 Scalp examples
(Jun 9 – Jul 13 dataset). All 12 produced a detection within 10–270 minutes of the entry point —
sane timing for an intraday scalp, no outliers. Direction (bullish/bearish) for each example was
established through iterative correction during this testing — several automated
direction-detection methods were tried and each failed on at least one example due to short-term
price noise; the reliable signal came from manual verification, not any single automated
heuristic. This is noted here so a future implementation doesn't assume direction detection is a
solved, trivial problem.

**Adverse mode**: verified against all 3 candidate examples in exhaustive detail:
- Jun 29: fires 22:00 UK (first 5m candle of the new 4H period); double-licky outcome only
  visible an hour later at 23:00 — the early exit was correct regardless of the later outcome.
- Jul 6: fires 22:00 UK — identical shape to Jun 29 (both break at the very first candle of the
  new 4H period).
- Jun 3: fires 14:45 UK, exact to the 5-minute candle — this one occurred *before* trade entry
  (the break happened at 14:45, ahead of the 15:50 entry), meaning it functions as a pre-entry
  risk flag rather than a post-entry exit in this instance — see Edge Cases.

All 3 timestamps matched the source notes exactly, with no adjustment needed to the detection
rule itself.

## Edge Cases
- Requires H_entry to have already broken the preceding higher-timeframe candle's extreme before
  this method is meaningful to apply — if it hasn't, the setup doesn't yet have the structural
  character this method describes (see Definition, observation 1).
- Not yet tested for cases where H_next never breaks H_entry's extreme (either mode) within a
  reasonable window (in the 12-example confirmation-mode test, all 12 broke within 270 minutes —
  but no cap/timeout behavior is defined for the case where none does; adverse mode has no
  timing distribution data yet at all).
- Not yet tested on pairs other than GBP/JPY, or timeframe combinations other than 1H/15m
  (confirmation mode) and 4H/1H (adverse mode).
- Adverse mode can fire either before or after trade entry (Jun 3 fired at 14:45, before the
  15:50 entry itself). When it fires before entry, it isn't an exit signal — there's no position
  yet — it functions instead as a pre-entry risk flag ("taking this entry means knowingly
  accepting elevated risk"). This is a genuinely different action (proceed-with-awareness vs.
  exit-now) triggered by the identical detection event, and isn't yet formally distinguished in
  the Output/Result schema. See Open Questions.
- Adverse mode firing does not require waiting to see whether the break resolves into a full
  reversal or a double-licky candle — the break itself is the signal, evaluated at the moment it
  happens. This was confirmed against real trader judgment (Jun 29), not assumed.

## Relationships
- Used by: 3:50 Scalp's Trade Management — confirmation mode for the break-even trigger, adverse
  mode for the take-profit invalidation exit
- Conceptually related to Origin Point Detection's double-licky handling (both rely on the same
  "drill into the lower timeframe for precision" pattern), but this method detects an ongoing
  continuation or invalidation signal, not an origin point.

## Open Questions / Deliberately Deferred
- No cap/timeout behavior defined for either mode if H_next never breaks H_entry's extreme.
- Only validated on GBP/JPY; confirmation mode only tested at 1H/15m, adverse mode only tested at
  4H/1H — applicability to other pairs or timeframe combinations is unverified.
- Adverse mode verified against all 3 candidate examples (Jun 29, Jul 6, Jun 3) — resolved.
- Pre-entry vs. post-entry firing (see Edge Cases) isn't formally distinguished yet — same
  detection event, different required action depending on timing relative to entry.
- Direction detection (a prerequisite input to this method, not something it solves itself)
  remains a genuinely unsolved problem for automation — flagged here since it surfaced during
  this method's own calibration, not because this method is responsible for solving it.
