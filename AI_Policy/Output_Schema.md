<!-- STATUS BLOCK v3-RECONCILIATION -->
> **STATUS: UNREVIEWED**
>
> - Not yet reviewed against main_Tier_1_Examples_v3.xlsx or GBPJPY_1550_Model_Tier_1_Rulebook. Content may be current; it has simply not been checked.
>
> Reconciliation pass: 2026-07-19. Authority for Tier 1 thresholds, timing and
> measurement conventions is `main_Tier_1_Examples_v3.xlsx` (Definitions sheet),
> then `GBPJPY_1550_Model_Tier_1_Rulebook`.

# AI Output Schema

## Metadata
- Path: AI Policy > Output Schema
- Status: Draft — based on Architecture.md's example response format, tightened to require
  evidence/concerns to cite specific structured fields rather than free text

## Purpose
Architecture.md's example AI response format is a good starting point, but as flagged in the
architecture review, "evidence" and "concerns" as free text risk becoming plausible-sounding
fabrication unless each line is bound to a specific field the AI was actually given. This schema
tightens that.

## Schema
```json
{
  "classification": "valid_candidate | invalid_candidate | ambiguous",
  "quality_score": 0,
  "evidence": [
    {
      "claim": "External sell-side liquidity was taken",
      "source_field": "LiquidityPool[LP-88].state == ACTIVATED",
      "epistemic_status": "CALCULATED"
    }
  ],
  "concerns": [
    {
      "claim": "Mitigation depth is larger than in validated examples",
      "source_field": "MitigationState[OP-123].approach_depth == 0.91",
      "epistemic_status": "CALCULATED",
      "comparison_basis": "historical_examples_query_id or null if no comparison was made"
    }
  ],
  "missing_information": [],
  "hard_rule_status": "PASS_THROUGH_ONLY — this field echoes StrategyCandidate.hard_rules verbatim; the AI does not compute or alter it",
  "summary": "Plain-language synthesis, must not introduce any claim not already present in evidence/concerns above",
  "model_version": "string"
}
```

## Key Differences from Architecture.md's Original Example
- Every `evidence`/`concerns` item requires a `source_field` pointing to a specific object/field
  the AI was actually given (a Tracker, Event, or Object_Schemas instance) — not a bare string.
  This is what prevents the free-text hallucination risk flagged in the Architecture.md review.
- Every item also carries its own `epistemic_status`, so a CALCULATED fact and an INFERRED
  interpretation don't get flattened into the same-looking bullet point.
- `hard_rule_status` is explicitly a pass-through field, reinforcing AI_Policy/Responsibilities.md's
  rule that the AI cannot alter hard-gate results — it can only display what code already decided.
- `summary` is constrained to synthesize only what's already in `evidence`/`concerns`, specifically
  to prevent the summary paragraph from being where ungrounded claims sneak back in after the
  structured fields were done properly.

## Open Questions / Deliberately Deferred
- `comparison_basis` in concerns assumes the Historical Examples Database (Architecture.md
  component 8) exists and is queryable — it doesn't yet.
- No schema yet for the "ambiguity warnings" and "questions it cannot resolve" outputs
  Architecture.md's component 7 also mentions — this version covers evidence/concerns/summary
  only; those two output types need their own schema addition.
