# Skill Contract: Healthcare Domain Intelligence

## 1. Purpose
Activate and validate US healthcare domain intelligence from product architecture — mapping FHIR R4 resources, HIPAA compliance gates, CMS SLAs, X12 transactions, and clinical workflow patterns into ProductOS artifacts.

## 2. Trigger / When To Use
- When `domain_intelligence.auto_activate()` detects healthcare intent keywords (prior auth, HIPAA, provider, payer, FHIR, CMS)
- When a PM explicitly enables the healthcare domain pack via `productos domain enable --pack healthcare --region us`
- As part of the `productos architect` pipeline when intent matches healthcare domain

## 3. Prerequisites
- `domain_intelligence.py` runtime available with healthcare domain pack loaded
- `core/domains/healthcare/base.schema.overlay.json` and `regions/us.schema.overlay.json` present and valid
- Workflow orchestration map or PRD with healthcare-relevant personas and handoffs

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Description |
|---|---|---|---|---|
| `architecture` | `object` | `product_architecture.schema.json` | Yes | Full product architecture with personas, workflows, PRDs |
| `region` | `string` | N/A | Yes | Region code (`us`, `eu`, `uk`) for regional overlay activation |
| `sub_packs` | `array` | N/A | No | Sub-pack IDs to activate (`provider`, `payer`, `insurer`, `government`) |

## 5. Execution Steps
1. **Detect healthcare domain**: Scan intent and architecture for healthcare keywords; compute confidence score (≥0.85 threshold).
2. **Load base overlay**: Load `base.schema.overlay.json` — FHIR R4 core resources (Patient, Coverage, Claim, Encounter, Practitioner, Organization, MedicationRequest).
3. **Load regional overlay**: Load region-specific overlay — HIPAA, HITECH, CMS SLA constraints, X12 transaction codes, CPT/ICD-10/HCPCS.
4. **Validate overlays**: Check regional against base for contradictions (additive only, no field removal).
5. **Activate sub-packs**: Load sub-pack manifests (provider, payer, insurer) — validate persona archetype requirements.
6. **Inject compliance gates**: Add HIPAA compliance checkpoints (audit log, consent record, breach notification, data minimization, encryption) into orchestration map handoffs.
7. **Map FHIR resources**: Tag workflow shared artifacts with FHIR resource type suggestions from the base overlay.
8. **Enforce CMS SLAs**: Set prior authorization SLA to 72 hours; flag any orchestration map with conflicting SLAs.
9. **Validate compliance coverage**: Run compliance check against all handoffs — emit compliance report with gaps.
10. **Emit DomainActivation**: Return structured activation with compliance coverage, resource mappings, and gap report.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `domain` | `string` | `domain_activation.schema.json` | Yes | Activated domain identifier (`healthcare`) |
| `region` | `string` | `domain_activation.schema.json` | Yes | Activated region (`us`) |
| `compliance_checkpoints[]` | `array` | `compliance_report.schema.json` | Yes | Compliance gates injected into orchestration handoffs |
| `fhir_resource_map[]` | `array` | `domain_activation.schema.json` | Yes | FHIR resource to workflow artifact mappings |
| `sla_constraints[]` | `array` | `domain_activation.schema.json` | Yes | Regulatory SLA requirements (e.g., CMS 72h) |
| `coverage_gaps[]` | `array` | `compliance_report.schema.json` | No | Compliance checkpoints not covered by active overlays |

Primary output artifacts: `domain_activation` → `core/schemas/artifacts/domain_activation.schema.json`, `compliance_report` → `core/schemas/artifacts/compliance_report.schema.json`

## 7. Guardrails
- **Low-confidence detection**: If healthcare domain confidence < 0.5, do not activate; return top-2 candidate domains for PM selection
- **Missing base overlay**: If `base.schema.overlay.json` is missing, refuse activation with error referencing the pack path
- **Regional without base**: Block activation of a regional overlay without its base overlay (invalid state)
- **Sub-pack missing persona**: If a sub-pack requires a persona archetype not in the workspace, emit warning but proceed
- **When to stop and escalate to PM**: If >50% of handoffs have zero compliance coverage, flag for PM risk review before activation
- **When output should be marked low-confidence**: If healthcare intent detection confidence is between 0.5 and 0.85

