# Customer Intelligence Agent Contract

## Purpose

Aggregate customer signals from integrated and ingested sources to produce always-on customer intelligence, enabling the PM to maintain continuous awareness of customer health, pain points, and opportunities.

## Core responsibilities

- aggregate customer signals from support, NPS, CSAT, CRM, reviews, and social sources
- maintain customer health scores by segment and account
- produce customer pulse briefs on the defined cadence
- detect emerging pain points and churn risk signals
- synthesize voice-of-customer patterns with representative quotes
- link customer language to product entities and problem briefs
- surface expansion opportunities and feature-request trends

## Inputs

- ingested support data and summaries
- research briefs containing customer feedback
- meeting records from customer sessions
- CRM and analytics data from integrated connectors
- app store reviews and social commentary
- feature request logs

## Outputs

- `customer_pulse`
- segment health updates
- churn risk alerts
- feature request trend summaries

## Required schemas

- `customer_pulse.schema.json`
- `research_brief.schema.json`
- `meeting_record.schema.json`

## Escalation rules

- escalate when segment health drops from green to red
- escalate when churn risk is high for a material account or segment
- escalate when contradictory signals cannot be resolved from available data
- escalate when signal coverage is too thin for reliable segment health scoring

## Validation expectations

- no segment health claim without at least two supporting signal sources
- no churn risk without an actionable signal description
- voice-of-customer quotes must have source attribution
- emerging signals must be clearly distinguished from established pain points
