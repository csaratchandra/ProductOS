# Demo Readout Automation Workflow

Purpose: Generate a structured sprint or demo readout from delivery artifacts without forcing the PM to compile it manually.

## 1. Outcome

Produce a `demo_readout` artifact covering features demoed, acceptance results, key learnings, feedback items, and next-sprint commitments.

## 2. Inputs

Required inputs:

- demo date
- audience list
- increment plan or sprint deliverables

Optional inputs:

- PM annotations on what to highlight
- meeting record from the demo session
- acceptance criteria results
- existing `workflow_state` if resuming
- inbound `handoff_contract` from sprint or acceptance workflows

## 3. Primary agents

- `orchestrator`
- `librarian`
- `chore-automation`
- `validation`

## 4. Runtime control

Maintain a `workflow_state` artifact from source collection through PM review.

Minimum expectations:

- feature coverage gaps are visible in step status and audit history
- feedback requiring action can trigger a downstream `handoff_contract`
- review-needed states remain explicit until PM approval

## 5. Workflow steps

### Step 1. Collect sprint deliverables

The librarian agent gathers:

- features completed or partially completed in the current sprint
- acceptance criteria status per feature
- any deferred items with reasons

### Step 2. Draft readout

The chore automation agent compiles:

- feature list with status and one-line descriptions
- acceptance results where available
- key learnings from the sprint
- next-sprint focus items

### Step 3. Incorporate feedback

If a meeting record from the demo session exists, extract:

- audience feedback items with action-required flags
- questions raised and answers given

### Step 4. Validate

The validation agent checks:

- all committed features are accounted for
- deferred items have explanations
- feedback items with action required have owners

### Step 5. PM review

The PM reviews the readout, adds context, and approves.

## 6. Trigger conditions

- sprint end cadence
- PM request for ad hoc demo readout
- post-demo meeting record arrival

## 7. Failure rules

Do not produce a publish-ready draft if:

- increment plan or deliverables are not available
- more than half of committed features have no status update

The workflow should remain `blocked` or `review_needed` until those defects are resolved.

## 8. Outputs

- `demo_readout`
- `workflow_state`
- optional `handoff_contract` for feedback items that require downstream action
- missing-context request list where needed
