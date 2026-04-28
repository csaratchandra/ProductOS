# Segment Priority Scoring

## Purpose

Rank segments explicitly so beachhead choices are evidence-backed and reviewable.

## Trigger / When To Use

Use when `segment_map` work needs a real beachhead choice instead of a descriptive list.

## Inputs

- segment definitions
- market and customer evidence
- delivery and proof constraints

## Outputs

- segment priority scores
- beachhead rationale
- tradeoff notes

## Guardrails

- do not hide why one segment loses to another
- keep current wedge constraints visible
- distinguish desirability from actual reachability

## Execution Pattern

1. score each segment on pain, reachability, and proof fit
2. compare the tradeoffs directly
3. recommend one beachhead with rationale
4. note what would change the ranking

## Validation Expectations

- the beachhead should feel earned
- the losing segments should still have documented rationale
- ranking should align with the current release boundary
