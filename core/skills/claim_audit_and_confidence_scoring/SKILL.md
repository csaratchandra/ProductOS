# Claim Audit And Confidence Scoring

## Purpose

Label strategic claims by evidentiary status and assign confidence without hiding uncertainty.

## Trigger / When To Use

Use when ProductOS is synthesizing positioning, strategy, market, or competitor conclusions from mixed-quality evidence.

## Inputs

- claims or artifact draft
- source evidence and freshness context
- contradictions and unknowns

## Outputs

- claim audit
- confidence scoring
- downgraded or flagged claims

## Guardrails

- do not convert inference into observation
- do not assign high confidence when evidence is thin or contradictory
- do not erase uncertainty for readability

## Execution Pattern

- enumerate the major claims in the artifact
- classify each as observed, inferred, or hypothesized
- assign confidence using freshness, source quality, and contradiction context
- mark any claims that should block commitment

## Validation Expectations

- major claims should have visible confidence and evidence posture
- contradictory or weak claims should be downgraded, not polished
- the audit should help PM review happen faster, not disappear
