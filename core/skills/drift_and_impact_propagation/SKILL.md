# Drift and Impact Propagation

## 1. Purpose

Detect when changed conditions cause artifact content to drift from truth and trace downstream impact propagation through the dependency graph — surfacing which downstream artifacts need regeneration and in what order.

## 2. Trigger / When To Use

Any artifact refreshed or updated. Intelligence alert generated. PM modifies an artifact directly. Freshness scan detects staleness.

## 3. Prerequisites

- Relevant upstream artifacts for the skill domain
- Evidence sources (source note cards, research artifacts, competitive data)
- Defined scope from PM or mission context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `primary_input` | `object` | Upstream artifact schemas | Yes | Core input for the skill |
| `context` | `array[object]` | Supporting artifacts | No | Additional context |

## 5. Execution Steps

1. Detect source change: Identify the triggering change — artifact updated, competitive alert generated, PESTLE factor changed, PM manual edit.
2. Map downstream dependencies: Load the artifact dependency graph. Which artifacts reference the changed artifact? Direct references (in linked_entity_refs, source_artifact_ids) and indirect references (via entity chains).
3. Assess impact per dependent: Per downstream artifact: what specifically would change? Is the change mechanical (just update a ref) or content-deep (the meaning changes)?
4. Classify impact: Minor (reference update only), Moderate (one section affected), Major (core claim or assumption changed), Critical (artifact would be misleading if not updated).
5. Determine regeneration mode: Auto-regenerate (mechanical changes, ref updates), PM review-regenerate (content changes needing judgment), Full artifact regenerate (major impact, rebuild from upstream sources).
6. Build propagation alert: Generate drift_detection_alert with: source change, drifted artifact, severity, affected downstream list with per-artifact impact and refresh priority.
7. Recommend regeneration sequence: Order downstream artifacts by dependency depth. Deepest dependencies first (so intermediate artifacts are fresh when regenerating their dependents).

## 6. Output Specification

Primary output: `drift_detection_alert, artifact_freshness_state` artifact

## 7. Guardrails

- Circular dependency detected: Artifact A depends on B, B depends on A → flag. Cannot auto-resolve. Manual PM intervention needed to break the cycle.
- Propagation depth too deep: A single change triggers >10 downstream regeneration recommendations → verify. Is the dependency graph correct? Some dependencies may be over-linked.
- When to escalate: Critical impact on release-driving artifact (PRD, release readiness). Regeneration would contradict a recent PM decision. Multiple artifacts need PM review — coordinate before regenerating.

## 8. Gold Standard Checklist

- [ ] Downstream dependencies are correctly traced from the dependency graph
- [ ] Impact classification is specific per artifact (not "all downstream affected")
- [ ] Regeneration mode is appropriate per artifact
- [ ] Sequence respects dependency ordering
- [ ] Framework: impact analysis, change propagation, artifact traceability
- [ ] Framework alignment: Impact analysis, change propagation, artifact traceability (ProductOS artifact-trace-map)
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: freshness_and_staleness_scan, competitive_radar_scan, competitive_shift_analysis
- **Downstream skills**: strategy_refresh, decision_analysis, release_readiness
- **Schemas**: drift_detection_alert.schema.json, artifact_freshness_state.schema.json

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full depth with qualitative exploration |
| 1→10 | Deep: comprehensive coverage |
| 10→100 | Standard: focused on highest-impact outputs |
| 100→10K+ | Focused: data-driven, portfolio-level |

## 12. Validation Criteria

- **Schema conformance**: validates against associated artifact schemas
- **Test file**: TBD in validation sprint
- **Example fixture**: associated `.example.json` files
