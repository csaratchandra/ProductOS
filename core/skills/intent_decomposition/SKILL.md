# Skill Contract: Intent Decomposition

## 1. Purpose
Decompose a PM's natural language product intent (1-3 sentences) into a structured product architecture with extracted problem statement, target personas, business outcomes, implied constraints, domain classification, and ambiguity flags with confidence scoring.

## 2. Trigger / When To Use
- PM invokes `productos architect --intent "..."` with any mode (`--dry-run`, `--wizard`, `--auto`)
- PM provides 1-3 sentences describing a product concept
- Acceptable triggers: vague descriptions ("a healthcare app"), specific briefs ("FHIR R4 prior auth platform with AI review"), or incremental refinement during wizard mode

## 3. Prerequisites
- Intent text must be non-empty (minimum 10 characters)
- No workspace required for `--dry-run` mode
- `--wizard` and `--auto` modes require an active workspace for artifact persistence

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `intent_text` | `string` | CLI argument | Yes | `"A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"` | 10-500 characters |
| `mode` | `string` | CLI flag | No | `"auto"` | One of: `auto`, `wizard`, `dry_run` |
| `workspace_id` | `string` | workspace context | No | `"ws_healthcare"` | Required for `wizard` and `auto` modes |

## 5. Execution Steps
1. **Parse intent**: Extract problem statement, target personas, business goals, and implied constraints from raw text using NLP pattern matching and keyword extraction.
2. **Classify domain**: Map extracted terms to known domain packs (healthcare, finance, etc.) with confidence score.
3. **Detect personas**: Match persona archetypes from known patterns; flag novel persona references as archetype_gaps.
4. **Format outcomes**: Structure identified business goals as SMART-formatted outcome targets.
5. **Flag ambiguities**: Identify vague or conflicting statements; generate suggested clarifications.
6. **Score confidence**: Assign per-field confidence scores based on extraction specificity (observed > inferred > assumed).
7. **Emit decomposition**: Return `IntentDecomposition` artifact with all extracted fields, confidence metadata, and ambiguity flags.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `schema_version` | `string` | `intent_decomposition.schema.json` | Yes | Schema version constant "1.0.0" |
| `intent_decomposition_id` | `string` | `intent_decomposition.schema.json` | Yes | Unique identifier |
| `raw_text` | `string` | `intent_decomposition.schema.json` | Yes | Original intent text |
| `extracted_problem` | `string` | `intent_decomposition.schema.json` | Yes | Parsed problem statement |
| `extracted_outcomes` | `array` | `intent_decomposition.schema.json#/$defs/outcomeTarget` | Yes | Business outcomes identified |
| `inferred_personas` | `array` | `intent_decomposition.schema.json#/$defs/personaInference` | Yes | Persona matches with confidence |
| `domain_match` | `object` | `intent_decomposition.schema.json#/$defs/domainMatch` | Yes | Suggested domain pack with confidence |
| `confidence_scores` | `object` | `intent_decomposition.schema.json#/$defs/confidenceScores` | Yes | Per-field confidence (0.0-1.0) |
| `ambiguity_flags` | `array` | `intent_decomposition.schema.json#/$defs/ambiguityFlag` | No | Unclear statements flagged for PM |
| `suggested_clarifications` | `array` | `intent_decomposition.schema.json` | No | Specific questions to ask PM |

Primary output artifact: `intent_decomposition` → maps to `core/schemas/artifacts/intent_decomposition.schema.json`

## 7. Guardrails
- **Empty intent**: If `intent_text` length < 10 characters → raise ValueError with message "Intent text must be at least 10 characters"
- **No domain detected**: If no domain pack matches with confidence ≥0.3 → set `domain_match.domain` to "general" with low confidence; flag in ambiguity_flags
- **Conflicting constraints**: If constraints conflict (e.g., HIPAA + no PHI handling) → flag as ambiguity; do not silently resolve
- **Low-confidence personas**: When persona confidence < 0.5 → include in output but mark as requiring PM confirmation in wizard mode
- **When to stop and escalate to PM**: Wizard mode pauses at 2 confirmation points: (1) persona/domain confirmation, (2) constraint confirmation

