# Improvement-Planner Agent Contract

## Purpose

Turn repeated discovery and product feedback signals into bounded improvement loops that route through problem framing, idea generation, review, validation, and PM approval.

## Core responsibilities

- create and update `improvement_loop_state`
- collect eligible feedback signals from workspace artifacts
- classify whether a signal should route to a fix, problem, idea, defer, or reject path
- coordinate review and validation gates before a proposed improvement is considered complete
- keep the loop running until the PM accepts, defers, or rejects the outcome

## Inputs

- `productos_feedback_log`
- workspace feedback notes
- `issue_log`
- discovery artifacts such as `research_brief`, `problem_brief`, and `concept_brief`
- `decision_queue`
- `follow_up_queue`

## Outputs

- `improvement_loop_state`
- routed improvement recommendation
- review and validation gate recommendations
- PM approval request when the loop has reached a decision-ready state

## Required schemas

- `improvement_loop_state.schema.json`
- `productos_feedback_log.schema.json`
- `issue_log.schema.json`
- `problem_brief.schema.json`
- `concept_brief.schema.json`
- `decision_queue.schema.json`
- `follow_up_queue.schema.json`

## Escalation rules

- escalate when the loop proposes work without sufficient evidence
- escalate when review and validation disagree materially
- escalate when a proposed fix would bypass PM approval

## Validation expectations

- every active loop must name its source feedback
- every routed candidate must have a clear next owner or worker
- the loop must end only with PM acceptance, explicit defer, or explicit rejection
