# Follow-up Automation Workflow

Purpose: Detect, track, and escalate open follow-up items from meetings, reviews, and decisions automatically.

## 1. Outcome

Produce and maintain a `followup_tracker` artifact that keeps all open follow-up items visible, assigns owners, tracks deadlines, and escalates overdue items.

## 2. Inputs

Required inputs:

- meeting records with action items
- decision logs with downstream actions

Optional inputs:

- review gate outputs with flagged items
- stakeholder meeting notes with commitments
- existing follow-up tracker for merge
- existing `workflow_state` if resuming
- inbound `handoff_contract` carrying follow-up work from another workflow

## 3. Primary agents

- `orchestrator`
- `librarian`
- `chore-automation`
- `validation`

## 4. Runtime control

Maintain a `workflow_state` artifact for extraction, merge, validation, and PM review.

Minimum expectations:

- follow-up ingestion and merge steps are recorded explicitly
- unresolved owners or dates raise targeted PM questions
- overdue or blocked items can trigger downstream `handoff_contract` outputs
- workflow completion is explicit once tracker output is attached

## 5. Workflow steps

### Step 1. Extract follow-up items

The chore automation agent extracts follow-up items from:

- action items in meeting records
- decisions that require downstream action
- review gate flagged items
- stakeholder commitments

Each item gets: description, owner, due date, source type, and source ID.

### Step 2. Merge with existing tracker

If a follow-up tracker already exists, merge new items and update status of existing items:

- items already completed: mark as completed
- items past due date: mark as overdue
- new items: add with status open

### Step 3. Compute overdue count

Count all items with status overdue and set the overdue_count field.

### Step 4. Validate

The validation agent checks:

- every item has an owner
- every item has a due date
- overdue items have escalation flags set

### Step 5. PM review

The PM reviews escalated items and may reassign, extend deadlines, or close items.

## 6. Trigger conditions

- new meeting record arrival
- new decision log update
- scheduled daily follow-up check
- PM request for follow-up summary

## 7. Failure rules

Do not suppress overdue items. Always surface them with escalation flags if past due date.

If owner or due-date gaps prevent safe tracking, keep the workflow in `review_needed` or `blocked`.

## 8. Outputs

- `followup_tracker`
- `workflow_state`
- optional `handoff_contract` for escalated overdue items
- overdue escalation alerts
