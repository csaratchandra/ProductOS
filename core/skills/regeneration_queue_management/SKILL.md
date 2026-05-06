# Regeneration Queue Management Skill

## 1. Purpose
Orchestrate artifact regeneration after source changes, ensuring mechanical updates auto-execute while content-deep changes queue for PM review.

## 2. Trigger / When To Use
- `drift_detection_alert` from `drift_and_impact_propagation`
- Competitive alert from `competitive_radar_scan`
- PM note added to inbox
- Research feed refresh
- Stakeholder feedback received

## 3. Prerequisites
- `impact_propagation_map.json` exists in workspace
- Source artifact that triggered the change is available
- Target artifacts are loadable and valid

## 4. Input Specification
- `trigger_event`: {event_type, source_artifact_ref, change_summary}
- `workspace_dir`: Path to the workspace
- `impact_propagation_map`: Dependency graph of artifacts

## 5. Execution Steps
1. Load trigger event and validate required fields
2. Load impact propagation map from workspace
3. Identify all downstream artifacts affected by source change
4. For each downstream artifact:
   a. Classify impact: mechanical / content_deep / structural
   b. Generate delta preview describing what would change
   c. Determine regeneration mode: auto / pm_review / full_rebuild
5. Order queue by dependency depth (deepest first)
6. Check for circular dependencies; block if found
7. Emit `regeneration_queue.json` artifact
8. Update `document_sync_state` for affected documents
9. Update cockpit with queue recommendations

## 6. Output Specification
- `regeneration_queue.json`: Queue with items, status, counts
- Updated `document_sync_state` with modification log entries
- Cockpit `living_updates_queue` panel entries

## 7. Guardrails
- Circular dependency detected → block queue, escalate to PM
- >10 queued items → split into batches with summary
- Critical artifact (PRD, release_readiness) → always pm_review mode
- Content-deep item without delta preview → reject, require refinement
- Missing target artifact → skip with warning, log in cockpit

## 8. Gold Standard Checklist
Every queued item has a clear delta preview that a PM can understand in <30 seconds. Mechanical items auto-execute silently. Content-deep items always require explicit PM approval. No artifact updates occur without corresponding queue entries.

## 9. Examples
- Excellent: Competitor pricing change → 3 mechanical updates (date stamps, references) auto-executed, 2 content-deep updates (strategy claims, battle card) queued with clear delta previews
- Poor: Competitor change triggers 15 items with no delta previews, no classification, PM must review everything manually

## 10. Cross-References
- Upstream: `drift_and_impact_propagation`, `competitive_radar_scan`
- Downstream: `living_document_rendering`, `export_pipeline`
- Related: `document_sync_state`, `cockpit_state`

## 11. Maturity Band Variations
- 0→1: All items queue for PM review (conservative)
- 1→10: Mechanical items auto-execute, content-deep queue for review
- 10→100: Full classification with learning from PM rejections

## 12. Validation Criteria
- `tests/test_v10_regeneration_queue.py`
- Queue schema validates against `regeneration_queue.schema.json`
- All items have required fields
- No circular dependencies in queue
