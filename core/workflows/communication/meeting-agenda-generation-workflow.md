# Meeting Agenda Generation Workflow

Purpose: Generate a meeting agenda from current product state, decisions needed, risks, and unresolved questions so recurring meetings are purposeful.

## Inputs

- status update inputs
- issue log
- decision log
- open questions and escalation items
- optional `workflow_state`
- optional inbound `handoff_contract`

## Outputs

- meeting agenda draft
- prioritized discussion topics
- expected decisions and follow-ups
- updated `workflow_state`
- optional downstream `handoff_contract`

## Runtime control

- maintain visible step state from signal collection through agenda assembly and PM review
- keep blocked or contradictory agenda inputs visible in `workflow_state`
- record missing context as targeted PM questions

## Handoffs

- emit `handoff_contract` when the agenda itself is part of a larger workflow chain, such as a leadership update or release review
- attach the triggering issues, decisions, or status artifacts to that handoff

## Rules

- agenda items should map to decisions, blockers, or unresolved questions
- do not include status topics that are already settled unless a decision is needed
- make expected outcomes of the meeting explicit
- preserve links back to the underlying issues or decisions that triggered agenda inclusion
