# Inspect And Adapt Review Workflow

Purpose: Capture system-demo and inspect-and-adapt evidence so ProductOS can learn from increment execution rather than only recording plans.

## 1. Outcome

Produce an inspect-and-adapt review that explains:

- what actually happened in the increment
- which delivery, reliability, or coordination patterns repeated
- what should change in the next planning cycle
- which decisions and follow-through actions must persist downstream

## 2. Inputs

Required inputs:

- `program_increment_state`
- increment plan outcomes
- issue trends

Optional inputs:

- change and reliability signals
- demo or meeting notes
- task and dependency completion history
- prior inspect-and-adapt reviews

## 3. Primary agents

- `orchestrator`
- `librarian`
- `analyst`
- `strategist`
- `leadership-intelligence`
- `validation`

## 4. Workflow steps

### Step 1. Collect execution evidence

The librarian agent gathers:

- the planned increment objectives
- actual outcomes against those objectives
- issue and blocker patterns during the increment
- reliability and change events that altered execution quality

### Step 2. Compare plan versus reality

The analyst agent identifies:

- objectives achieved, missed, or partially achieved
- recurring blocker types
- dependencies that resolved late or failed to resolve
- reliability or coordination problems that materially affected delivery

### Step 3. Frame improvement actions

The strategist agent converts evidence into:

- repeated-pattern findings
- concrete improvement actions for the next increment
- decisions or policy changes that should carry into planning

### Step 4. Prepare review-ready summary

If the audience includes broader leadership contexts, the leadership-intelligence agent compresses detailed findings into concise decision-ready framing without hiding repeated execution problems.

### Step 5. Validate and route forward

The validation agent checks:

- evidence supports each major finding
- improvement actions are tied to observed outcomes
- next-cycle decisions are explicit and traceable

## 5. Trigger conditions

- end of an increment or program increment
- scheduled inspect-and-adapt review cadence
- PM or delivery lead request after a major execution disruption

## 6. Failure rules

Do not produce a polished review if:

- planned objectives or actual outcomes cannot be reconstructed
- findings are based mainly on retrospective opinion without evidence
- repeated problems are described without a proposed next action

In these cases, return a review draft with evidence gaps called out explicitly.

## 7. Outputs

- inspect-and-adapt review summary
- repeated-pattern findings
- improvement actions for the next increment
- decision carry-forward notes
