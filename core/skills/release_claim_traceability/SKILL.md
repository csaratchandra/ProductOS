# Release Claim Traceability

## Purpose

Ensure every release claim points to real evidence and stays inside the current proof boundary.

## Trigger / When To Use

Use when writing or reviewing `release_note` or `release_readiness`.

## Inputs

- release note draft
- readiness checks
- validation and benchmark evidence

## Outputs

- claim-to-evidence mapping
- bounded audience scope
- flagged unsupported claims

## Guardrails

- do not publish claims without evidence refs
- keep customer-safe and internal-only scopes distinct
- preserve known limitations

## Execution Pattern

1. extract each claim
2. attach the minimum evidence set that supports it
3. mark the audience scope and evidence status
4. remove or bound any unsupported claim

## Validation Expectations

- every claim should have evidence
- unsupported claims should be obvious
- limitations should stay visible
