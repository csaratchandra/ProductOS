# Freshness and Staleness Scan

## 1. Purpose

Scan all workspace artifacts for staleness, compare against per-artifact-type TTL, detect drift conditions, flag artifacts requiring refresh, and generate prioritized refresh recommendations.

## 2. Trigger / When To Use

Scheduled scan (daily/weekly). PM triggers manual scan. Intelligence feed detects drift. Before major release or strategy review.

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

1. Inventory all artifacts: Enumerate every workspace artifact with their generated_at date and artifact_type.
2. Lookup freshness TTL per type: From maturity_band_profile or default TTL map. PESTLE: 90 days. Competitor dossier: 60 days. Market sizing: 180 days. Persona: 120 days. PRD: 90 days.
3. Calculate age: For each artifact, compute age_days = (now - generated_at). Compare against TTL.
4. Classify freshness: Fresh (age < 50% TTL), Approaching stale (50-90% TTL), Stale (90-120% TTL), Critical stale (>120% TTL).
5. Detect drift: Check linked sources for freshness. If sources have changed but artifact hasn't → drift detected. Compare competitive radar state changes against affected artifacts.
6. Generate alerts: Per stale/critical-stale artifact, create freshness alert with: severity, message, affected_artifact_ids, recommended_action.
7. Build refresh recommendations: Per artifact needing refresh: reason, priority, regeneration scope, estimated impact.
8. Update freshness state: Persist artifact_freshness_state with all entries, alerts, and recommendations.

## 6. Output Specification

Primary output: `artifact_freshness_state, maturity_band_profile` artifact

## 7. Guardrails

- All artifacts marked as 'fresh' when several are clearly stale: Detection criteria: artifact age > TTL but freshness_status = fresh → flag. TTL computation error or timestamp corruption.
- Refresh recommendations overwhelm PM: >10 artifacts recommended for refresh at once → aggregate. Group by priority. Surface top 3 only in PM digest.
- When to escalate: Critical-stale count >3 — multiple artifacts severely outdated. Strategy may be built on stale data. Release gate should block until refreshed.

## 8. Gold Standard Checklist

- [ ] Every artifact has a freshness_status based on age vs TTL
- [ ] TTL per artifact type is explicit and justified
- [ ] Drift detection checks source freshness, not just artifact age
- [ ] Refresh recommendations have priority and scope
- [ ] Framework: data freshness governance, observability best practices
- [ ] Framework alignment: Data freshness governance, observability (ProductOS observability-model), artifact lifecycle management
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: competitive_radar_scan, artifact_freshness_state, maturity_band_profile
- **Downstream skills**: drift_and_impact_propagation, strategy_refresh, release_gate_decision
- **Schemas**: artifact_freshness_state.schema.json, maturity_band_profile.schema.json

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
