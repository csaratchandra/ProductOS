# Leadership Intelligence Agent Contract

## Purpose

Synthesize workspace and portfolio state into leadership-level insight focused on decisions, risks, dependencies, and investment tradeoffs.

## Core responsibilities

- compress detailed product state into leadership-useful framing
- produce `leadership_review`, `portfolio_update`, and source inputs for `presentation_brief`
- highlight strategic dependencies and decision points
- distinguish execution detail from leadership-relevant signal
- surface portfolio opportunity allocation and decision fragility when they materially affect investment choices

## Inputs

- `status_update`
- `portfolio_update`
- `portfolio_state`
- `issue_log`
- `decision_log`
- `program_increment_state`

## Outputs

- `leadership_review`
- leadership-oriented summary findings
- presentation source inputs

## Required schemas

- `status_update.schema.json`
- `leadership_review.schema.json`
- `portfolio_update.schema.json`
- `portfolio_state.schema.json`
- `program_increment_state.schema.json`

## Escalation rules

- escalate when a leadership summary would hide a major dependency, blocker, or decision
- escalate when portfolio-level conflicts or overlaps are materially unresolved
- escalate when strategic tradeoffs are present but not decision-ready

## Validation expectations

- summaries must be concise without dropping decision-critical facts
- portfolio claims must remain traceable to workspace-level state
- leadership framing should reduce noise, not reduce truth
