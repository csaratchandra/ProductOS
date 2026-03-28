# Weekly Update Automation Workflow

Purpose: Generate a structured weekly team update from workspace state without requiring the PM to draft it manually.

## 1. Outcome

Produce a `weekly_update` artifact covering highlights, blockers, upcoming milestones, team health, follow-up digest, and next-week focus.

## 2. Inputs

Required inputs:

- week ending date
- audience list
- current increment plan or active delivery state
- issue log
- decision log

Optional inputs:

- PM notes on emphasis or nuance
- meeting records from the week
- follow-up tracker state
- existing `workflow_state` if resuming
- inbound `handoff_contract` from delivery, issue, or decision workflows

## 3. Primary agents

- `orchestrator`
- `librarian`
- `chore-automation`
- `status-communications`
- `validation`

## 4. Runtime control

Maintain a `workflow_state` artifact across the weekly run.

Minimum expectations:

- current step and status stay visible to the PM
- missing nuance is raised as targeted questions, not hidden in summary language
- blocked inputs move the workflow to `blocked`
- approved publication moves the workflow to `completed`

Emit a `handoff_contract` when blockers, decisions, or follow-up items need action in another workflow.

## 5. Workflow steps

### Step 1. Collect weekly state

The librarian agent gathers:

- delivery progress from the increment plan
- issues opened, resolved, or escalated during the week
- decisions made or pending
- follow-up items due or overdue
- meeting outcomes from any records during the week

### Step 2. Draft highlights and blockers

The chore automation agent compiles:

- top three to five highlights from delivery progress and resolved issues
- active blockers with severity and owner
- upcoming milestones with on-track, at-risk, or delayed status

### Step 3. Compile follow-up digest

Extract open and overdue follow-ups from the follow-up tracker and summarize for the audience.

### Step 4. Validate

The validation agent checks:

- highlights have traceable source artifacts
- blockers have owners
- no important open issues are omitted
- team health assessment is consistent with blocker severity

### Step 5. PM review

The PM reviews the draft and may add, remove, or reframe items before approval.

### Step 6. Publish

On approval, mark the weekly update as approved and link to source artifacts.

Also attach the output to `workflow_state` and generate downstream handoffs where needed.

## 6. Trigger conditions

- scheduled weekly cadence
- PM request for ad hoc team update

## 7. Failure rules

Do not produce a publish-ready draft if:

- delivery state has not been updated in the last seven days
- issue log has unresolved contradictory status
- next-week focus items are missing

The workflow should remain `blocked` or `review_needed` until those conditions are resolved.

## 8. Outputs

- `weekly_update`
- `workflow_state`
- optional `handoff_contract` for follow-up or escalation paths
- missing-context request list where needed
