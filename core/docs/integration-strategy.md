# Integration Strategy

Purpose: Define how ProductOS moves from file-drop support to a more ambient, policy-driven integration model without losing source-of-truth discipline.

## Strategy Layers

- connector strategy: define which systems provide authoritative state for which domains
- sync model: scheduled, event-driven, or manual sync behavior by connector
- refresh logic: stale thresholds, retry expectations, and escalation timing
- source-of-truth rules: domain-level authority and conflict action
- disagreement handling: what happens when multiple systems disagree materially

## Expected Connector Behavior

- every connector should declare freshness thresholds and owned domains
- authoritative connector failure should state whether publish pauses or only escalates
- derived ProductOS artifacts should remain explicit about when they depend on stale upstream state

## Practical Interpretation

- ProductOS should not mirror external systems blindly
- ProductOS should normalize only the operating state needed for decision quality, traceability, and leadership visibility
- integration realism means freshness, conflict, and fallback behavior are visible, not hidden
