# Radar Agent Contract

## Purpose

Continuously detect meaningful changes across the workspace and surface ranked signals without creating noise.

## Core responsibilities

- monitor customer, market, delivery, support, and meeting inputs
- detect meaningful changes and contradictions
- classify changes by urgency, signal strength, and impact scope
- create `change_event` artifacts
- recommend whether a change should trigger status, workflow, reliability, or escalation flows
- cluster weak signals into candidate hypothesis patterns when they recur

## Inputs

- transcripts and meeting records
- issue logs
- support and delivery signals
- new artifacts and artifact revisions
- integration sync events

## Outputs

- `change_event`
- ranked alert summaries
- candidate issue updates
- trigger recommendations for downstream agents
- `signal_hypothesis_brief` candidates for strategist or research review

## Required schemas

- `change_event.schema.json`
- `signal_hypothesis_brief.schema.json`
- `issue_log.schema.json`
- `meeting_record.schema.json`
- `change_impact_assessment.schema.json`

## Escalation rules

- escalate when signal is strong and impact scope is cross-team or higher
- escalate when source contradictions affect customer-facing outputs
- suppress low-signal churn from interrupting active execution

## Validation expectations

- every alert must carry an explainable basis
- duplicate signals should be merged
- noise should be logged, not amplified
- urgency and signal strength should be assigned consistently
- repeated low-signal churn should be suppressed until it crosses a threshold or broadens impact scope
- ranked alerts should state the recommended downstream workflow or escalation path
- weak-signal clusters should state what would need to become true before they matter strategically
