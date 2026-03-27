# Integration And Compliance Review Workflow

Purpose: Evaluate connector health, source-of-truth conflicts, and trust/compliance findings before ProductOS relies on integrated external state.

## Inputs

- `connector_manifest`
- `source_of_truth_policy`
- privacy, policy, and compliance review findings
- integration failure signals

## Outputs

- `integration_state`
- trust and compliance review summary
- publish-block or escalation recommendation

## Rules

- authoritative connector failures should block dependent publish paths when policy requires it
- stale authoritative connectors should trigger watch or escalation handling
- privacy, policy, and compliance findings should remain explicit in the review output
- never silently continue when source-of-truth conflicts remain unresolved
- workspace-manual mode is allowed only when the source-of-truth policy explicitly permits it
- publish-block rationale should name the failed or stale authoritative connector directly
- cross-system conflicts should recommend whether to pause publish, escalate, or continue with explicit override
