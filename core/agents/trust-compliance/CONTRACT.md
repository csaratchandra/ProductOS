# Trust And Compliance Agent Contract

## Purpose

Evaluate whether an artifact may be viewed, approved, or published based on sensitivity, access policy, and trust/compliance review state.

## Core responsibilities

- classify customer-safe versus internal-only outputs
- apply access rules by role
- track privacy, policy, and compliance review outcomes
- block publish when required reviews are pending or rejected

## Inputs

- `access_policy`
- `artifact_sensitivity`
- `compliance_review_state`

## Outputs

- publish eligibility decision
- trust/compliance findings
- customer-safe versus internal-only boundary status

## Required schemas

- `access_policy.schema.json`
- `artifact_sensitivity.schema.json`
- `compliance_review_state.schema.json`

## Escalation rules

- escalate when an internal-only or restricted artifact is routed to a customer-safe path
- escalate when required review state is pending or rejected
- escalate when actor role is not allowed to publish

## Validation expectations

- boundary decisions must be explicit
- review findings must explain publish blocks
- publish allowance must match role policy

