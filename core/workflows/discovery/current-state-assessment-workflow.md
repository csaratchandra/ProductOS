# Current-State Assessment Workflow

Purpose: Create a decision-ready view of current product state before starting discovery, prioritization, or delivery replanning.

## 1. Outcome

Produce a `current_state_assessment` artifact that captures current objectives, delivery health, open risks, open blockers, recent customer feedback, decisions needed, and recommended next steps.

## 2. Inputs

Required inputs:

- workspace manifest
- current product artifacts that reflect active work

Optional inputs:

- issue log
- status mail or weekly update
- decision log
- customer pulse
- program increment state
- release readiness packet
- inbound `handoff_contract`

## 3. Primary agents

- `orchestrator`
- `librarian`
- `analyst`
- `validation`

## 4. Workflow steps

### Step 1. Gather current product state

Collect the latest product, delivery, and customer-facing artifacts that reflect current work.

### Step 2. Summarize objectives and delivery health

Identify the active objectives, current delivery health, major risks, blockers, and unresolved decisions.

### Step 3. Summarize customer and stakeholder pressure

Extract any recent customer or stakeholder feedback that materially affects priorities or execution.

### Step 4. Recommend next steps

Convert the current-state view into a short list of recommended next actions and explicit PM decisions.

### Step 5. Validate

The validation agent checks:

- product summary is clear
- at least one decision needed is explicit
- recommended next steps are actionable
- confidence reflects evidence quality

## 5. Failure rules

If current product state is too stale or incomplete to support a defensible assessment, keep the workflow in `review_needed` or `blocked`.

## 6. Outputs

- `current_state_assessment`
- optional `handoff_contract`
- optional `workflow_state`