## 8. Gold Standard Checklist
- [ ] FHIR R4 core resources listed include at minimum: Patient, Coverage, Claim, Encounter, Practitioner, Organization
- [ ] HIPAA compliance checkpoints cover: audit_log, consent_record, breach_notification, data_minimization, encryption_at_rest, encryption_in_transit
- [ ] CMS SLA constraint sets prior authorization to 72 hours (259200 seconds)
- [ ] X12 transaction codes include: 278 (authorization), 837 (claims), 835 (payment)
- [ ] Every orchestration handoff with PHI data gets at least one compliance checkpoint
- [ ] Sub-pack manifests reference only fields that exist in base + regional overlay
- [ ] Prior authorization workflow pattern has provider→payer and payer→provider handoffs

## 9. Examples

### Excellent Output (5/5)
```json
{
  "domain": "healthcare",
  "region": "us",
  "confidence": 0.92,
  "fhir_resource_map": [
    {"workflow_artifact": "prior_auth_request", "fhir_resource": "Claim", "profile": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-claim"},
    {"workflow_artifact": "patient_demographics", "fhir_resource": "Patient", "profile": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"}
  ],
  "compliance_checkpoints": [
    {"handoff": "provider_to_payer", "checkpoints": ["audit_log_at_phi_handoffs", "phi_encryption_in_transit", "consent_record_at_data_access"]}
  ],
  "sla_constraints": [
    {"regulation": "CMS", "handoff_type": "prior_authorization", "sla_hours": 72}
  ],
  "coverage_gaps": []
}
```

### Poor Output (2/5) — What to Avoid
```json
{
  "domain": "healthcare",
  "region": "us",
  "confidence": "high",
  "compliance_checkpoints": [],
  "fhir_resource_map": [],
  "coverage_gaps": []
}
```

**Why this fails:** Missing FHIR resource mappings (empty array), no compliance checkpoints injected, confidence is string instead of numeric, and empty coverage gaps suggest incomplete validation rather than true full coverage.

## 10. Cross-References
- **Upstream skills**: `domain_intelligence` (auto-activation), `architecture_synthesis` (workflow input)
- **Downstream skills**: `ai_architecture_planning` (regulatory alignment), `predictive_analytics_planning` (privacy classification)
- **Related artifact schemas**: `core/schemas/artifacts/domain_activation.schema.json`, `core/schemas/artifacts/compliance_report.schema.json`, `core/schemas/artifacts/workflow_orchestration_map.schema.json`
- **Related entity schemas**: `core/schemas/entities/artifact.schema.json`
- **Domain pack**: `core/domains/healthcare/README.md`, `core/domains/healthcare/base.schema.overlay.json`, `core/domains/healthcare/regions/us.schema.overlay.json`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Keyword-based domain detection | Intent text with healthcare keywords | Domain match with confidence score |
| 1→10 | FHIR resource mapping from overlays | Domain pack base + regional overlays | Resource map + compliance checkpoints |
| 10→100 | Full compliance gate injection into orchestration | Architecture with workflow handoffs | Complete compliance coverage with gap detection |
| 100→10K+ | Multi-region healthcare with conflict resolution | Multiple regional overlays active | Cross-region compliance with conflict detection |

## 12. Validation Criteria
- **Schema conformance**: validates against `core/schemas/artifacts/domain_activation.schema.json`
- **Test file**: `tests/test_v14_healthcare_domain_pack.py` (6 tests + integration)
- **Example fixture**: `core/domains/healthcare/base.schema.overlay.json` validates as overlay
- **Skill consistency test**: included in `tests/test_skill_consistency.py` with all 12 elements present
