<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: RECONCILIATION PENDING**
>
> - The Event / Tracker / Evaluator separation defined here conflicts with the linear chain in GBPJPY_1550_Model_Object_Definitions_v1.0, which models mitigation as an event.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Event Model

## Metadata
- Path: Domain Model > Event Model
- Status: Draft — first version
- Resolves: the circular dependency flagged in the Thoughts and Feedback review

## The Problem This Solves
Checking the actual "Depends on" metadata fields across this system surfaces a real cycle:
**Liquidity Sweep depends on Efficient Price** (its own precondition: "Efficient Price must equal
EFFICIENT for any prior opposing sweep's pair"), **and Efficient Price depends on Liquidity Sweep**
(transitively, via Mitigation and Inefficiency, both of which are produced by a Liquidity Sweep
instance). This is a genuine two-node cycle, not just the three-node loop through Mitigation
originally described in the feedback — both exist simultaneously.

Conceptually, this cycle is fine and correct: it reflects a real feedback loop (a sweep produces
an origin_point; whether that origin_point later gets mitigated determines whether a *future*
sweep at a related level is even valid). The Domain Model documents should keep describing that
relationship as it actually is — forcing the Markdown "Depends on" fields into an artificially
acyclic shape would misrepresent the real relationship for the sake of tidiness.

But a software module that imports another module which imports it back is a real problem
(a literal circular import in most languages, and independent of language, muddled ownership of
which object is the source of truth for what). The fix is architectural, not conceptual: separate
what the Domain Model calls one thing into three different *kinds* of objects, per Object_Schemas.

## The Three Kinds of Objects
1. **Events** — immutable facts about something that happened, created once and never mutated.
   `SweepEvent`, `OriginPoint` (in its creation, not its ongoing mitigation status), and
   `InefficiencyInstance` (at formation) are Events.
2. **Trackers** — mutable state that updates over time as new price data arrives, each reading
   from Events but never the other way around. `MitigationState` reads `OriginPoint` (which
   Event created it) and updates its own `mitigation_state`/`approach_depth` independently.
   `EfficiencyState` reads `InefficiencyInstance` and `MitigationState` together — it does not
   read `SweepEvent` or `OriginPoint` directly, and no Event or earlier Tracker ever reads a later
   Tracker's output. This one-directional read order is what breaks the cycle: `EfficiencyState`
   depends on `MitigationState`, but `MitigationState` never depends on `EfficiencyState`.
3. **Eligibility Evaluators** — read Tracker (and Event) states to decide whether a *new*
   candidate sweep/setup is valid right now. `SweepEligibilityEvaluator` is what actually
   implements Liquidity Sweep's precondition ("Efficient Price must equal EFFICIENT") — it reads
   the current `EfficiencyState` for the relevant region before creating a new candidate
   `SweepEvent`. The precondition check lives in the Evaluator, not inside `SweepEvent` itself, so
   `SweepEvent` never needs to import `EfficiencyState` — the Evaluator sits between them.

## Resulting Dependency Direction (acyclic)
```
SweepEvent  --creates-->  OriginPoint, InefficiencyInstance
OriginPoint  --read by-->  MitigationState (tracker updates over time)
InefficiencyInstance  --read by-->  (its own state updates directly; also read by EfficiencyState)
MitigationState + InefficiencyInstance  --read by-->  EfficiencyState
EfficiencyState  --read by-->  SweepEligibilityEvaluator
SweepEligibilityEvaluator  --creates-->  new SweepEvent (candidate)
```
Note the last line: a new `SweepEvent` is created *by* the Evaluator, which read `EfficiencyState`
— but the *previous* `SweepEvent` that led to that `EfficiencyState` is a different instance, not
the same object reading itself. Nothing here requires two modules to import each other.

## Event Types
- `REFERENCE_LEVEL_CREATED` — a Detection Method produced a new ReferenceLevel
- `PRICE_APPROACHING_LEVEL` — price is nearing a tracked level (used for Companion Interface
  "developing" states, per Architecture.md's example UI)
- `LEVEL_BREACHED` — price entered a ReferenceLevel/LiquidityPool's zone_bounds
- `SWEEP_CANDIDATE_CREATED` — zone entered, reversal not yet confirmed (ZONE_ENTERED state)
- `SWEEP_CONFIRMED` — close-based reversal confirmed; a SweepEvent object is finalized
- `ORIGIN_POINT_CREATED` — an OriginPoint object created (PROVISIONAL) following a confirmed sweep
- `MITIGATION_STARTED` — price begins approaching an origin_point (UNMITIGATED → PARTIALLY_MITIGATED)
- `MITIGATION_COMPLETED` — MitigationState reaches MITIGATED
- `INEFFICIENCY_FILLED` — InefficiencyInstance reaches FULLY_FILLED
- `SETUP_INVALIDATED` — a StrategyCandidate's status becomes invalidated (a hard rule failed, or
  an OriginPoint reached INVALIDATED per Origin_Point_Detection.md)

This is how the system is intended to operate in real time — each event triggering the next
tracker update, ultimately feeding a StrategyCandidate the AI reasoning layer can assess.

## Relationships
- This document doesn't replace any existing Domain Model entry's own Relationships section — it
  describes how those conceptual relationships should be implemented without creating circular
  software dependencies. The Markdown entries keep describing the real, sometimes-cyclic
  conceptual relationships; this document is the translation layer into acyclic code structure.

## Open Questions / Deliberately Deferred
- This is a first-pass event list; likely incomplete once actual implementation starts (e.g.
  events for GRAB vs. SWEEP sub-classification, or Origin_Point_Detection's fakeout-discard case,
  aren't separately named yet).
- No formal event-sourcing/persistence design yet (e.g. event store, replay behavior for
  backtesting) — this document defines the event *types*, not the infrastructure that carries them.
