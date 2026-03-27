# Decision Log Update Workflow

Purpose: Keep formal decision state current by converting meeting outcomes, change events, and PM approvals into structured decision records.

## 1. Outcome

Update the workspace decision log so ProductOS can reliably answer:

- what was decided
- why it was decided
- what evidence supported it
- what changed because of it
- what remains unresolved

## 2. Inputs

- meeting records
- change impact assessments
- PM approvals and overrides
- status mail drafts
- active increment plans

## 3. Primary agents

- `workflow`
- `librarian`
- `status-communications`
- `validation`
- `detail-guardian`

## 4. Workflow steps

### Step 1. Gather candidate decisions

Collect candidate decision statements from:

- transcript-derived decisions
- approved replans
- PM review checkpoints
- scope, sequencing, and publish approvals

### Step 2. Normalize decision quality

Each decision entry should include:

- a clear decision statement
- current status
- evidence or source references
- rationale
- downstream impact

### Step 3. Reconcile duplicates and contradictions

If multiple records describe the same decision:

- merge duplicate entries
- preserve the strongest source references
- flag contradictory decision states for PM review

### Step 4. Update formal decision state

Write the decision into the decision log and link it to:

- affected artifacts
- affected workflows
- affected increments where relevant

### Step 5. Validate

The validation and detail guardian agents check:

- whether the decision is explicit rather than implied
- whether the rationale is traceable
- whether the change impact is linked
- whether unresolved questions are still clearly open

## 5. Trigger conditions

- new meeting record approved
- change impact assessment approved
- PM manual approval or override
- status cadence before publish

## 6. Outputs

- updated decision log entry or entries
- contradiction alerts where applicable
- traceability links for downstream workflows

