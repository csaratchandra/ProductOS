# Bi-Weekly Status Mail Automation Workflow

Purpose: Generate a review-ready bi-weekly status mail that keeps stakeholders aligned without requiring the PM to draft it from scratch.

## 1. Outcome

Produce a `status_mail` artifact that explains:

- what happened during the reporting period
- material changes
- open issues and risks
- decisions made or needed
- next steps for the next reporting window

## 2. Inputs

Required inputs:

- reporting period boundaries
- relevant workspace artifacts and decisions
- current issue log
- recent meeting records
- increment plan or active delivery plan

Optional inputs:

- PM notes on nuance not visible in source systems
- stakeholder-specific emphasis requests
- launch or customer communication constraints
- existing `workflow_state` if this run is resuming
- inbound `handoff_contract` from a meeting, decision, or change workflow

## 3. Primary agents

- `orchestrator`
- `librarian`
- `status-communications`
- `radar`
- `workflow`
- `validation`

## 4. Runtime control

Maintain a `workflow_state` artifact for the full run.

Minimum expectations:

- status transitions should follow the standard workflow contract
- the active step should be visible at all times
- targeted PM questions should be recorded in `pending_questions`
- blocked publication should move the workflow to `blocked` rather than silently drafting around gaps

Emit a `handoff_contract` when this workflow hands material issues, decisions, or follow-up actions into another workflow.

## 5. Workflow steps

### Step 1. Collect source state

The librarian agent gathers:

- change events during the reporting period
- decisions logged during the reporting period
- issue log entries still open or recently resolved
- meeting records and transcript-derived actions
- increment progress and dependency status

### Step 2. Detect narrative gaps

The status and communications agent checks whether source state explains:

- why major changes happened
- what tradeoffs were made
- what leadership should care about
- what is genuinely next

If not, the system should request targeted PM context rather than asking for a full rewrite.

Example prompts:

- What is the one most important thing leadership should understand from this period?
- Which issue deserves attention but should not be escalated yet?
- Did anything happen that systems recorded inaccurately or without enough nuance?

### Step 3. Build the draft

Generate a `status_mail` artifact using the schema and template.

The draft should:

- emphasize changes and decisions over activity noise
- separate facts from interpretation
- call out blocked or at-risk work clearly
- tailor tone to the selected audience

### Step 4. Validate

The validation agent checks:

- source traceability for each major claim
- whether low-signal items were inappropriately included
- whether important risks or decisions were omitted
- whether next steps have owners and dates

### Step 5. PM review

The PM reviews:

- subject line
- summary framing
- escalations and risk wording
- next-step clarity

### Step 6. Publish and log

On approval:

- mark the `status_mail` artifact approved
- link it to contributing artifacts
- log any PM-added context for future learning
- attach the published artifact to `workflow_state`
- emit follow-on `handoff_contract` payloads if the mail creates new work for decision, issue, or delivery paths

## 6. Trigger conditions

- scheduled bi-weekly cadence
- material change that requires an out-of-cycle update
- PM request for an ad hoc status draft

## 7. Failure rules

Do not produce a publish-ready draft if:

- there is insufficient traceable source state for major claims
- important issues have unresolved contradictory status
- next steps are missing owners
- reporting-period boundaries are unclear

In these cases, return a controlled draft with explicit missing-context prompts.

The workflow state should remain `blocked` or `review_needed` until those conditions are resolved.

## 8. Outputs

- `status_mail`
- `workflow_state`
- optional `handoff_contract` for downstream action
- missing-context request list where needed
- source trace map
