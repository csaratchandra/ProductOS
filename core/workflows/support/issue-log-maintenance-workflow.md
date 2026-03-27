# Issue Log Maintenance Workflow

Purpose: Maintain a structured issue log so the PM is not manually reconstructing open problems, risks, and mitigations across tools and meetings.

## 1. Outcome

Produce and maintain an `issue_log` artifact with current issue state, owners, severity, status, and mitigation notes.

## 2. Inputs

- meeting records
- transcript-derived issue flags
- change events
- delivery and dependency alerts
- support and quality signals
- PM corrections and overrides

## 3. Primary agents

- `radar`
- `workflow`
- `status-communications`
- `reliability`
- `validation`

## 4. Workflow steps

### Step 1. Gather candidate issues

Collect potential issues from:

- blocked workflow incidents
- dependency risks
- launch readiness changes
- transcript-derived blockers
- support and quality patterns

### Step 2. Normalize and deduplicate

For each candidate issue:

- assign category
- assign severity
- infer current owner where possible
- merge duplicates
- preserve source references

### Step 3. Validate issue quality

An issue should not enter the log unless it has:

- a clear title
- a defined severity
- a current status
- an owner or explicit owner gap
- a mitigation or next action

### Step 4. Ask for PM clarification only where necessary

Prompt the PM only when:

- ownership cannot be inferred
- severity is ambiguous
- mitigation is politically sensitive
- two sources materially disagree

### Step 5. Publish updated log

Update the `issue_log` artifact and expose deltas:

- newly opened issues
- severity changes
- resolved issues
- issues now considered blocked

## 5. Trigger conditions

- new meeting transcript processed
- dependency or delivery risk detected
- scheduled status cadence
- PM manual request

## 6. Outputs

- `issue_log`
- issue delta summary
- unresolved clarification requests

