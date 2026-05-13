# Skill Contract: Gap Intelligence

## 1. Purpose
Detect gaps across all architecture layers — missing handoffs, orphan personas, SLA inconsistencies, compliance gaps, broken traceability — with narrative explanations of why each gap matters and concrete fix suggestions.

## 2. Trigger / When To Use
- After `architecture_synthesis` completes and returns a `ProductArchitecture` container
- When a PM explicitly requests `productos architect --intent "..."` in any mode (gap analysis is always included)
- When cross-layer consistency validation detects issues that need narrative explanation

## 3. Prerequisites
- Completed `ProductArchitecture` container from `architecture_synthesis`
- Cross-consistency validation should be run first (gaps identified here complement validation results)

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture container | Must include artifact groups and cross_links |
| `consistency_report` | `object` | `consistency_report.schema.json` | No | Optional pre-consistency check results | Used to seed known failures |

## 5. Execution Steps
1. **Analyze handoffs**: Check every persona in archetype pack has at least one handoff role; detect missing handoffs between personas that share workflow objects.
2. **Check SLA consistency**: Verify SLA targets in orchestration map are internally consistent and achievable given handoff complexity.
3. **Scan compliance gates**: For regulated domains, verify required compliance gates exist at relevant handoff points.
4. **Validate persona coverage**: Ensure every journey stage has an assigned persona and every persona has at least one journey stage.
5. **Check API contracts**: Verify every shared artifact in orchestration map has a corresponding API contract definition.
6. **Trace outcomes to metrics**: Ensure every business outcome has at least one measurable feature metric.
7. **Detect broken links**: Scan cross-links for missing or invalid artifact UUIDs.
8. **Detect circular dependencies**: Walk component dependency graph for cycles.
9. **Generate narrative explanations**: For each gap, produce impact statement, suggestion, and confidence score.
10. **Emit gap analysis**: Return `GapAnalysis` with all detected gaps, summary statistics, and auto-fix payloads.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `gaps[]` | `array` | `gap_analysis.schema.json#/$defs/gap` | Yes | All detected gaps with narratives |
| `gaps[].gap_type` | `string` | Enum in schema | Yes | Type of gap detected |
| `gaps[].severity` | `string` | Enum in schema | Yes | critical / warning / info |
| `gaps[].impact` | `string` | `gap_analysis.schema.json#/$defs/gap` | Yes | Narrative of impact |
| `gaps[].suggestion` | `string` | `gap_analysis.schema.json#/$defs/gap` | Yes | Concrete fix suggestion |
| `summary` | `object` | `gap_analysis.schema.json` | Yes | Counts by severity |

Primary output artifact: `gap_analysis` → maps to `core/schemas/artifacts/gap_analysis.schema.json`

## 7. Guardrails
- **No gaps found**: Return clean report with `total_gaps: 0` and confirmation message — never fabricate gaps
- **Low-confidence gaps**: If confidence < 0.5, mark severity as `info` and flag in PM briefing as requiring confirmation
- **Circular dependency detected**: Always emit as `critical` severity — prevents infinite loops in execution
- **Auto-fix available**: Only set `auto_fix_available = true` when the exact fix can be generated (e.g., adding a missing handoff with known source/target)
- **When to stop and escalate to PM**: If >10 critical gaps detected, pause and ask PM to prioritize which gaps to address first

## 8. Gold Standard Checklist
- [ ] Every persona in archetype pack checked for handoff presence
- [ ] SLA values compared across handoffs for consistency
- [ ] Compliance gates verified against domain pack requirements
- [ ] Impact narratives explain WHY the gap matters, not just what is missing
- [ ] Suggestions are concrete and implementable (schema additions, PRD text, workflow changes)
- [ ] Confidence scored per gap
- [ ] Evidence traceability: each gap references affected artifact UUIDs
- [ ] Auto-fix payload provided when fix is deterministic

## 9. Examples

### Excellent Output (5/5)
```json
{
  "gap_id": "gap_001",
  "gap_type": "missing_handoff",
  "severity": "critical",
  "description": "Provider persona has no handoff to Payer persona in prior authorization workflow",
  "impact": "Without this handoff, the Provider cannot submit prior authorization requests to the Payer. The authorization workflow dead-ends at Provider completion with no receiver. This blocks the entire prior auth process.",
  "suggestion": "Add handoff from Provider to Payer with shared artifact 'prior_auth_request', trigger event 'Provider submits prior auth request', and SLA target of 72 hours per CMS requirements",
  "auto_fix_available": true,
  "confidence": 0.92
}
```

### Poor Output (2/5) — What to Avoid
```json
{
  "gap_id": "gap_001",
  "gap_type": "missing_handoff",
  "severity": "critical",
  "description": "missing handoff",
  "impact": "bad",
  "suggestion": "fix it",
  "confidence": 0.1
}
```

**Why this fails:** Impact narrative is too vague, suggestion is not actionable, confidence is not meaningful. Every gap must explain why it matters and how to fix it.

## 10. Cross-References
- **Upstream skills**: `intent_decomposition`, `architecture_synthesis`
- **Downstream skills**: `domain_intelligence`, `predictive_simulation`
- **Related artifact schemas**: `core/schemas/artifacts/gap_analysis.schema.json`, `core/schemas/artifacts/consistency_report.schema.json`
- **Related entity schemas**: `core/schemas/entities/persona.schema.json`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Rule-based pattern matching only | Must have complete artifact set | 70% gap detection rate |
| 1→10 | Enhanced pattern matching + heuristics | Domain-aware compliance rules | 85% gap detection rate |
| 10→100 | LLM-assisted narrative generation | Cross-layer consistency report seeded | 90% gap detection rate |
| 100→10K+ | Full semantic understanding with self-healing | Historical gap patterns for prediction | 95% detection + auto-fix |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/gap_analysis.schema.json`
- **Test file**: `tests/test_v14_gap_intelligence.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
