# Current ProductOS Plan

Status: active
Audience: PM, engineering, design, leadership
Owner: ProductOS PM
Updated At: 2026-04-27

## Current Stable Line

ProductOS `V8.4.0` is the current stable core line.

The promoted stable slice combines:

- strategy-quality upgrade and decision-ready strategy artifacts
- mission-first control-plane hardening
- governed research and alignment paths that now clear the bounded baseline gate
- bounded visual export and workflow corridor surfaces over the same governed PM operating model

## Canonical Plan Sources

Read these in order:

1. [roadmap.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/roadmap.md)
2. [mission-brief.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/mission-brief.md)
3. [research-superpower-plan.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/research-superpower-plan.md)
4. [pm-superpower-recovery-plan.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/pm-superpower-recovery-plan.md)

These files are the canonical human-readable next-version plan path.

Superseded planning inputs that must not drive `v9` release proof:

- `tests/fixtures/workspaces/productos-sample/artifacts/increment_plan.json`
- `tests/fixtures/workspaces/productos-sample/artifacts/program_increment_state.json`
- `tests/fixtures/workspaces/productos-sample/outputs/improve/next_version_release_gate_decision.json`

Those March artifacts remain in the repo only as historical context. The April 27 planning set above is canonical for lifecycle-enrichment release work.

## What Was Implemented

- V8.4.0 stable release metadata, strategy-quality upgrade, and bounded visual-release surfaces
- visual CLI expansion through `./productos visual plan|build|review|export`
- workflow corridor component, contracts, schemas, and examples
- shared visual foundations for deck, map, and corridor rendering
- reference alignment outputs that now emit corridor artifacts alongside deck artifacts

## Active Next-Version Program

The active next program is lifecycle enrichment reconciliation across `P0`, `P1`, and `P2`.

The internal promotion candidate for that program is `v9 = 9.0.0`, but the public stable line remains `V8.4.0` until one shared `go` gate clears across all three tracks.

This program should answer:

- `P0`: how runtime, starter/adopted workspaces, governed docs, Ralph gating, and execution-driving schemas stay coherent when newer discovery artifacts are absent or partially adopted
- `P1`: how governed research, framework selection, prioritization logic, and downstream handoff context form one decision-ready packet instead of optional side artifacts
- `P2`: how launch, support, outcome, and post-launch evidence loops preserve traceability and recommend bounded reopen actions instead of silently mutating the decision chain

The visual operating system remains an aligned-output slice within this broader program:

- keep deck, map, and workflow corridor outputs consistent with the enriched lifecycle spine
- do not let visual publication outrank runtime safety, research coherence, or traceability proof
- keep external claims bounded to the evidence-backed `V8.4.0` line while the broader lifecycle-enrichment program hardens internally

Reference:

1. [research-superpower-plan.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/research-superpower-plan.md)
2. [pm-superpower-recovery-plan.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/pm-superpower-recovery-plan.md)
3. [mission-brief.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/mission-brief.md)

## Program Posture

Do not broaden release claims beyond `V8.4.0` while this reconciliation program is in flight.

The immediate bar is runtime safety and repo coherence, not a larger public promise.

## Fast Verification

Use these commands when checking the current plan and implementation state:

- `./productos status`
- `python3 scripts/validate_artifacts.py`
- `pytest`

## Why This File Exists

Finding the active ProductOS plan should not require searching across runtime code, release metadata, and workspace docs.

This file is the canonical starting point for the current plan.
