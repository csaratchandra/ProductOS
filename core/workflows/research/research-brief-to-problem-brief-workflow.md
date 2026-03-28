# Research Brief To Problem Brief Workflow

Purpose: Convert structured research findings into a decision-ready `problem_brief` when evidence is strong enough to frame the problem clearly.

## Inputs

- `research_brief`
- optional `idea_record`
- optional `concept_brief`
- linked entities

## Outputs

- `problem_brief`
- `artifact_trace_map`

## Rules

- preserve target segment and target persona from the research input
- carry forward only insights relevant to the problem framing
- if evidence is still weak or contradictory, recommend more research or a prototype instead of forcing a problem brief
- when the recommendation is `advance_to_problem_brief`, record the `research_brief` as an upstream artifact
