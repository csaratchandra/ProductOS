# Retrieval Selection

## Purpose

Choose the right prior ProductOS context before downstream work begins.

## Trigger / When To Use

Use when a persona, workflow, or runtime route needs canonical prior context rather than a broad dump of history.

## Inputs

- active question or task
- available artifacts, traces, and memory signals
- canonical-state hints

## Outputs

- retrieval bundle
- canonical context recommendation
- stale or conflicting context flags

## Guardrails

- do not silently substitute one source of truth for another
- do not overwhelm downstream work with irrelevant history
- do not treat stale context as canonical

## Execution Pattern

- identify candidate prior artifacts
- rank by relevance and canonical status
- package a bounded retrieval bundle
- surface conflicts or stale references

## Validation Expectations

- retrieval bundles should be explainable and bounded
- canonical recommendations should cite concrete source refs
- duplicate or conflicting state should remain visible
