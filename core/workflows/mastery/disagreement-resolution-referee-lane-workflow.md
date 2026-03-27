# Disagreement Resolution Referee Lane Workflow

Purpose: Resolve material conflicts between AI review, AI test, and manual validation so V4 outputs have one explicit next action.

## Inputs

- conflicting lane results
- `validation_lane_report`
- affected artifact or readable doc
- benchmark, policy, and approval context

## Outputs

- `referee_decision_record`
- tie-break decision
- explicit next action and unresolved questions

## Operating Sequence

1. Name the exact disagreement and whether it is about evidence, quality, policy, or adoption value.
2. Compare each lane's position and rationale without collapsing them into a generic summary.
3. Decide whether the safest next step is proceed, revise, block, or defer.
4. Record the result in `referee_decision_record`.
5. Return the output to the parent workflow with one explicit next action.

## Rules

- referee is required when the disagreement changes approval outcome, publish safety, or scope
- do not treat a value-judgment disagreement as a schema issue or vice versa
- if the PM must decide the tradeoff directly, say that plainly instead of pretending the lanes converged
