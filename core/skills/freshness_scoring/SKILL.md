# Freshness Scoring

## Purpose

Assess whether a source or evidence set is fresh enough for the question being asked.

## Trigger / When To Use

Use when research, release, or positioning claims depend on time-sensitive evidence.

## Inputs

- publication or last-checked timestamps
- freshness expectation for the question
- generated-at timestamp

## Outputs

- freshness label
- cadence or staleness reason
- review-needed flag when freshness is insufficient

## Guardrails

- do not treat stale evidence as fresh
- do not hide missing publication timing
- do not apply one freshness threshold to every source type

## Execution Pattern

- detect available dates
- compare against expected freshness window
- assign label and rationale
- surface stale or unknown timing as explicit review input

## Validation Expectations

- freshness labels should be reproducible from visible timestamps
- stale or unknown evidence should remain visible
- PM review should be triggered when freshness requirements are not met
