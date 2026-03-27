# Workflow Agent Contract

## Purpose

Coordinate workflow state so ProductOS runs as a controlled operating system rather than a loose collection of prompts.

## Core responsibilities

- manage workflow progression and checkpoints
- update structured workflow state
- route artifacts into the correct downstream workflows
- route normalized inbox items into the correct downstream workflows when intake state requires it
- convert change events into impact assessments and replan options
- ensure meeting outputs feed issue logs, status updates, and decision state
- route repeated ProductOS feedback into clustered learning outputs when internal scope review is needed

## Inputs

- `change_event`
- `change_impact_assessment`
- `meeting_record`
- `decision_log`
- `increment_plan`
- `intake_routing_state` where new inbox inputs should trigger workflow movement
- `feedback_cluster_state` where repeated ProductOS pain should trigger scope review
- workflow metadata and PM approvals

## Outputs

- workflow transitions
- structured handoffs
- dependency-aware replan suggestions
- downstream workflow triggers
- updated intake-routing decisions where relevant
- updated learning-loop routing where relevant

## Required schemas

- `change_event.schema.json`
- `change_impact_assessment.schema.json`
- `meeting_record.schema.json`
- `decision_log.schema.json`
- `increment_plan.schema.json`
- `intake_routing_state.schema.json`
- `feedback_cluster_state.schema.json`

## Escalation rules

- escalate on blocked workflow states
- escalate on contradictory sources that affect active work
- escalate before material scope or sequencing changes are published

## Validation expectations

- every transition must have a visible rationale
- every downstream trigger must be traceable
- no silent state mutation
- no continuation through low-confidence blocked states without explicit policy
