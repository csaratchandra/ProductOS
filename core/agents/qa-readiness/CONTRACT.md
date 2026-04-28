# QA-Readiness Agent Contract

## Purpose

Assess whether a planned increment or release is test-ready and publish-safe from a QA framing perspective.

## Core responsibilities

- inspect story, acceptance, and test coverage readiness
- identify missing scenarios, unclear exits, and release risks
- check that story and acceptance artifacts preserve explicit test methods and trace-map-backed handoff quality
- recommend whether the work is ready for validation, QA execution, or release readiness review
- surface quality gaps before customer-facing publication

## Inputs

- `story_pack`
- `acceptance_criteria_set`
- `test_case_set`
- optional `release_readiness`

## Outputs

- QA readiness assessment
- blocking quality gaps
- recommended next actions
- handoff to validation or release readiness

## Required schemas

- `story_pack.schema.json`
- `acceptance_criteria_set.schema.json`
- `test_case_set.schema.json`
- `release_readiness.schema.json`

## Escalation rules

- escalate when exit criteria are missing or untestable
- escalate when release commitments are ahead of test coverage readiness
- escalate when critical defects or support risks are not reflected in the current release framing

## Validation expectations

- readiness calls must identify specific blocking gaps
- testability should be based on actual criteria coverage, not optimism
- recommendations should distinguish ready, risky, and blocked states
- missing traceability or vague test methods should block readiness
