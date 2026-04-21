# Idea To Concept Workflow

Purpose: Convert a raw `idea_record` into a focused `concept_brief` so discovery can decide whether to research, prototype, park, or reject the idea.

## Inputs

- `idea_record`
- optional linked entities such as `problem`, `opportunity`, `metric`, or `decision`
- optional prior discovery notes

## Outputs

- `concept_brief`
- optional `handoff_contract` to research or prototype-validation

## Companion templates

- `../../templates/discovery/idea_record.md`
- `../../templates/discovery/concept_brief.md`
- `../../templates/research/research_notebook.md`
- `../../templates/research/research_brief.md`

## Rules

- preserve target segment and target persona from the idea unless new evidence justifies a change
- sharpen the core hypothesis instead of restating the raw idea summary
- capture why now, why us, and the initial advantage hypothesis instead of leaving strategic value implicit
- preserve `strategy_context_brief`, `product_vision_brief`, and `market_strategy_brief` references in `concept_brief.strategy_artifact_ids` when they exist upstream
- if ambiguity is still high, record explicit open questions in the concept brief
- classify major unknowns and attach an `uncertainty_map` when the next learning step is not obvious
- route to research when the unknown is evidence or market understanding
- route to prototype-validation when the unknown is usability, workflow fit, or trust
- park or reject ideas that do not connect to a meaningful problem, outcome, or operating goal
