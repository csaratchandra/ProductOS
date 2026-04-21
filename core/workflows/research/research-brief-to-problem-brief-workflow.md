# Research Brief To Problem Brief Workflow

Purpose: Convert structured research findings into a decision-ready `problem_brief` when evidence is strong enough to frame the problem clearly.

## Inputs

- `research_brief`
- optional `idea_record`
- optional `concept_brief`
- optional `strategy_context_brief`
- optional `product_vision_brief`
- optional `market_strategy_brief`
- linked entities

## Outputs

- `problem_brief`
- `artifact_trace_map`

## Rules

- preserve target segment and target persona from the research input
- carry forward only insights relevant to the problem framing
- if evidence is still weak or contradictory, recommend more research or a prototype instead of forcing a problem brief
- when the recommendation is `advance_to_problem_brief`, record the `research_brief` as an upstream artifact
- preserve `strategy_context_brief`, `product_vision_brief`, and `market_strategy_brief` in `problem_brief.upstream_artifact_ids` when they shape the framing or recommendation
