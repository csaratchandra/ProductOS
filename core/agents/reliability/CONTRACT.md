# Reliability Agent Contract

## Purpose

Evaluate whether ProductOS should continue, transfer, or publish based on confidence, contradiction, missing ownership, and blocked-work conditions.

## Core responsibilities

- evaluate reliability state before transfer or publish
- apply confidence policy thresholds
- detect blocked and low-confidence workflow conditions
- produce `reliability_state` artifacts
- require PM override where policy allows but confidence is below threshold

## Inputs

- `confidence_policy`
- `workflow_state`
- `meeting_record`
- `status_mail`
- `issue_log`
- handoff contracts and change assessments where relevant

## Outputs

- `reliability_state`
- publish-block recommendation
- transfer-block recommendation
- override-required flag

## Required schemas

- `confidence_policy.schema.json`
- `reliability_state.schema.json`
- `workflow_state.schema.json`
- `status_mail.schema.json`

## Escalation rules

- escalate when publish is blocked
- escalate when critical actions are ownerless
- escalate when contradiction policy is triggered

## Validation expectations

- confidence decisions must be explainable
- blocked state must include explicit reasons
- override-required must only appear when policy allows PM override

