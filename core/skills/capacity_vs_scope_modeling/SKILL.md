# Capacity vs Scope Modeling

## 1. Purpose

Model team capacity against roadmap scope to surface realistic delivery timelines, capacity gaps, and trade-off scenarios — helping PMs make data-driven scope decisions.

## 2. Trigger / When To Use

Roadmap scenario generated. Team capacity changes (hiring, departure). Scope creep exceeds threshold. Before committing to stakeholder timelines.

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

1. Model team capacity: Per team: headcount, velocity (trailing 6-sprint average), allocation %, available sprints. Total capacity = team velocity × available sprints × allocation.
2. Calculate scope demand: Total story points. Breakdown by priority (must_now, next, later) and by team assignment.
3. Compute gap: Capacity - demand. If negative (over capacity): identify what must be cut or delayed. If positive (under capacity): identify what could be accelerated.
4. Assess must_now risk: Can all must-now features be delivered? If not, this is a critical escalation.
5. Generate trade-off scenarios: What if we swap feature A for feature B? What if we add 2 sprints? What if we borrow 1 engineer?
6. Recommend: Cut, delay, add capacity, or accept risk. With specific features named.

## 6. Output Specification

Primary output artifact: specified in schema reference below.

## 7. Guardrails

- Trailing velocity not representative: Team had 2 atypical sprints (holiday, outage) → use 4-sprint trimmed mean.
- Must-now gap >0: Cannot deliver committed scope → escalation. Do not proceed with plan that cannot deliver commitments.
- When to escalate: All trade-off scenarios fail to close the gap. Must-now demand exceeds capacity by >20%.

## 8. Gold Standard Checklist

- [ ] Velocity source is explicit (trailing N sprints, trimmed mean)
- [ ] Must-now gap is separately calculated — if >0, flagged
- [ ] Trade-off scenarios name specific features, not generic "cut 20%"
- [ ] Capacity model accounts for team allocation (not 100% — meetings, reviews, on-call)
- [ ] Framework alignment: validates against Capacity planning, agile velocity modeling, resource allocation
- [ ] Every recommendation includes explicit evidence basis
- [ ] PM has clear next action with owner and timeline

## 9. Examples

See example artifacts in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: roadmap_scenario_generation, story_decomposition_and_ambiguity_detection, agentic_delivery_burden_estimation
- **Downstream skills**: decision_packet_synthesis, roadmap_scenario_generation, status_mail
- **Schemas**: capacity_model.schema.json, roadmap_scenario.schema.json

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
