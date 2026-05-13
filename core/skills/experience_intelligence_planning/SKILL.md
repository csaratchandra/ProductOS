# Skill Contract: Experience Intelligence Planning

## 1. Purpose
Generate a predictive experience plan from product architecture — per-persona device context prediction, progressive enhancement rules, accessibility mapping, cognitive load analysis, performance targets, and cross-persona continuity planning.

## 2. Trigger / When To Use
- After architecture synthesis completes with persona archetype pack and journey maps
- As part of the full `productos architect` pipeline (always included in auto mode)

## 3. Prerequisites
- Completed `ProductArchitecture` with persona archetype pack, customer journey maps, and workflow orchestration map

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Description |
|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture with persona pack and journeys |

## 5. Execution Steps
1. **Predict device context**: Per persona, infer primary and secondary devices from domain, persona role, and journey context.
2. **Define progressive enhancement**: Map base experience (web) to enhanced experience (native app, offline sync) with triggers.
3. **Set performance targets**: From domain pack, apply load time, interaction time, and offline sync interval targets.
4. **Apply accessibility mapping**: Auto-apply WCAG 2.1 AA + regional requirements (Section 508, EN 301 549) per persona.
5. **Model cognitive load**: Analyze journey stage decision points per persona; suggest simplifications for high-cognitive-load journeys.
6. **Plan cross-persona continuity**: Identify data that must sync across persona device switches.
7. **Predict offline capability**: From persona journey context, predict required offline duration.
8. **Emit ExperiencePlan**: Return structured plan with all per-persona and per-workflow-stage recommendations.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `per_persona_device_context[]` | `array` | `experience_plan.schema.json` | Yes | Persona device predictions, offline capability, accessibility |
| `performance_targets[]` | `array` | `experience_plan.schema.json` | No | Load time, interaction time targets |
| `cognitive_load_analysis[]` | `array` | `experience_plan.schema.json` | No | Decision point counts and simplification suggestions |

Primary output artifact: `experience_plan` → maps to `core/schemas/artifacts/experience_plan.schema.json`

## 7. Guardrails
- **No persona data**: Return minimal plan with generic web-only defaults
- **Low-confidence predictions**: When device prediction confidence < 0.5, flag for PM review
- **Accessibility overrides**: PM can provide explicit accessibility requirements that override auto-detection
- **When to stop and escalate to PM**: If cognitive load score > 20 decision points for any persona, flag as critical UX risk

## 8. Gold Standard Checklist
- [ ] Every persona has a predicted primary device
- [ ] Device context matches persona role and domain (e.g., clinical → tablet, office → desktop, mobile → phone)
- [ ] Accessibility requirements are domain-appropriate and region-aware
- [ ] Cognitive load analysis flags high-decision-point journeys
- [ ] Cross-persona continuity is addressed for multi-persona workflows

## 9. Examples

### Excellent Output (5/5)
```json
{
  "per_persona_device_context": [
    {"persona": "Healthcare Provider", "predicted_primary_device": "tablet", "predicted_secondary_device": "desktop", "offline_capability": true, "accessibility_requirements": "WCAG 2.1 AA, Section 508"},
    {"persona": "Payer Reviewer", "predicted_primary_device": "desktop", "offline_capability": false, "accessibility_requirements": "WCAG 2.1 AA"}
  ],
  "performance_targets": [
    {"metric": "load_time", "target": "<3s (patient waiting)"},
    {"metric": "offline_sync_interval", "target": "4 hours (rural provider)"}
  ]
}
```

## 10. Cross-References
- **Upstream skills**: `architecture_synthesis`, `domain_intelligence`
- **Related artifact schemas**: `core/schemas/artifacts/experience_plan.schema.json`
- **Test file**: `tests/test_v14_experience_intelligence.py`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Role-based device defaults | Persona archetype pack only | Primary device per persona |
| 1→10 | Domain-aware device prediction | Persona pack + journey maps | Device context + performance targets |
| 10→100 | LLM-assisted cognitive load analysis | Full architecture + domain pack | Full experience plan with accessibility |
| 100→10K+ | Predictive UX with A/B test suggestions | Historical UX data + persona telemetry | Proactive experience optimization |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/experience_plan.schema.json`
- **Test file**: `tests/test_v14_experience_intelligence.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
