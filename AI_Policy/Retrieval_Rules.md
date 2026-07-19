<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# Retrieval Rules

## Metadata
- Path: AI Policy > Retrieval Rules
- Status: Draft — first version

## Purpose
Defines what gets retrieved for the AI reasoning layer before it assesses a candidate (per
Architecture.md component 6, "Context-retrieval system" / RAG). The Strategy Library's Relevance
Maps (the "Uses" / "Does NOT use" lists in every Strategy Overview) are, almost verbatim, the
retrieval index this component needs — this document just makes that connection explicit and
states the retrieval procedure.

## Retrieval Procedure
Given a StrategyCandidate for a specific strategy (e.g. "3:50 Scalp"):

1. Retrieve that strategy's Overview.md from Strategy_Library/Strategies/, specifically its
   Relevance Map's "Uses" list.
2. For each Domain Model entry named there, retrieve that entry's Definition and Epistemic Status
   sections in full. Do NOT retrieve entries listed in that strategy's "does NOT use" list, even
   if they seem generically related — that list exists specifically to keep retrieval scoped and
   prevent irrelevant context from diluting the AI's grounding.
3. Retrieve the relevant Detection Method(s) actually referenced by the retrieved Domain Model
   entries (e.g. if Liquidity Pools is retrieved, also retrieve whichever Detection Method
   produced the specific ReferenceLevel this candidate's structural_reference actually used —
   not all Detection Methods indiscriminately).
4. Retrieve that strategy's Applicable General Rules.
5. Retrieve labeled historical examples matching this candidate's strategy_name and, where
   possible, similar detected structure (once the Historical Examples Database exists — see
   Validation folder; this step is currently a placeholder).
6. Do NOT retrieve Backlog_Notes.md or any Overview marked Draft/Skeleton unless the candidate's
   own strategy_name is that Draft strategy — backlog content describes what's unresolved, not
   grounding the AI should reason from as if settled.

## What This Prevents
Without a scoped retrieval rule, a generically "similar-sounding" Domain Model entry could get
pulled in for every candidate regardless of strategy, diluting context with irrelevant material
and increasing the chance the AI reasons from something not actually applicable to the strategy
at hand — this is the same failure mode the Relevance Maps were built to prevent at the
documentation level; this document just makes sure retrieval actually respects those boundaries
at inference time instead of ignoring them.

## Open Questions / Deliberately Deferred
- No actual retrieval implementation exists yet (this assumes a system that can look up Domain
  Model/Strategy Library entries by name — a real RAG index, not yet built)
- Step 5 (historical example retrieval) is fully blocked on the Historical Examples Database not
  existing yet
