# Standard Workflow Contract

Purpose: Give every ProductOS workflow the same runtime shape so orchestration, visibility, testing, and recovery all work consistently.

## Required runtime artifact

Every executable workflow should maintain a `workflow_state` artifact.

## Required fields

- workflow identity
- workspace identity
- workflow type
- overall status
- current step
- ordered step list
- input artifact references
- output artifact references
- pending PM questions
- audit log

## Required behavior

Every workflow should:

- start in a visible state
- record step transitions explicitly
- attach source and output artifacts
- surface missing context as targeted questions
- move to `review_needed` when PM approval is required
- move to `blocked` when it cannot continue safely
- record completion explicitly

## Standard statuses

- `not_started`
- `collecting_inputs`
- `in_progress`
- `review_needed`
- `blocked`
- `completed`
- `cancelled`

## Standard step status values

- `pending`
- `active`
- `completed`
- `blocked`
- `skipped`

## Minimum audit events

- created
- step transition
- artifact attached
- question raised
- blocked
- completed

