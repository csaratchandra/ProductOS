# Signal Priority Scoring

## Purpose

Convert mixed evidence into a visible priority score without hiding burden, ambiguity, or weak proof.

## Trigger / When To Use

Use when ProductOS must rank problems, opportunities, or features and the repo should preserve why.

## Inputs

- current evidence artifacts
- agentic leverage assumptions
- compliance and ambiguity burden

## Outputs

- score inputs
- priority lane assignment
- rationale for rank ordering

## Guardrails

- do not compress all tradeoffs into one unexplained number
- keep PM override explicit
- preserve weak evidence warnings

## Execution Pattern

1. score customer value, strategic fit, leverage, and burden separately
2. assign a lane with rationale
3. record the source artifacts behind the rank
4. note where PM judgment overrode the raw order

## Validation Expectations

- the score should be explainable quickly
- burden should visibly affect the result
- source artifacts should remain attached to the decision
