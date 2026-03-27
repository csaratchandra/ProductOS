# Bounded Improvement Workflow

Purpose: Convert a validated repeated-pain cluster into one bounded improvement proposal with explicit scope, validation, and PM decision gates.

## Inputs

- repeated-pain summary from loop clustering
- `improvement_loop_state`
- optional `problem_brief`, `idea_record`, and `release_scope_recommendation`
- benchmark and rejected-path memory

## Outputs

- updated `improvement_loop_state`
- bounded improvement recommendation
- revise / continue / defer / reject decision package

## Operating Sequence

1. Confirm the repeated pain is real, current, and still worth addressing.
2. Define one bounded improvement slice rather than a broad platform rewrite.
3. Record scope, validation tier, benchmark target, and PM decision path in `improvement_loop_state`.
4. Route the slice through AI review, AI test, and targeted manual validation where required.
5. Return continue, revise, defer, or reject guidance for the next Ralph-loop pass.

## Rules

- do not expand one repeated-pain cluster into speculative roadmap sprawl
- every bounded slice must name the benchmark movement it expects
- if the same slice was already rejected, require a materially different rationale before retrying it
