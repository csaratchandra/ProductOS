# Market Strategy Definition Workflow

Purpose: Turn discovery outputs into a committed `market_strategy_brief` that makes market role, offering shape, posture, and positioning explicit before downstream concept, prototype, and PRD work.

## Inputs

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
- define the offering shape and positioning statement explicitly
- compare against direct competitors, adjacent tools, internal build, services, and the status quo
- reject posture claims that lack a credible wedge, proof path, or route to distribution
- route to `strategy-option-generation-workflow` when more than one posture remains credible
- do not advance to `problem_brief` if market role, offering, and proof requirements remain materially ambiguous
