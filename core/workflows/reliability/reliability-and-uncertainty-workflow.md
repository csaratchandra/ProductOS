# Reliability And Uncertainty Workflow

Purpose: Evaluate whether a workflow output is reliable enough to transfer, publish, or escalate, especially when evidence is incomplete or contradictory.

## Inputs

- `workflow_state`
- `confidence_policy`
- source artifacts
- contradiction and missing-owner signals

## Outputs

- `reliability_state`
- publish or transfer block recommendation
- uncertainty explanation

## Rules

- separate confidence score from policy thresholds
- block or watch outputs when contradictions materially affect downstream trust
- escalate missing owner, stale evidence, or low-confidence conditions before publish
- preserve the reasons behind any override or block recommendation
- contradictory-source states should block transfer when contradiction policy is enabled
- missing-owner states should never pass publish review silently
- low-confidence, contradiction, and missing-owner causes should remain individually visible in the final rationale
