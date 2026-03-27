# Current ProductOS Plan

Status: active
Audience: PM, engineering, design, leadership
Owner: ProductOS PM
Updated At: 2026-03-27

## Current Stable Line

ProductOS `V6.0.0` is the current stable core line.

The promoted bounded slice is lifecycle traceability through `release_readiness`.

That means the repo now expects one canonical item trace to stay explicit across:

- `signal_intake`
- `research_synthesis`
- `segmentation_and_personas`
- `problem_framing`
- `concept_shaping`
- `prototype_validation`
- `prd_handoff`
- `story_planning`
- `acceptance_ready`
- `release_readiness`

The currently deferred stages are:

- `launch_preparation`
- `outcome_review`

## Canonical Plan Sources

Read these in order:

1. [v6-candidate-note.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/planning/v6-candidate-note.md)
2. [v6-cutover-plan.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/planning/v6-cutover-plan.md)
3. [lifecycle-release-readiness-review.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/delivery/lifecycle-release-readiness-review.md)

These three files are now the canonical human-readable V6 plan path.

## What Was Implemented

- V6 runtime bundle and CLI support
- checked-in V6 release artifacts and release metadata
- lifecycle state extended through `release_readiness` in the self-hosting and starter workspaces
- concrete lifecycle snapshots for `discovery`, `delivery`, `launch`, `outcomes`, and `full_lifecycle`
- preserved archived V5 state so the V5 bundle remains reproducible

## Current Next Problem

The next bounded expansion is lifecycle traceability beyond `release_readiness`.

That follow-on slice should answer:

- what minimum launch-preparation evidence is mandatory before a trace can claim launch coverage
- what minimum outcome-review evidence is mandatory before a trace can claim post-release learning coverage
- how external publication and communication routes should consume lifecycle traces as first-class inputs

## Fast Verification

Use these commands when checking the current plan and implementation state:

- `./productos status`
- `./productos v6 --output-dir /tmp/productos-v6-lifecycle`
- `./productos cutover --output-path workspaces/productos-v2/docs/planning/v6-cutover-plan.md`
- `python3 scripts/validate_artifacts.py`
- `pytest`

## Why This File Exists

Finding the active ProductOS plan should not require searching across runtime code, release metadata, and workspace docs.

This file is the canonical starting point for the current plan.
