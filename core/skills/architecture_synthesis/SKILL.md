# Skill Contract: Architecture Synthesis

## 1. Purpose
Generate all 6 artifact layers in parallel from a MasterPRD — persona archetype packs, workflow orchestration maps, component PRD stubs, customer journey maps, API contract hypotheses, and zoom navigation maps — with cross-layer consistency validation and UUID cross-linking.

## 2. Trigger / When To Use
- After `intent_decomposition` completes and MasterPRD is generated
- When PM confirms decomposition in wizard mode
- As part of the full `productos architect` pipeline (always included in auto mode)

## 3. Prerequisites
- Completed `IntentDecomposition` from `intent_engine`
- Generated `MasterPRD` from `intent_engine.generate_master_prd()`
- Domain pack loaded if domain was identified with confidence >= 0.5

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `master_prd` | `object` | `intent_decomposition.schema.json` | Yes | Full MasterPRD from intent engine | Must include persona_coverage_map and scope boundaries |
| `mode` | `string` | CLI flag | No | `"standard"` | One of: `standard`, `quick`, `comprehensive` |

## 5. Execution Steps
1. **Synthesize persona archetype pack**: Extract persona definitions from MasterPRD persona_coverage_map; assign JTBD, goals, and pain points per archetype.
2. **Build workflow orchestration map**: Infer handoffs between personas based on shared artifacts and workflow dependencies; annotate with inferred SLAs.
3. **Generate component PRD stubs**: Decompose at natural handoff boundaries; each component gets a PRD stub with scope, interfaces, and dependencies.
4. **Create customer journey maps**: Per persona, map stages linked to orchestration map states; include emotion scores and touchpoints.
5. **Hypothesize API contracts**: From shared artifact mutation tracking, generate API contract hypotheses with fields, types, and mutation operations.
6. **Build zoom navigation map**: Hierarchical component tree with drill-down paths.
7. **Cross-link artifacts**: Assign UUIDs to all artifacts; create cross_links array in ProductArchitecture container.
8. **Validate cross-consistency**: Run all consistency checks — persona presence, handoff completeness, orphan detection, circular dependency check.
9. **Emit ProductArchitecture**: Return unified container with all artifacts, cross-links, and generation metadata.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `artifacts[]` | `array` | `product_architecture.schema.json` | Yes | All generated artifacts with uuid, type, version, confidence_metadata |
| `cross_links[]` | `array` | `product_architecture.schema.json#/$defs/crossLink` | Yes | Source → target UUID links with link_type and confidence |
| `persona_archetype_pack` | `object` | `product_architecture.schema.json` | Yes | Persona definitions with JTBD, goals, pain points |
| `workflow_orchestration_map` | `object` | `product_architecture.schema.json` | Yes | Handoff map with SLAs and compliance gates |
| `component_prds[]` | `array` | `product_architecture.schema.json` | Yes | Component PRD stubs with scope and dependencies |
| `customer_journey_maps[]` | `array` | `product_architecture.schema.json` | Yes | Per-persona journey maps linked to orchestration states |
| `api_contract_hypotheses[]` | `array` | `product_architecture.schema.json` | Yes | API contracts from shared artifact patterns |
| `zoom_navigation_map` | `object` | `product_architecture.schema.json` | Yes | Hierarchical component tree |
| `generation_metadata` | `object` | `product_architecture.schema.json` | Yes | mode, duration_ms, decomposition_uuid |

Primary output artifact: `product_architecture` → maps to `core/schemas/artifacts/product_architecture.schema.json`

## 7. Guardrails
- **Parallel execution**: All 6 engines run simultaneously; if any engine fails, its artifact group defaults to empty with a warning
- **Orphan detection**: After synthesis, scan for artifacts with no upstream or downstream links; flag as warnings
- **Circular dependency**: If component graph has cycles, break ties by removing lowest-confidence dependency edge
- **SLA inference**: When no explicit SLA is provided, infer from journey stage complexity scores (simple=24h, medium=72h, complex=168h)
- **When to stop and escalate to PM**: If cross-consistency validation finds >5 critical failures, pause and offer to regenerate

## 8. Gold Standard Checklist
- [ ] All 6 artifact groups generated (non-empty for non-trivial architectures)
- [ ] Every persona in archetype pack appears in orchestration map
- [ ] Every handoff has source/target in archetype pack
- [ ] Every component PRD has assigned personas from archetype pack
- [ ] Every journey stage links to orchestration map state
- [ ] Shared artifacts in orchestration map have API contract fields
- [ ] No orphan artifacts exist
- [ ] No circular dependencies in component graph
- [ ] All artifacts have UUID references in cross_links

## 9. Examples

### Excellent Output (5/5)
```json
{
  "product_architecture_id": "pa_001",
  "artifacts": [
    {"uuid": "art_001", "type": "persona_archetype_pack", "version": "1.0.0", "confidence_metadata": {"overall": 0.85}},
    {"uuid": "art_002", "type": "workflow_orchestration_map", "version": "1.0.0", "confidence_metadata": {"overall": 0.82}}
  ],
  "cross_links": [
    {"source_uuid": "art_001", "target_uuid": "art_002", "link_type": "references", "confidence": 0.9}
  ],
  "generation_metadata": {"mode": "standard", "duration_ms": 4200, "decomposition_uuid": "id_001"}
}
```

### Poor Output (2/5) — What to Avoid
```json
{"artifacts": [], "cross_links": []}
```

**Why this fails:** Empty artifacts array means synthesis produced nothing. Every non-trivial architecture should generate at minimum persona pack and workflow map.

## 10. Cross-References
- **Upstream skills**: `intent_decomposition`
- **Downstream skills**: `gap_intelligence`, `domain_intelligence`, `predictive_simulation`
- **Related artifact schemas**: `core/schemas/artifacts/product_architecture.schema.json`, `core/schemas/artifacts/consistency_report.schema.json`
- **Related entity schemas**: `core/schemas/entities/persona.schema.json`
- **Related CLI**: `productos architect --intent "..."`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Template-based artifact generation | MasterPRD with persona list | 4/6 artifact groups generated |
| 1→10 | Pattern-based synthesis | MasterPRD + domain pack | 6/6 artifact groups, basic cross-links |
| 10→100 | LLM-assisted semantic synthesis | Full architecture context | 6/6 groups with confidence scoring and cross-layer consistency |
| 100→10K+ | Self-validating synthesis with auto-repair | Historical architecture patterns | Zero orphan artifacts, optimal decomposition |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/product_architecture.schema.json`
- **Test file**: `tests/test_v14_architecture_synthesis.py`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
