# Artifact Quality Grading

## Purpose

Grade whether an artifact is merely valid, reviewable, or decision-ready before it is allowed to drive downstream work.

## Trigger / When To Use

Use when ProductOS has generated or refreshed a strategy, competitor, or market artifact and must decide whether it can be committed or only reviewed as draft.

## Inputs

- artifact payload
- required evidence and linkage expectations
- workflow stage and downstream dependency context

## Outputs

- quality grade
- blocking gaps
- recommendation to commit, review, or gather more evidence

## Guardrails

- do not treat schema validity as decision readiness
- do not let draft artifacts silently drive posture or scope
- do not hide blocked states behind a clean summary

## Execution Pattern

- inspect the artifact against the stage-specific quality bar
- identify blocking evidence, linkage, or option gaps
- assign a grade and recommendation
- preserve the blockers for downstream review

## Validation Expectations

- the quality grade should match the visible artifact evidence
- blocked artifacts should expose why they are blocked
- downstream workflows should be able to use the grade as a routing signal
