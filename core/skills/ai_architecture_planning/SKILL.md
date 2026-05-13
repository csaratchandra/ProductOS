# Skill Contract: AI Architecture Planning

## 1. Purpose
Generate an AI-native architecture plan that identifies automation opportunities, human-in-the-loop checkpoints, per-persona AI features, trust indicators, consent flows, data privacy guards, failure modes, and regulatory alignment for every product architecture.

## 2. Trigger / When To Use
- After architecture synthesis completes with workflow orchestration map
- As part of the full `productos architect` pipeline (always included in auto mode)

## 3. Prerequisites
- Completed `ProductArchitecture` with workflow orchestration map and persona archetype pack

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Description |
|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture with workflow and personas |

## 5. Execution Steps
1. **Analyze handoffs**: Identify workflow handoffs suitable for AI assistance (generative, predictive, classificatory).
2. **Identify checkpoints**: Determine which handoffs require human-in-the-loop approval.
3. **Map per-persona AI features**: For each persona, infer AI-powered capabilities relevant to their role.
4. **Define trust framework**: Specify confidence visualization, uncertainty communication, and override mechanisms.
5. **Consent and privacy**: Identify where user consent is required and what data AI systems access.
6. **Failure mode analysis**: For each automation, define detection, rollback, and fallback procedures.
7. **Regulatory alignment**: Map against EU AI Act, US AI EO, and domain-specific regulations.
8. **Emit AILayerPlan**: Return structured plan with all AI architecture dimensions.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `automation_candidates[]` | `array` | `ai_layer_plan.schema.json` | Yes | Workflow stages suitable for AI with ROI estimates |
| `human_in_the_loop_checkpoints[]` | `array` | `ai_layer_plan.schema.json` | No | Stages requiring human approval with escalation rules |
| `per_persona_ai_features[]` | `array` | `ai_layer_plan.schema.json` | No | AI features per persona with triggers and outputs |
| `failure_modes[]` | `array` | `ai_layer_plan.schema.json` | No | Failure detection, rollback, and fallback per stage |

Primary output artifact: `ai_layer_plan` → maps to `core/schemas/artifacts/ai_layer_plan.schema.json`

## 7. Guardrails
- **High-risk automations**: Any automation with confidence < 0.7 must include a human-in-the-loop checkpoint
- **Failure modes required**: Every automation candidate must have at least one failure mode defined
- **Regulatory override**: If domain requires human oversight (e.g., healthcare diagnosis), force checkpoint regardless of confidence
- **When to stop and escalate to PM**: If >5 high-risk automations identified, flag for PM risk review

## 8. Gold Standard Checklist
- [ ] Automation candidates map to actual workflow handoffs
- [ ] Human-in-the-loop checkpoints include escalation rules and fallback paths
- [ ] Per-persona AI features are role-appropriate (e.g., provider gets AI-assisted review, not fully automated decisions)
- [ ] Trust indicators include confidence visualization and override mechanisms
- [ ] Consent flows identify where user consent is required and opt-out paths
- [ ] Data privacy guards specify retention, anonymization, and what AI can access
- [ ] Failure modes have detection, rollback, and fallback for every automation
- [ ] Regulatory alignment maps to relevant regulations (EU AI Act, US AI EO, domain-specific)

## 9. Examples

### Excellent Output (5/5)
```json
{
  "automation_candidates": [
    {"workflow_stage": "prior_auth_review", "automation_approach": "AI-assisted review", "estimated_roi": "40% reduction in processing time", "confidence": 0.7}
  ],
  "human_in_the_loop_checkpoints": [
    {"stage": "final_approval", "escalation_rules": "If AI confidence < 0.7, route to human reviewer"}
  ],
  "regulatory_alignment": [
    {"regulation": "EU AI Act", "compliance_status": "partial", "required_actions": ["Implement human oversight for high-risk automations"]}
  ]
}
```

## 10. Cross-References
- **Upstream skills**: `architecture_synthesis`, `domain_intelligence`
- **Related artifact schemas**: `core/schemas/artifacts/ai_layer_plan.schema.json`
- **Test file**: `tests/test_v14_ai_architecture.py`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Rule-based handoff classification | Workflow orchestration map | Automation candidates only |
| 1→10 | Pattern-matched AI opportunity detection | Workflow + persona pack | Automation + human-in-the-loop |
| 10→100 | LLM-assisted AI architecture generation | Full architecture + domain pack | Complete AI layer plan with all 8 dimensions |
| 100→10K+ | Self-learning AI architecture optimization | Historical AI performance data | Predictive AI architecture with ROI calibration |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/ai_layer_plan.schema.json`
- **Test file**: `tests/test_v14_ai_architecture.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
