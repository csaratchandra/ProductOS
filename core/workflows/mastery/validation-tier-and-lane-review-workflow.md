# Validation Tier And Lane Review Workflow

Purpose: Determine the validation tier for a V4 output, run the required lanes for that tier, and emit `validation_lane_report` before the output advances.

## Inputs

- [validation-tier-policy.md](/Users/sarat/Documents/code/ProductOS/core/docs/validation-tier-policy.md)
- [v4-artifact-workflow-matrix.md](/Users/sarat/Documents/code/ProductOS/core/docs/archive/version-history/v4-artifact-workflow-matrix.md)
- candidate artifact or readable doc
- relevant workflow state and upstream traceability context
- benchmark context where the output claims leverage or release movement

## Outputs

- `validation_lane_report`
- revise / proceed / block guidance
- referee escalation when lane disagreement occurs

## Operating Sequence

1. Classify the candidate output by risk, audience, and commitment level.
2. Choose `Tier 0`, `Tier 1`, `Tier 2`, or `Tier 3` using the validation-tier policy and workflow matrix.
3. Run `AI Reviewer` checks for logic, framing, traceability, and audience fit.
4. Run `AI Tester` checks for schema, fixture, regression, gate-enforcement, and benchmark behavior where relevant.
5. Determine whether manual validation is not required, sampled, targeted, or mandatory.
6. Emit `validation_lane_report` with lane outcomes, unresolved questions, and the next action.
7. Route any material disagreement to referee instead of merging conflicting conclusions.

## Rules

- do not downgrade a tier just to avoid manual validation
- if the workflow matrix and risk reality disagree, use the stricter tier and record why
- if AI review or AI test finds a blocking defect, the report should say revise or block rather than implying partial success
- if manual validation is still pending for a required lane, the artifact may be ready for manual validation but not fully passed
- referee routing is required whenever disagreement would change scope, publish safety, or approval outcome
