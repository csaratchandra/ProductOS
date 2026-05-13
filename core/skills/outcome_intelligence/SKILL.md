# Skill Contract: Outcome Intelligence

## 1. Purpose
Generate a full outcome cascade from product architecture — mapping business outcomes to product outcomes, feature metrics, user actions, and data sources — with confidence scoring, measurement gap detection, and cascade update suggestions when architecture changes.

## 2. Trigger / When To Use
- After architecture synthesis completes and returns a `ProductArchitecture` container
- When a PM requests outcome cascade generation for an existing architecture
- As part of the full `productos architect` pipeline (always included in auto mode)

## 3. Prerequisites
- Completed `ProductArchitecture` container with persona archetype pack, workflow orchestration map, and component PRDs

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Description |
|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture with all artifact groups |

## 5. Execution Steps
1. **Extract outcomes**: Parse MasterPRD and component PRDs for stated and implied business outcomes.
2. **Build cascade levels**: Map each business outcome through product outcome → feature metric → user action → data source.
3. **Assign confidence**: Tag each cascade entry as observed (explicitly stated), inferred (derived from context), or assumed (default).
4. **Detect measurement gaps**: Identify outcomes with no linked metric, metrics with no data source, or broken traceability.
5. **Format cascade**: Return structured `OutcomeCascade` artifact.
6. **Analyze architecture delta**: When architecture changes, suggest new outcomes, metrics, and reprioritization.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `cascade[]` | `array` | `outcome_cascade.schema.json` | Yes | 5-level outcome cascade with entries per level |
| `measurement_gaps[]` | `array` | `outcome_cascade.schema.json` | No | Gaps where outcomes lack measurement or data sources |

Primary output artifact: `outcome_cascade` → maps to `core/schemas/artifacts/outcome_cascade.schema.json`

## 7. Guardrails
- **No outcomes found**: Return cascade with single "Improve workflow efficiency" inferred outcome and a measurement gap flag
- **Low-confidence outcomes**: When confidence is "assumed", flag in PM briefing as requiring confirmation
- **Broken links**: If an outcome references a non-existent metric or data source, emit a measurement gap
- **When to stop and escalate to PM**: If all outcomes have "assumed" confidence, suggest PM provide explicit business outcomes

## 8. Gold Standard Checklist
- [ ] Every business outcome traces through all 5 cascade levels
- [ ] Each entry has a confidence label (observed / inferred / assumed)
- [ ] Measurement gaps are identified and explained
- [ ] Data sources are suggested for each metric
- [ ] Cascade updates respect architecture delta (additive, not destructive)

## 9. Examples

### Excellent Output (5/5)
```json
{
  "cascade": [
    {"level": "Business Outcome", "entries": [{"id": "bo_001", "description": "Reduce prior auth denial rate by 40%", "confidence": "inferred"}]},
    {"level": "Product Outcome", "entries": [{"id": "po_001", "description": "AI review accuracy >= 95%", "confidence": "inferred", "linked_business_outcome": "bo_001"}]},
    {"level": "Feature Metric", "entries": [{"id": "fm_001", "description": "Model precision on authorization requests", "measurement": "precision@k", "data_source": "AI model evaluation pipeline"}]},
    {"level": "User Action", "entries": [{"id": "ua_001", "description": "Provider submits complete prior auth request", "linked_feature_metric": "fm_001"}]},
    {"level": "Data Source", "entries": [{"id": "ds_001", "description": "EHR integration + payer adjudication API"}]}
  ]
}
```

## 10. Cross-References
- **Upstream skills**: `architecture_synthesis`
- **Downstream skills**: `gap_intelligence`, `predictive_analytics_planning`
- **Related artifact schemas**: `core/schemas/artifacts/outcome_cascade.schema.json`
- **Test file**: `tests/test_v14_outcome_intelligence.py`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Keyword-based outcome extraction | MasterPRD with explicit outcomes section | 2 cascade levels |
| 1→10 | Pattern-matched cascade inference | Architecture with persona and workflow data | 4 cascade levels with confidence |
| 10→100 | LLM-assisted semantic outcome mapping | Full architecture context | 5 levels with measurement gaps |
| 100→10K+ | Self-suggesting outcomes from market data | Historical outcome-performance data | Proactive outcome recommendations |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/outcome_cascade.schema.json`
- **Test file**: `tests/test_v14_outcome_intelligence.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
