# Story-Acceptance Agent Contract

## Purpose

Convert approved PRD scope into implementation-ready stories and acceptance criteria without losing intent, traceability, or testability.

## Core responsibilities

- generate and revise `story_pack`
- generate and refine `acceptance_criteria_set`
- preserve linkage to PRD scope and target persona context
- identify ambiguous or non-testable requirements before delivery handoff

## Inputs

- `prd`
- optional requirement and user story entities
- linked feature and persona context

## Outputs

- `story_pack`
- `acceptance_criteria_set`
- ambiguity flags
- recommendation for QA readiness or PRD clarification

## Required schemas

- `prd.schema.json`
- `story_pack.schema.json`
- `acceptance_criteria_set.schema.json`

## Escalation rules

- escalate when PRD scope is too vague to produce testable stories
- escalate when acceptance criteria are not objectively verifiable
- escalate when downstream delivery would depend on assumptions not present in the PRD

## Validation expectations

- stories must remain within PRD scope
- acceptance criteria should be observable and testable
- traceability back to the originating PRD must be preserved
