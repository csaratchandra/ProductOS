# Failure-Mode System

Purpose: Define how ProductOS behaves when work is uncertain, contradictory, blocked, stale, or otherwise unsafe to continue normally.

## Failure Modes

- low confidence: the output does not meet publish or transfer thresholds
- contradictory sources: materially conflicting evidence affects the recommendation
- blocked workflow: a required dependency, approval, or owner is missing
- stale evidence: authoritative source freshness is outside acceptable bounds
- unresolved adjudication: required PM or reviewer judgment has not been provided

## Response Rules

- low-confidence states should trigger watch or block status based on policy thresholds
- contradictory-source states should block transfer when contradiction policy requires it
- blocked-workflow states should preserve the blocker reason and required next actor
- stale-evidence states should route through reliability or integration review before publish
- unresolved adjudication should prevent silent continuation on customer-facing paths

## No-Go Thresholds

- publish should stop when policy blocks, unresolved contradictions, or missing required reviews remain
- transfer should stop when downstream work would inherit unresolved contradiction or confidence failures
- overrides must be logged with the reason and approving actor
