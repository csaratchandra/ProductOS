# Ralph Loop Workflow

Purpose: Run a governed inspect, implement, refine, validate, fix, and revalidate loop over a bounded ProductOS slice before it advances.

## Inputs

- candidate artifact bundle or implementation slice
- applicable validation tier and workflow context
- source evidence and freshness metadata
- benchmark or release context where relevant

## Outputs

- `ralph_loop_state`
- updated validation and manual-review records
- rejected-path or loophole capture when weaknesses are discovered
- explicit proceed / revise / defer / block outcome

## Operating Sequence

1. Inspect the current repo state, source evidence, and open gaps.
2. Implement or revise the bounded slice.
3. Refine the logic, traceability, readability, and recommendation quality.
4. Validate schemas, fixtures, workflow wiring, and benchmark-sensitive behavior.
5. Fix blocking issues and record rejected paths or loopholes.
6. Revalidate and emit one explicit next action.

## Rules

- do not skip from validate to release without an explicit fix and revalidate pass when blocking issues are found
- do not treat first-pass implementation as complete until a refine pass has hardened the slice
- do not treat manual review as optional when the chosen tier requires it
- if the loop discovers a structural weakness, capture it explicitly instead of burying it in a summary
- if disagreement changes the approval outcome, route to referee before release promotion
