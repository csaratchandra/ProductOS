# Feature Scoring And Dogfood Review Workflow

Purpose: Convert a self-hosted ProductOS feature run into a `feature_scorecard` so every next-version capability is graded before promotion.

## Inputs

- the feature slice being reviewed
- dogfood run evidence from the current self-hosting workspace
- relevant validation-lane outputs
- relevant manual validation outputs
- current `pm_superpower_benchmark`
- any relevant `outcome_review`, `feedback_cluster_state`, or `improvement_loop_state`
- for prototype-heavy slices, the latest `prototype_record` and `ux_design_review`

## Outputs

- `feature_scorecard`
- routed feedback items for any gap below `5/5`
- promote / keep-internal / improve / block recommendation

## Operating Sequence

1. Lock the feature slice, loop, and evidence window being reviewed.
2. Choose the real dogfood scenarios that prove whether the feature works in ProductOS-on-ProductOS use.
3. Score `pm_leverage`, `output_quality`, `reliability`, `autonomy_quality`, and `repeatability`.
4. For prototype-heavy slices, use the prototype-quality rubric and `ux_design_review` to justify `output_quality` and any interaction-driven `pm_leverage` claims.
5. Record reviewer, tester, and manual verdicts rather than collapsing disagreement into one sentence.
6. Assign the overall score based on the strongest level the feature fully satisfies.
7. If the score is below `5`, write explicit feedback items and route them to the existing feedback and improvement loop.
8. Emit one next action: promote, keep in internal use, route to improvement, or block.

## Rules

- do not score from aspiration; score from current dogfood evidence
- do not call a prototype-driven slice `5/5` if the latest UX review does not rate the prototype quality as `excellent`
- do not call a feature `5/5` if the PM still needs repeated manual cleanup
- `4/5` can stay active internally only if the remaining gaps are explicit and bounded
- `3/5` or below must not be counted as a completed superpower
- every sub-`5` gap must have a named feedback route instead of vague “improve later” language
