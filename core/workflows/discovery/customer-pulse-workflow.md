# Customer Pulse Workflow

Purpose: Generate a structured customer intelligence summary from available customer signals.

## 1. Outcome

Produce a `customer_pulse` artifact covering top pain points, segment health, churn risks, expansion opportunities, and voice-of-customer synthesis.

## 2. Inputs

Required inputs:

- reporting period
- cadence level (weekly, monthly, quarterly)

Optional inputs:

- support ticket data or summaries
- NPS or CSAT scores
- CRM notes
- app store reviews
- social commentary summaries
- customer interview transcripts
- feature request logs

## 3. Primary agents

- `orchestrator`
- `librarian`
- `customer-intelligence`
- `research`
- `validation`

## 4. Workflow steps

### Step 1. Aggregate signals

The customer intelligence agent gathers available customer signals from:

- ingested support data
- research briefs with customer feedback
- meeting records from customer sessions
- integrated CRM or analytics sources

### Step 2. Synthesize themes

Cluster signals into:

- pain-point themes with severity and frequency
- emerging signals not yet at pain-point level
- sentiment trends by segment

### Step 3. Score segment health

For each known segment, assign:

- health score: green, amber, or red
- trend direction: improving, stable, or declining
- supporting evidence

### Step 4. Identify risks and opportunities

- churn risks: segments or accounts showing declining signals
- expansion opportunities: segments showing interest in new capabilities
- trending feature requests with frequency data

### Step 5. Compile voice-of-customer

Select representative customer quotes that illustrate key themes. Tag each with source and sentiment.

### Step 6. Validate

The validation agent checks:

- pain points have supporting evidence
- segment health scores are consistent with signal data
- churn risks have actionable signal descriptions

### Step 7. PM review

The PM reviews the pulse brief, adds context, and approves.

## 5. Trigger conditions

- weekly, monthly, or quarterly cadence
- PM request for ad hoc customer intelligence
- significant customer signal event such as NPS drop or churn spike

## 6. Failure rules

Do not produce a pulse brief with only one source. Require at minimum two independent signal sources for segment health claims.

## 7. Outputs

- `customer_pulse`
- missing-data request list where signal coverage is insufficient

## 8. Companion templates

- `../../templates/discovery/customer_pulse.md`
- `../../templates/research/source_note_card.md`
- `../../templates/research/research_brief.md`
