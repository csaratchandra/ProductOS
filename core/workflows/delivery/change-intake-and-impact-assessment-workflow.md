# Change Intake And Impact Assessment Workflow

Purpose: Intake notable product or delivery change events and turn them into explicit impact analysis rather than hidden plan drift.

## 1. Outcome

Produce a `change_impact_assessment` that explains:

- what changed
- which artifacts, commitments, or dependencies are affected
- whether the change is noise, local drift, or replan-worthy movement
- what escalation or follow-on workflow should happen next

## 2. Inputs

Required inputs:

- `change_event`
- current increment plan or equivalent active delivery plan
- current issue log

Optional inputs:

- release state or portfolio state
- recent status updates or leadership summaries
- open dependency records
- prior change assessments for the same scope area

## 3. Primary agents

- `orchestrator`
- `librarian`
- `radar`
- `analyst`
- `strategist`
- `validation`

## 4. Workflow steps

### Step 1. Gather the current baseline

The librarian agent retrieves:

- the original `change_event`
- the currently approved plan or commitment state
- linked issues, risks, and dependencies
- any prior assessments that may already cover the same change area

### Step 2. Classify the change

The radar and analyst agents determine:

- whether the change is scope, sequencing, dependency, reliability, or delivery-status movement
- whether the signal is isolated churn or a meaningful change in execution reality
- whether the change is local to one workflow or affects broader commitments

### Step 3. Assess impact explicitly

Generate a `change_impact_assessment` that evaluates:

- customer impact
- delivery risk
- time cost
- affected artifacts and workflow states
- preserved commitments versus threatened commitments

### Step 4. Recommend the next path

The strategist agent recommends whether to:

- absorb the change without replanning
- trigger `replan-recommendation-workflow`
- escalate immediately to PM or leadership review
- refresh status, issue, or portfolio outputs

### Step 5. Validate and log

The validation agent checks:

- that the original change event remains the traceable upstream source
- that material impacts are explicit rather than implied
- that the recommendation matches the assessed impact scope

## 5. Trigger conditions

- new `change_event` with medium or higher impact scope
- repeated low-signal churn that crosses the workspace threshold
- PM request for explicit impact analysis
- contradiction between current plan and live delivery state

## 6. Failure rules

Do not produce a low-confidence assessment if:

- the current canonical plan cannot be identified
- the source change cannot be traced to a real event or artifact
- contradictions across source systems remain unresolved

In these cases, return a controlled assessment with explicit missing-context and conflict notes.

## 7. Outputs

- `change_impact_assessment`
- impact summary
- escalation or replan recommendation
- source traceability notes
