# Core Skills

Purpose: Define reusable capability building blocks that ProductOS personas, agents, and workflows can compose instead of re-describing the same behavior in many places.

## Why This Exists

ProductOS already has a broad contract catalog in `core/agents/`.

That catalog is useful for authority boundaries and review posture.

It is not sufficient as the main source of task quality.

The shared skill layer exists so important capabilities are:

- defined once
- reviewed once
- improved once
- reused by many personas and workflows

## Structure

Each skill lives at:

- `core/skills/<skill_name>/SKILL.md`

Each skill document should use this section order:

1. `Purpose`
2. `Trigger / When To Use`
3. `Inputs`
4. `Outputs`
5. `Guardrails`
6. `Execution Pattern`
7. `Validation Expectations`

## Initial Skill Set

- `source_discovery`
- `source_normalization`
- `source_ranking`
- `freshness_scoring`
- `contradiction_detection`
- `evidence_extraction`
- `retrieval_selection`
- `strategy_refresh`
- `decision_packet_synthesis`
- `publish_safe_summarization`
- `competitive_entity_resolution`
- `competitive_capability_decomposition`
- `market_definition_precision`
- `strategy_option_architecture`
- `wedge_design`
- `right_to_win_assessment`
- `proof_path_design`
- `buyer_motion_and_packaging`
- `claim_audit_and_confidence_scoring`
- `artifact_quality_grading`
- `segment_enrichment`
- `persona_evidence_synthesis`
- `problem_severity_quantification`
- `concept_risk_surfacing`
- `prd_scope_boundary_check`
- `story_decomposition_and_ambiguity_detection`
- `story_testability_expansion`
- `agentic_delivery_burden_estimation`
- `market_framework_synthesis`
- `market_sizing_reasoning_check`
- `displacement_barrier_assessment`
- `quantitative_competitive_comparison`
- `signal_priority_scoring`
- `segment_priority_scoring`
- `persona_priority_scoring`
- `problem_priority_scoring`
- `concept_priority_scoring`
- `release_claim_traceability`
- `customer_signal_clustering`
- `launch_priority_reasoning`
- `outcome_signal_evaluation`
- `outcome_to_backlog_prioritization`
- `visual_message_hierarchy`
- `visual_pattern_selection`
- `visual_composition_planning`
- `visual_publish_safety`
- `dual_target_fidelity`
- `visual_regression_review`
- `workflow_corridor_design`

## Rules

- skills should be capability-oriented, not persona-oriented
- skills should stay reusable across multiple workflows where practical
- skills should preserve evidence, review, and claim-boundary discipline
- if a behavior is only implied by a persona contract and is reused elsewhere, promote it into a skill
