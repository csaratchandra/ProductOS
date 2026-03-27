# Discovery Review: PM Lifecycle Traceability

## Canonical Item

- Item id: `opp_pm_lifecycle_traceability`
- Title: `Lifecycle traceability and stage visibility for PM work`
- Current stage: `prd_handoff`
- Overall status: `ready_for_handoff`

## What Happened In Discovery

The V5 discovery pass started from a basics-first problem statement: PMs cannot reliably inspect one opportunity end to end across discovery without reopening scattered artifacts and rebuilding the story manually. The research bundle compared PM lifecycle tools and broader execution systems to check whether this gap is already solved well enough elsewhere.

The mixed competitor set showed a consistent pattern. PM lifecycle tools are strong at prioritization, roadmaps, and connected discovery surfaces. Execution systems are strong at status, collaboration, and downstream tracking. But neither category clearly leads with a durable, audit-ready item narrative that explains which segments and personas were targeted, which discovery artifacts were created, which gates passed, and what is ready next.

## Discovery Outputs

- Research grounding: `research_notebook_pm_lifecycle_visibility`, `competitor_dossier_pm_lifecycle_visibility`, `market_analysis_brief_pm_lifecycle_visibility`
- Customer framing: `segment_map_pm_lifecycle_visibility`, `persona_pack_pm_lifecycle_visibility`
- Problem and concept: `problem_brief_pm_lifecycle_visibility`, `idea_record_pm_lifecycle_visibility`, `concept_brief_pm_lifecycle_visibility`
- Validation: `prototype_record_pm_item_timeline`, `ux_design_review_pm_lifecycle_visibility`, `visual_reasoning_state_pm_lifecycle_visibility`
- Handoff: `prd_pm_lifecycle_visibility`, `validation_lane_report_pm_lifecycle_visibility`, `manual_validation_record_pm_lifecycle_visibility`
- Traceability controls: `item_lifecycle_state_pm_lifecycle_visibility`, `lifecycle_stage_snapshot_discovery`, and trace maps for the problem brief, concept brief, prototype record, and PRD

## Gates Passed

- `signal_intake`
- `research_synthesis`
- `segmentation_and_personas`
- `problem_framing`
- `concept_shaping`
- `prototype_validation`
- `prd_handoff`

## Decision

Discovery passed. The correct V5.0 scope is to ship lifecycle traceability through `prd_handoff`, keep later lifecycle stages explicit but `not_started`, and use the starter workspace as the reusable adoption surface for the same model.
