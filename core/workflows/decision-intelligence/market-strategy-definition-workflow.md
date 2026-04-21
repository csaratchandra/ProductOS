# Market Strategy Definition Workflow

Purpose: Turn discovery outputs into a committed `market_strategy_brief` that makes market role, offering shape, posture, and positioning explicit before downstream concept, prototype, and PRD work.

## Inputs

- `strategy_context_brief`
- `product_vision_brief`
- `strategy_option_set`
- `segment_map`
- `persona_archetype_pack` or `persona_pack`
- `competitor_dossier`
- `market_analysis_brief`
- optional `research_brief`, `opportunity_advantage_brief`, or `signal_hypothesis_brief`

## Outputs

- `market_strategy_brief`
- recommendation for `strategy_option_set` generation when multiple credible paths remain

## Rules

- explicitly choose a strategic posture: `leader`, `challenger`, `follower`, or `niche`
- define the market around the job, workflow, or decision context being served rather than a vague category label
- identify the beachhead segment and priority personas before concept work continues
- preserve `strategy_option_set` lineage and record the rejected path, not just the selected posture
- preserve links to `strategy_context_brief` and `product_vision_brief` through existing artifact-reference fields such as `linked_artifact_ids` and `evidence_refs`
- define the offering shape and positioning statement explicitly
- compare against direct competitors, adjacent tools, internal build, services, and the status quo
- define explicit proof requirements, critical assumptions, and proof-plan ownership before `commit_posture`
- reject posture claims that lack a credible wedge, proof path, or route to distribution
- route to `strategy-option-generation-workflow` when more than one posture remains credible
- do not advance if posture and positioning contradict the product vision, north-star metric, or enterprise-goal linkage
- do not advance to `problem_brief` if market role, offering, and proof requirements remain materially ambiguous
- do not allow `commit_posture` when competitor evidence is only draft-quality or when the strategy artifact is below `decision_ready`
