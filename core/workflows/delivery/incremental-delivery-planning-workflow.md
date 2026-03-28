# Incremental Delivery Planning Workflow

Purpose: Convert approved scope into an increment plan that makes sequencing, dependencies, and delivery risks explicit.

## 1. Outcome

Produce an `increment_plan` that makes execution inspectable before work starts by showing:

- the smallest reviewable increments
- sequencing and dependency logic
- delivery risks and confidence assumptions
- the points where replanning or escalation would be required

## 2. Inputs

Required inputs:

- approved PRD and story outputs
- current dependencies
- release or increment constraints

Optional inputs:

- issue log
- change assessments that affect the same scope
- current resourcing assumptions
- risk and confidence signals

## 3. Primary agents

- `orchestrator`
- `librarian`
- `story-acceptance`
- `analyst`
- `strategist`
- `validation`

## 4. Workflow steps

### Step 1. Gather approved scope and constraints

The librarian agent retrieves:

- current approved PRD and story pack state
- acceptance criteria where already available
- dependency records and release constraints
- open issues or change assessments that could alter planning confidence

### Step 2. Slice the work into increments

The strategist and analyst agents:

- group stories into reviewable execution increments
- separate must-have sequencing from nice-to-have batching
- identify blocker-sensitive work and early validation points

### Step 3. Map dependencies and risks

For each increment, make explicit:

- upstream and downstream dependencies
- blocker conditions
- confidence assumptions
- delivery risks that could force replanning

### Step 4. Build the plan artifact

Generate an `increment_plan` that shows:

- increment boundaries and goals
- story or feature linkage
- milestone or review points
- dependency and risk summaries

### Step 5. Validate before handoff

The validation agent checks:

- that all planned scope traces back to approved artifacts
- that no stories were silently omitted or expanded
- that dependency and blocker points are named clearly
- that uncertainty is surfaced where sequencing relies on unresolved conditions

## 5. Trigger conditions

- PRD and story pack approval
- PM request for execution planning
- major scope or dependency change affecting the current plan
- upcoming release or increment boundary

## 6. Failure rules

Do not publish a confident increment plan if:

- approved scope is incomplete or stale
- critical dependencies have unknown owners or status
- major sequencing depends on unresolved external conditions

In these cases, return a draft with explicit risk and missing-input prompts.

## 7. Outputs

- `increment_plan`
- dependency view
- delivery risk summary
- sequencing assumptions and blocker notes
