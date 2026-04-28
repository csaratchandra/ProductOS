# PRD Agent Contract

## Purpose

Produce and revise structured PRDs from validated upstream inputs without dropping evidence, scope boundaries, or delivery-critical context.

## Core responsibilities

- create or update `prd`
- translate validated problem framing into product requirements and scope
- preserve prioritization, artifact traceability, and canonical persona-archetype truth
- preserve segment, persona, and upstream artifact traceability
- identify unresolved questions that block delivery-ready framing

## Inputs

- `problem_brief`
- optional `research_brief`
- optional `prototype_record`
- linked entities and upstream artifacts
- canonical `persona_archetype_pack`

## Outputs

- `prd`
- scope notes
- unresolved questions
- handoff recommendation to story and acceptance workflows

## Required schemas

- `prd.schema.json`
- `problem_brief.schema.json`
- `concept_brief.schema.json`
- `research_brief.schema.json`
- `prototype_record.schema.json`

## Escalation rules

- escalate when the problem is not validated strongly enough for PRD commitment
- escalate when prototype or research evidence conflicts with the requested scope
- escalate when requirements are requested without a clear problem, outcome, or target user context

## Validation expectations

- PRD scope must be traceable to upstream evidence
- unresolved questions must be explicit
- no hidden expansion of customer-facing scope
- scope boundaries, out-of-scope items, and handoff risks should all stay explicit
