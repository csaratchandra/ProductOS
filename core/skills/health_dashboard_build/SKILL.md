# Health Dashboard Build

## 1. Purpose

Assemble a living product-health surface from freshness, drift, adoption, funnel, and churn signals so PMs can see top risks and next actions in one place.

## 2. Trigger / When To Use

Use when PM needs a single operating view across research freshness, downstream drift, feature usage, funnel movement, or churn risk. Typical triggers:
- Weekly or monthly operating review
- Release-readiness or outcome-review preparation
- Freshness or drift alerts have accumulated and need prioritization
- PM requests a top-actions dashboard from existing analytics artifacts

## 3. Prerequisites

- Current intelligence or analytics artifacts for freshness, drift, adoption, funnel, or churn
- A bounded workspace or mission scope to summarize
- PM-approved definition of which signals are decision-driving for the dashboard view

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `primary_input` | `object` | Runtime, analytics, or strategy artifacts | Yes | The current product-health signal set |
| `context` | `array[object]` | Supporting artifacts and evidence | No | Additional signal context and historical comparisons |

## 5. Execution Steps

1. Gather signal artifacts: Load the current freshness, drift, adoption, funnel, cohort, and churn artifacts relevant to the scoped product surface.
2. Normalize status: Convert each signal into a comparable status band such as healthy, watch, or critical with explicit evidence refs.
3. Rank issues: Prioritize the highest-impact signal changes by business risk, user impact, and immediacy.
4. Synthesize narrative: Explain what changed, why it matters, and which signals reinforce or contradict each other.
5. Build top actions: Convert the ranked issues into concrete PM actions with owner, urgency, and expected outcome.
6. Link dependencies: Show when a dashboard recommendation depends on upstream freshness or drift remediation before downstream execution.
7. Emit the dashboard bundle: Package the signal summary, priority issues, and recommended actions into the living-system output set.

## 6. Output Specification

- `artifact_freshness_state` → `core/schemas/artifacts/artifact_freshness_state.schema.json`
- `drift_detection_alert` → `core/schemas/artifacts/drift_detection_alert.schema.json`
- `cohort_analysis` → `core/schemas/artifacts/cohort_analysis.schema.json`
- `funnel_analysis` → `core/schemas/artifacts/funnel_analysis.schema.json`
- `feature_adoption_report` → `core/schemas/artifacts/feature_adoption_report.schema.json`
- `churn_prediction` → `core/schemas/artifacts/churn_prediction.schema.json`

## 7. Guardrails

- Do not claim a single “health score” if the underlying artifacts disagree; surface the contradiction explicitly.
- Do not recommend downstream actions when the blocking issue is stale or drifted upstream evidence; route refresh first.
- Escalate to PM when churn, adoption, and funnel signals conflict materially or when evidence freshness makes the dashboard misleading.

## 8. Gold Standard Checklist

- [ ] Every surfaced issue is tied to a concrete source artifact
- [ ] Top actions are specific enough to execute without reinterpretation
- [ ] Contradictory signals are called out instead of averaged away
- [ ] Freshness and drift blockers are visible before downstream recommendations
- [ ] Framework alignment: product observability, reliability review, and explicit action prioritization

## 9. Examples

See `artifact_freshness_state.example.json`, `drift_detection_alert.example.json`, `cohort_analysis.example.json`, `funnel_analysis.example.json`, `feature_adoption_report.example.json`, and `churn_prediction.example.json` in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: `freshness_and_staleness_scan`, `drift_and_impact_propagation`, `competitive_shift_analysis`
- **Downstream skills**: `stakeholder_management`, `strategy_refresh`, `release_claim_traceability`
- **Schemas**: `artifact_freshness_state.schema.json`, `drift_detection_alert.schema.json`, `cohort_analysis.schema.json`, `funnel_analysis.schema.json`, `feature_adoption_report.schema.json`, `churn_prediction.schema.json`

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: include all major signals with narrative interpretation and manual-action routing |
| 1→10 | Deep: combine signal trends with prioritized PM actions and visible dependencies |
| 10→100 | Standard: emphasize movement, risk ranking, and exception management |
| 100→10K+ | Focused: portfolio-level dashboard with only critical signal deltas and top interventions |

## 12. Validation Criteria

- **Schema conformance**: dashboard outputs validate against associated artifact schemas
- **Test file**: `tests/test_v10_health_dashboard_build.py`
- **Example fixture**: `artifact_freshness_state.example.json`, `drift_detection_alert.example.json`, `cohort_analysis.example.json`, `funnel_analysis.example.json`, `feature_adoption_report.example.json`, `churn_prediction.example.json`
