# Non-Functional Requirement Extraction

## 1. Purpose

Extract and specify non-functional requirements — performance, security, scalability, reliability, compliance, accessibility, observability — from PRD scope, user stories, and technical constraints, producing structured NFRs for developer handoff.

## 2. Trigger / When To Use

PRD complete. Stories being decomposed for sprint planning. Technical review requested before handoff. Architecture impact assessment triggers NFR needs.

## 3. Prerequisites

- Current feature prioritization data (feature_prioritization_brief, prioritization_decision_record)
- Engineering team structure and velocity data (from capacity_model or PM input)
- OKR or strategic objectives defined for the planning period
- (Recommended) PESTLE analysis and market context
- (Recommended) Previous roadmap scenario for comparison

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `feature_backlog` | `array[object]` | feature_prioritization_brief, prioritization_decision_record | Yes | Prioritized features with story points |
| `team_data` | `array[object]` | PM input or capacity_model | Yes | Team velocity, headcount, allocation |
| `time_horizon_months` | `integer` | PM input | Yes | Planning horizon (3-24 months) |

## 5. Execution Steps

1. Scan PRD scope: Identify NFR implications from: expected user scale, data sensitivity, regulatory requirements, availability expectations, integration patterns.
2. Categorize NFRs: Performance (latency, throughput, resource usage), Security (auth, encryption, audit, data protection), Scalability (horizontal, vertical, limits), Reliability (uptime, recovery, backup), Compliance (GDPR, SOC2, WCAG), Accessibility (WCAG level), Observability (logging, monitoring, alerting).
3. Define per category: Requirement (what must be true), Measurement (how we verify), Priority (must_have, should_have, nice_to_have).
4. Validate against stories: For each story, check if it implicates NFRs. Story requiring user data → privacy NFR. Story with real-time interaction → performance NFR.
5. Flag conflicts: NFR conflicts with story acceptance criteria? Trade-off required.
6. Assemble for handoff pack.

## 6. Output Specification

Primary output artifact: specified in schema reference below.

## 7. Guardrails

- NFRs too generic: "System should be fast" → reject. Require specific metric: "P95 latency < 200ms."
- NFRs without measurement: Requirement stated but verification undefined → flag. Every NFR needs a measurement method.
- When to escalate: NFR requires infrastructure change beyond current team capacity. Compliance NFR (GDPR, SOC2) cannot be met within launch timeline.

## 8. Gold Standard Checklist

- [ ] Every NFR has a specific, measurable requirement (not "should be fast")
- [ ] Categorized across all 7 NFR dimensions
- [ ] Each NFR has a priority (must/should/nice)
- [ ] NFRs are traceable to specific PRD scope or stories
- [ ] Conflicts between NFRs and story ACs are surfaced
- [ ] Framework alignment: validates against ISO 25010 (software quality), WCAG 2.1, GDPR/SOC2 compliance, SRE/SLO methodology (Google)
- [ ] Every recommendation includes explicit evidence basis
- [ ] PM has clear next action with owner and timeline

## 9. Examples

See example artifacts in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: prd_scope_boundary_check, story_decomposition_and_ambiguity_detection, api_contract_generation
- **Downstream skills**: developer_handoff_pack assembly, technical review, architecture assessment
- **Schemas**: developer_handoff_pack.schema.json, prd.schema.json, api_contract.schema.json

## 11. Maturity Band Variations

| Band | Depth Adjustment |
|---|---|
| 0→1 | Exhaustive: multiple scenario modeling with qualitative depth. Capacity model lean — early team is small. |
| 1→10 | Deep: 3-scenario model. Capacity modeling important — team scaling. |
| 10→100 | Standard: 2-scenario model. Capacity modeling data-driven. Resource allocation focus. |
| 100→10K+ | Focused: portfolio-level scenarios. Capacity modeling across multiple teams. |

## 12. Validation Criteria

- **Schema conformance**: validates against associated schemas
- **Test file**: TBD in target sprint
- **Example fixture**: see associated `.example.json` files
