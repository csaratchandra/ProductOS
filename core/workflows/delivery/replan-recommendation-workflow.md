# Replan Recommendation Workflow

Purpose: Recommend the smallest safe replan when priorities, evidence, or constraints change mid-stream.

## 1. Outcome

Produce a recommendation that helps the PM choose the smallest safe replan by making explicit:

- what should stay fixed
- what should change in scope, sequencing, or timing
- the customer and delivery tradeoffs of each option
- when leadership review is required before acting

## 2. Inputs

Required inputs:

- `change_impact_assessment`
- current increment plan
- open dependencies and risks
- current commitments

Optional inputs:

- current status updates
- release constraints
- portfolio or leadership priorities
- prior replan decisions for similar changes

## 3. Primary agents

- `orchestrator`
- `librarian`
- `strategist`
- `analyst`
- `leadership-intelligence`
- `validation`

## 4. Workflow steps

### Step 1. Retrieve current commitments

The librarian agent gathers:

- the active increment plan
- the triggering `change_impact_assessment`
- open dependency and risk state
- any customer or leadership commitments that constrain replanning

### Step 2. Generate materially different options

The strategist and analyst agents produce options that vary in:

- scope retained versus deferred
- sequencing changes
- delivery risk exposure
- time cost and confidence impact

### Step 3. Rank and recommend

Rank options by:

- customer impact
- delivery risk
- time cost
- preservation of existing commitments

Prefer the smallest safe replan rather than broad unnecessary reshuffling.

### Step 4. Check for escalation requirements

If the top recommendation changes external promises or leadership-approved scope, the leadership-intelligence agent adds explicit decision-needed framing for escalation.

### Step 5. Validate the recommendation

The validation agent checks:

- preserved commitments and changed commitments are explicit
- the recommended option matches the upstream impact assessment
- tradeoffs are concrete rather than implied

## 5. Trigger conditions

- completion of `change_impact_assessment` with replan-needed outcome
- PM request for option framing after plan drift
- mid-increment capacity, dependency, or priority shift

## 6. Failure rules

Do not present a single confident recommendation if:

- current commitments are unclear or contradictory
- options differ only cosmetically
- the recommendation would change leadership-approved scope without explicit escalation framing

In these cases, return ranked options with an explicit decision-needed summary.

## 7. Outputs

- ranked replan options
- recommended scope or sequencing adjustment
- decision-needed summary
- commitment-preservation notes
