# Radar Operating Rules

Purpose: Define how ProductOS radar distinguishes signal from noise and when detected changes should trigger escalation, workflow updates, or publish interruption.

## Ranking Dimensions

- urgency: how fast action is needed
- impact scope: single artifact, workflow, workspace, suite, or portfolio
- confidence: how credible and corroborated the signal is
- reversibility: how costly it is to wait or be wrong
- customer exposure: whether the change affects customer-facing outputs or commitments

## Signal Levels

- `critical`: immediate escalation, likely publish interruption, or active delivery/customer risk
- `high`: same-day PM attention with downstream workflow or status implications
- `medium`: visible in the next operating review and tracked if repeated
- `low`: logged for trend analysis and suppressed from interruptive alerts

## Noise Suppression Rules

- merge duplicate signals from the same source window
- suppress repeated low-signal churn unless it crosses a count threshold or broadens impact scope
- age out stale alerts when the underlying issue is resolved or superseded
- do not interrupt active execution for low-confidence, low-scope signals

## Escalation Triggers

- escalate immediately when source contradictions affect customer-facing outputs
- escalate when blocked workflow, compliance risk, or failed authoritative connectors are detected
- trigger reliability review when confidence, ownership, or contradiction thresholds are crossed
- trigger status and leadership flows when the impact scope is cross-team or higher

## Required Alert Shape

Every ranked alert should include:

- why it was surfaced
- source references or event basis
- impact scope
- recommended next workflow or agent trigger
- suppression rationale if a related signal was not elevated
