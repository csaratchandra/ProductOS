# Program Increment Planning Workflow

Purpose: Support SAFe-compatible program increment planning with explicit objectives, dependencies, and inspectable evidence.

## 1. Outcome

Produce a `program_increment_state` that makes coordinated delivery visible across teams by showing:

- PI objectives and confidence
- cross-team dependencies and risks
- objective changes and tradeoffs
- the evidence needed for inspect-and-adapt review later

## 2. Inputs

Required inputs:

- product and feature status
- increment plans
- cross-team dependencies

Optional inputs:

- current risks and change assessments
- portfolio state
- leadership priorities
- prior PI review findings

## 3. Primary agents

- `orchestrator`
- `librarian`
- `analyst`
- `strategist`
- `leadership-intelligence`
- `validation`

## 4. Workflow steps

### Step 1. Build the PI planning baseline

The librarian agent retrieves:

- current product and feature status
- active increment plans
- known cross-team dependencies
- open risks and current change assessments

### Step 2. Define PI objectives

The analyst and strategist agents:

- synthesize objectives from active plans and priorities
- separate committed objectives from stretch objectives where needed
- identify assumptions that affect objective confidence

### Step 3. Map cross-team tradeoffs

Make explicit:

- dependency chains across teams or products
- bottleneck risks
- sequencing conflicts
- objective changes required by new evidence or capacity shifts

### Step 4. Draft the PI state artifact

Generate a `program_increment_state` with:

- objective summaries
- dependency and risk view
- evidence for changed tradeoffs
- carry-forward notes for inspect-and-adapt review

### Step 5. Validate and socialize

The validation and leadership-intelligence agents check:

- dependency visibility is complete enough for coordinated execution
- objective changes and tradeoffs are evidence-backed
- leadership-facing summaries do not hide blocked or fragile commitments

## 5. Trigger conditions

- PI planning cadence
- major cross-team scope or capacity change
- PM or delivery leadership request for coordinated planning state

## 6. Failure rules

Do not present a confident PI state if:

- cross-team dependencies remain materially unknown
- objective changes are proposed without evidence
- major risks are compressed into vague summary language

In these cases, return a draft PI state with unresolved dependencies and decision gaps highlighted.

## 7. Outputs

- `program_increment_state`
- PI objectives summary
- dependency and risk view
- tradeoff and confidence notes
