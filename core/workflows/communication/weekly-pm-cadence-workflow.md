# Weekly PM Cadence Workflow

Purpose: Run the weekly PM operating rhythm across execution status, decisions, risks, dependencies, and communications.

## Inputs

- increment plan
- issue log
- meeting notes and meeting record outputs
- decision log
- change events
- optional `workflow_state`
- optional inbound `handoff_contract`

## Outputs

- refreshed `status_update`
- updated issue and decision state
- `next_steps_digest`
- updated `workflow_state`
- downstream `handoff_contract` payloads for escalations and follow-up

## Runtime control

- maintain a visible `workflow_state` artifact across status review, state refresh, communication generation, and PM review
- move the workflow to `review_needed` when PM approval is required for summary framing or escalation language
- move the workflow to `blocked` when issue, decision, or change inputs contradict one another materially

## Handoffs

- emit `handoff_contract` when the weekly cadence creates downstream work for decision, issue, delivery, or leadership communication paths
- include source artifact references and pending questions in each downstream handoff

## Rules

- review status, blockers, owner shifts, and dependency changes weekly
- refresh decision and issue state before generating communication outputs
- surface escalation-needed items rather than hiding them in narrative summaries
- preserve traceability from weekly updates back to the underlying artifacts