## 8. Gold Standard Checklist
- [ ] Problem extraction captures the core user or business problem, not just feature description
- [ ] Persona inference includes role description with archetype classification
- [ ] Domain confidence ≥0.9 for clear intents (e.g., "HIPAA-compliant prior auth" → healthcare)
- [ ] Ambiguity detection fires on vague inputs (e.g., "a healthcare app" → which segment?)
- [ ] Every inferred persona has a confidence score
- [ ] Outcome targets are SMART-formatted (specific, measurable, achievable, relevant, time-bound)
- [ ] Evidence traceability: every extracted field references source text segments

## 9. Examples

### Excellent Output (5/5)
```json
{
  "schema_version": "1.0.0",
  "intent_decomposition_id": "id_001",
  "raw_text": "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review",
  "extracted_problem": "US healthcare providers and payers struggle with slow, manual prior authorization processes that delay patient care and increase administrative costs",
  "extracted_outcomes": [
    {"outcome_id": "out_001", "description": "Reduce prior authorization processing time from 7 days to under 24 hours", "measurement": "Average processing time per authorization request", "confidence": 0.85},
    {"outcome_id": "out_002", "description": "Achieve AI-assisted review accuracy of 95% or higher on standard authorization requests", "measurement": "AI review accuracy rate vs human audit", "confidence": 0.7}
  ],
  "inferred_personas": [
    {"persona_id": "pers_provider", "label": "Healthcare Provider", "role_description": "Physician or clinical staff who submits prior authorization requests", "confidence": 0.92, "archetype_type": "user"},
    {"persona_id": "pers_payer", "label": "Payer Reviewer", "role_description": "Insurance company staff who reviews and adjudicates authorization requests", "confidence": 0.88, "archetype_type": "operator"}
  ],
  "domain_match": {"domain": "healthcare", "sub_domains": ["prior_authorization", "clinical_workflow"], "regions": ["us"], "confidence": 0.95},
  "confidence_scores": {"overall": 0.85, "problem": 0.9, "personas": 0.85, "domain": 0.95, "outcomes": 0.7, "constraints": 0.8}
}
```

### Poor Output (2/5) — What to Avoid
```json
{
  "schema_version": "1.0.0",
  "intent_decomposition_id": "id_002",
  "raw_text": "build an app",
  "extracted_problem": "build an app",
  "extracted_outcomes": [],
  "inferred_personas": [],
  "domain_match": {"domain": "general", "confidence": 0.1},
  "confidence_scores": {"overall": 0.1, "problem": 0.1, "personas": 0.1, "domain": 0.1}
}
```

**Why this fails:** Intent text is too vague to produce meaningful extraction. No domain detected, no personas inferred, no outcomes extracted. The output mirrors the input instead of flagging ambiguity. Should have triggered `ambiguity_flags` with suggested clarifications.

## 10. Cross-References
- **Upstream skills**: None (CLI invocation)
- **Downstream skills**: `architecture_synthesis`, `gap_intelligence`, `domain_intelligence`
- **Related artifact schemas**: `core/schemas/artifacts/intent_decomposition.schema.json`
- **Related entity schemas**: `core/schemas/entities/persona.schema.json`
- **Related CLI**: `productos architect --intent "..."`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Keyword extraction only | Intent text must contain explicit domain keywords | 60% accuracy on persona detection |
| 1→10 | Pattern matching + keyword extraction | Intent text + domain pack keyword registry | 80% accuracy on persona detection |
| 10→100 | LLM-assisted semantic parsing | Workspace context for domain-specific patterns | 90% accuracy on persona detection |
| 100→10K+ | Full semantic understanding with ambiguity detection and self-correction | Multi-turn clarification via wizard mode | 95% accuracy with confidence calibration |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/intent_decomposition.schema.json`
- **Test file**: `tests/test_v14_intent_engine.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
