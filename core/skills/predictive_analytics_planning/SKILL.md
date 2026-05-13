# Skill Contract: Predictive Analytics Planning

## 1. Purpose
Auto-generate a complete analytics instrumentation plan from product architecture — inferring event taxonomy, metrics, funnel drop-offs, A/B test candidates, privacy risks, and dashboard layouts.

## 2. Trigger / When To Use
- After architecture synthesis completes for a product with 2+ handoffs or personas
- When a PM requests analytics planning for an existing architecture
- As part of the full `productos architect` pipeline (always included in auto mode)

## 3. Prerequisites
- Completed `ProductArchitecture` container with workflow orchestration map, persona pack, and journey maps

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Description |
|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture with workflow, personas, and journeys |

## 5. Execution Steps
1. **Infer event taxonomy**: From handoffs and personas, generate event names, triggers, properties, and privacy classifications.
2. **Define metrics**: From events, define metric formulas, data sources, aggregation methods, and alert thresholds.
3. **Predict funnel drop-offs**: From journey stage emotion scores, predict stages with highest drop-off risk.
4. **Suggest A/B tests**: From handoff patterns, identify test candidates with hypothesis and expected lift.
5. **Assess privacy risks**: Classify events by regulation (GDPR, HIPAA, PCI-DSS) and suggest mitigations.
6. **Design dashboards**: Per audience (PM, executive, operator), suggest widget layouts.
7. **Emit AnalyticsPlan**: Return structured plan with all analytics dimensions.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `event_taxonomy[]` | `array` | `analytics_plan.schema.json` | Yes | Events with triggers, properties, persona refs, privacy classification |
| `metric_definitions[]` | `array` | `analytics_plan.schema.json` | Yes | Metrics with formulas, data sources, aggregation, alert thresholds |
| `predicted_funnel_dropoffs[]` | `array` | `analytics_plan.schema.json` | No | Stages with predicted drop-off rates and improvement suggestions |
| `ab_test_candidates[]` | `array` | `analytics_plan.schema.json` | No | A/B test hypotheses with target metrics and expected lift |

Primary output artifact: `analytics_plan` → maps to `core/schemas/artifacts/analytics_plan.schema.json`

## 7. Guardrails
- **Event trigger check**: Only infer events that have clear triggers in the architecture; do not fabricate events
- **Privacy defaults**: Privacy classification defaults to "behavioral" unless domain context (HIPAA, PCI-DSS) indicates otherwise
- **Funnel prediction requirement**: Funnel drop-offs require emotion scores on journey stages; if absent, skip without error
- **When to stop and escalate to PM**: If event count exceeds 50 for a medium-complexity architecture, flag for simplification

## 8. Gold Standard Checklist
- [ ] Event count scales with architecture complexity (at least 2 events per handoff)
- [ ] Every event has a clear trigger, persona reference, and property list
- [ ] Metrics map to measurable outcomes in the architecture
- [ ] Funnel predictions are based on journey stage complexity, not fabricated
- [ ] Privacy classification is domain-appropriate and regulation-aware
- [ ] Dashboard specs are audience-appropriate (PM vs executive vs operator)

## 9. Examples

### Excellent Output (5/5)
```json
{
  "event_taxonomy": [
    {"event_name": "prior_auth_submitted", "trigger": "Provider submits prior auth request", "persona_ref": "pers_provider", "properties": ["auth_id", "patient_id", "procedure_code"], "privacy_classification": "phi"}
  ],
  "metric_definitions": [
    {"metric_name": "prior_auth_processing_time", "formula": "p50 of handoff completion time", "data_sources": ["analytics_pipeline"], "aggregation": "p50/p90/p95"}
  ],
  "predicted_funnel_dropoffs": [
    {"stage": "payer_review", "predicted_dropoff_rate": 0.15, "suggested_improvement": "Add status notifications to reduce abandonment"}
  ]
}
```

## 10. Cross-References
- **Upstream skills**: `architecture_synthesis`
- **Downstream skills**: `gap_intelligence`, `outcome_intelligence`
- **Related artifact schemas**: `core/schemas/artifacts/analytics_plan.schema.json`, `core/schemas/artifacts/product_architecture.schema.json`
- **Test file**: `tests/test_v14_predictive_analytics.py`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Handoff-count-based event inference | Workflow orchestration map | 1 event per handoff, no privacy classification |
| 1→10 | Pattern-matched event generation | Workflow + persona pack | 2 events per handoff with privacy classification |
| 10→100 | LLM-assisted analytics architecture | Full architecture + domain pack | Complete plan with funnel predictions and A/B tests |
| 100→10K+ | Self-calibrating analytics from historical data | Historical event performance data | Predictive funnel optimization with auto-suggested metrics |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/analytics_plan.schema.json`
- **Test file**: `tests/test_v14_predictive_analytics.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
