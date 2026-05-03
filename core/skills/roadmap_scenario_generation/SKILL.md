# Roadmap Scenario Generation

## 1. Purpose

Generate multiple roadmap scenarios (optimistic, expected, pessimistic) from prioritization data and capacity constraints, surfacing dependency critical paths, OKR alignment, and stakeholder-specific views.

## 2. Trigger / When To Use

Quarterly planning cycle begins. Major scope change or reprioritization needed. PM requests scenario comparison before stakeholder review.

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

1. Ingest feature backlog: Load prioritized features with story points, dependencies, and owner teams.
2. Model team capacity: Gather team velocity, headcount, allocation %. Calculate total capacity for planning horizon.
3. Sequence features: Order features by priority within dependency constraints. Identify critical path.
4. Build scenario timelines: Optimistic (all features ship, velocity holds). Expected (realistic velocity, 10% buffer). Pessimistic (velocity drop, scope cuts).
5. Assign milestone confidence: Per milestone, assess confidence (high/moderate/low) based on dependencies, unknowns, and team history.
6. Align with OKRs: Map features to company objectives, product key results, and measurable feature metrics.
7. Generate stakeholder views: Executive (milestones + OKRs), Engineering (sprint detail + dependencies), Customer (what's coming, when).

## 6. Output Specification

Primary output artifact: specified in schema reference below.

## 7. Guardrails

- Over-optimistic velocity: Expected scenario uses velocity higher than team's 6-sprint average → flag. Use trailing average.
- Ignored dependencies: Feature sequenced without its dependency → block. Dependency graph must be satisfied before sequencing.
- When to escalate: Pessimistic scenario misses critical OKR target — product commitment at risk. Critical path >60% of planning horizon — too many serial dependencies.

## 8. Gold Standard Checklist

- [ ] All 3 scenarios have explicit milestone dates, not just descriptions
- [ ] Critical path is identified and every milestone on it is flagged
- [ ] OKR alignment: every milestone links to at least one key result
- [ ] Stakeholder views are generated from source data — not manually composed
- [ ] Framework alignment: validates against Roadmap planning (Cagan, Inspired), scenario planning (Shell), critical path method
- [ ] Every recommendation includes explicit evidence basis
- [ ] PM has clear next action with owner and timeline

## 9. Examples

See example artifacts in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: trade_off_analysis, capacity_vs_scope_modeling, feature_prioritization_brief
- **Downstream skills**: decision_packet_synthesis, investor_content_generation, status_mail
- **Schemas**: roadmap_scenario.schema.json, capacity_model.schema.json

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
