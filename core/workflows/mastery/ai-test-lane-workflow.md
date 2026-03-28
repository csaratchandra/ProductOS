# AI Test Lane Workflow

Purpose: Run the V4 `AI Tester` lane with schema, fixture, regression, and gate-enforcement checks.

## Inputs

- candidate artifact or readable doc
- relevant schemas, fixtures, and workflow rules
- benchmark or regression context when the output claims improvement

## Outputs

- tester findings
- pass / revise / fail recommendation
- automation-gap notes requiring manual follow-up

## Operating Sequence

1. Validate structural requirements such as schema, metadata, and required section coverage.
2. Run fixture, bundle, regression, and cross-reference checks relevant to the output class.
3. Check that gate policy, route policy, and benchmark claims are not being bypassed.
4. Separate blocking failures from non-blocking gaps and manual-only checks.
5. Return the result for inclusion in `validation_lane_report`.

## Rules

- do not claim "passed" when required automated checks were skipped
- if automation is incomplete, record the exact gap and route it to manual validation where needed
- when tests and review disagree materially, trigger referee rather than summarizing away the conflict
