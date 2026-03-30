# Item Lifecycle Trace Workflow

## Purpose

Turn one opportunity or feature item into a fully traceable lifecycle record that a PM can inspect by item or by stage.

## Inputs

- `intake_routing_state`
- `research_notebook`
- `competitor_dossier`
- `market_analysis_brief`
- `segment_map`
- `persona_pack`
- `idea_record`
- `problem_brief`
- `concept_brief`
- `prototype_record`
- `ux_design_review`
- `visual_reasoning_state`
- `prd`
- `validation_lane_report`
- `manual_validation_record`
- optional `artifact_trace_map`

## Outputs

- `item_lifecycle_state`
- `lifecycle_stage_snapshot`
- readable discovery review doc

## Workflow

1. Resolve the canonical item id, linked segments, linked personas, and linked entities.
2. Group upstream artifacts by lifecycle stage using the standard stage order.
3. Confirm each stage gate result from validation artifacts or explicit PM approval notes.
4. Emit an `item_lifecycle_state` artifact with:
   - current stage
   - overall status
   - stage-by-stage artifact links
   - pending questions
   - blocked reasons
   - audit log
5. Emit a `lifecycle_stage_snapshot` artifact summarizing:
   - active item count
   - segment count
   - persona count
   - artifact counts
   - gate counts
   - stage-level item lists
6. Produce a readable review document explaining what happened end to end during discovery.

## Acceptance

- Every discovery-stage artifact is linked back to the canonical item.
- Every discovery stage has an explicit gate status.
- Prototype-validation stages should make prototype fidelity, interaction depth, and next improvement actions inspectable.
- High-fidelity prototype-validation stages should include `ux_design_review` before PRD handoff is treated as passed.
- `prd_handoff` cannot be marked passed without a validation lane report and manual validation record.
- Later lifecycle stages must still exist in the item model, even when `not_started`.
