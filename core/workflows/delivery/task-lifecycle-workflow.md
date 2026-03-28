# Task Lifecycle Automation Workflow

Purpose: Automate the creation, status tracking, and change detection of delivery tasks from approved PRDs and story packs.

## 1. Outcome

Keep the `item_tracking_log` in sync with approved stories and delivery progress. Detect blocked or changed tasks and alert the PM.

## 2. Inputs

Required inputs:

- approved story pack or PRD with user stories
- current item tracking log

Optional inputs:

- external tracking system state from Jira or Aha connectors
- change events that affect scope or timeline
- delivery signals from engineering

## 3. Primary agents

- `orchestrator`
- `librarian`
- `chore-automation`
- `radar`
- `validation`
- `integration` where external systems are connected

## 4. Workflow steps

### Step 1. Task creation from stories

When new user stories are approved in a story pack or PRD:

- create task items in the item tracking log
- carry over acceptance criteria, owner, and target date
- link each task to its source story
- preserve attached implementation context references so engineering can retrieve the same handoff packet later
- preserve the canonical artifact link so later change detection can find the source

### Step 2. Status sync

Periodically or on event:

- check delivery signals or external tracker for status changes
- update task status: not-started, in-progress, blocked, completed
- detect tasks that have been blocked for longer than the threshold
- preserve the last trusted external source when tracker and manual state disagree

### Step 3. Change detection

When a change event affects a requirement or story:

- identify tasks derived from that requirement
- flag affected tasks with a change notice
- draft a change summary for the PM
- route material impacts into change assessment rather than only annotating the task log

### Step 4. Blocked task escalation

When a task remains blocked beyond the workspace threshold:

- escalate to the PM with context, owner, and blocker description
- include recommended unblocking actions
- identify whether the blocker is local, dependency-driven, or leadership-relevant

### Step 5. Validate

The validation agent checks:

- all approved stories have corresponding tasks
- no orphan tasks without story linkage
- blocked tasks have owners and blocker descriptions
- task status changes remain traceable to an approved source or trusted external signal

## 5. Trigger conditions

- story pack or PRD approval
- delivery status signal from engineering or external system
- change event affecting requirements
- scheduled daily task health check

## 6. Failure rules

Do not auto-resolve blocked tasks. Always escalate to the PM for judgment.

Do not silently overwrite trusted tracker state when manual and external states conflict. Surface the contradiction for review.

## 7. Outputs

- updated `item_tracking_log`
- change notices for affected tasks
- blocked task escalation alerts
- conflict notes where task truth is unclear
