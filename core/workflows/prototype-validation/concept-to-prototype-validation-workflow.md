# Concept To Prototype Validation Workflow

Purpose: Turn a `concept_brief` into a prototype-validation loop that reduces ambiguity before `problem_brief` or PRD commitment.

## Inputs

- `concept_brief`
- optional `research_brief`
- optional `persona_pack`
- optional `competitor_dossier`
- linked entities

## Outputs

- `prototype_record`
- `artifact_trace_map`
- recommendation to advance, iterate, park, or stop

## Rules

- route to prototype when usability, feasibility, trust, or workflow ambiguity is still material
- keep the prototype focused on the uncertainty being tested
- prefer the cheapest learning method identified in the `uncertainty_map` before expanding prototype scope
- preserve target segment and target persona in the prototype record
- record learnings clearly enough that downstream problem framing can reuse them
- do not force a prototype when the uncertainty can be resolved by cheaper research
