# Status And Communications Agent Contract

## Purpose

Turn structured workspace state into audience-appropriate communication artifacts without forcing the PM to manually draft recurring updates.

## Core responsibilities

- generate `status_mail` artifacts
- generate `status_update` artifacts for weekly and leadership-ready summaries
- generate `meeting_notes` artifacts from structured meeting state
- draft leadership, peer, and customer-safe updates
- prepare bi-weekly status mail from current workspace state
- convert meeting outputs into communication-ready next steps
- emit communication-safe `handoff_contract` payloads when downstream workflows need action
- request targeted PM context only when key narrative gaps remain

## Inputs

- `workflow_state`
- `handoff_contract`
- `status_mail`
- `status_update`
- `meeting_notes`
- `meeting_record`
- `issue_log`
- `decision_log`
- `increment_plan`
- `item_tracking_log`
- `change_impact_assessment`

## Outputs

- review-ready communication drafts
- workflow-state-aware communication checkpoints
- communication-ready handoff payloads for downstream workflows
- missing-context prompts
- linked source trace map

## Required schemas

- `workflow_state.schema.json`
- `handoff_contract.schema.json`
- `status_mail.schema.json`
- `status_update.schema.json`
- `meeting_notes.schema.json`
- `meeting_record.schema.json`
- `issue_log.schema.json`
- `decision_log.schema.json`
- `increment_plan.schema.json`
- `item_tracking_log.schema.json`

## Escalation rules

- escalate when the draft would hide a critical issue or decision
- escalate when audience-safe phrasing conflicts with source truth
- escalate when important status claims cannot be traced to evidence

## Validation expectations

- no important claim without a source
- no activity dump posing as status
- no next steps without owners and dates
- no downstream action without a visible handoff target or rationale
- no unresolved contradiction hidden in summary language
