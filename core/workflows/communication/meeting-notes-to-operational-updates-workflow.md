# Meeting Notes To Operational Updates Workflow

Purpose: Convert meeting notes into downstream operational updates so decisions and follow-through are reflected in ProductOS state quickly.

## Inputs

- `meeting_notes`
- optional `meeting_record`
- optional `workflow_state`
- optional inbound `handoff_contract`
- current issue, decision, and item tracking state

## Outputs

- refreshed `decision_log`
- refreshed `item_tracking_log`
- updated `workflow_state`
- optional downstream `handoff_contract`
- update recommendations for status, issue, or change artifacts

## Runtime control

- maintain visible step state from note parsing through downstream update recommendation
- raise targeted PM questions when owners, due dates, or decision language are ambiguous
- keep the workflow in `blocked` if approved operating state conflicts with the notes

## Handoffs

- emit `handoff_contract` when meeting-derived changes should route into issue, status, change, or decision workflows
- attach the source meeting artifact references so downstream workflows can trace the update

## Rules

- extract decisions, action items, owners, due dates, issues, and open questions from meeting outputs
- update downstream operational artifacts rather than leaving decisions trapped in notes
- preserve traceability to the originating meeting source
- escalate when notes conflict with current approved operating state
