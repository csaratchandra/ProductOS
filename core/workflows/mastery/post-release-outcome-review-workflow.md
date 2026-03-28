# Post Release Outcome Review Workflow

Purpose: Measure whether an adopted V4 slice delivered the intended PM, agent, and workflow outcomes, then decide whether to keep, iterate, or roll it back.

## Inputs

- `pm_superpower_benchmark`
- `ai_agent_benchmark`
- latest `feature_scorecard` for the reviewed slice
- release or adoption evidence such as `release_gate_decision`, `productos_feedback_log`, and `document_sync_state`
- any relevant `rejected_path_record`

## Outputs

- `outcome_review`
- updated `feature_scorecard` when the slice still needs improvement
- keep / iterate / rollback recommendation
- updated rejected-path memory when a route fails

## Operating Sequence

1. Choose the specific change or slice being reviewed and lock the relevant benchmark window.
2. Compare expected signals against observed usage, quality, and benchmark evidence.
3. Record outcome status for each target outcome instead of hiding mixed results in one summary.
4. If the slice is still below the superpower bar, update the `feature_scorecard` and route the remaining gaps into the improvement loop.
5. Update `rejected_path_record` when the reviewed path should not be repeated unchanged.
6. Emit `outcome_review` with the next action for the next Ralph-loop pass.

## Rules

- do not call a slice successful just because artifacts, docs, or workflows now exist
- do not leave a sub-`5/5` feature score implicit after outcome review
- if adoption is weak or pain recurs, say iterate or rollback instead of using vague progress language
- outcome review should update loop memory so the same dead end does not come back as a "new" idea
