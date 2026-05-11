# V6 Cutover Plan

Target Version: `6.0.0`
Source Baseline: `V5.0.0`
Current Stage: `extend_lifecycle_beyond_release_readiness`
Selection Status: `stable_active`
Promotion Gate: `ready`
Stable Release: `V6.0.0`

## Selected Bundle

- id: `v6_lifecycle_traceability_release_readiness`
- name: `Lifecycle traceability through release readiness`
- scope: Extend item-first lifecycle traceability from `prd_handoff` through `story_planning`, `acceptance_ready`, and `release_readiness`.
- scope: Back every advertised trace focus area with concrete workspace snapshots across `discovery`, `delivery`, `launch`, `outcomes`, and `full_lifecycle`.
- scope: Keep `launch_preparation` and `outcome_review` explicit but `not_started` until a later release extends them.
- scope: Use the starter workspace as the clean reusable adoption surface for the same traceability model.
- evidence: `tests/fixtures/workspaces/productos-sample/docs/delivery/lifecycle-release-readiness-review.md`
- evidence: `templates/docs/delivery/release-readiness-review.md`
- evidence: `tests/fixtures/workspaces/productos-sample/feedback/2026-03-23-design-and-architecture-review.md`

## Build Strategy

- keep V6.0.0 as the stable line for lifecycle traceability through release_readiness
- preserve release evidence, trace focus-area coverage, and starter-workspace adoption parity for the current slice
- extend beyond release_readiness only through a later bounded release

## Current Blockers

- ProductOS V6.0.0 is already the stable release.
- The next bounded expansion is extending lifecycle traceability beyond release_readiness.
- Top priority feature remains `extend_lifecycle_beyond_release_readiness`.

## Required Steps

- Keep ProductOS V6.0.0 as the canonical stable line while preserving the selected release-readiness lifecycle evidence.
- Extend lifecycle traceability beyond release_readiness only as a later bounded release.
- Keep the starter workspace as the default reusable adoption surface for the current V6 slice.

## Rules

- Do not broaden the V6 lifecycle headline beyond release_readiness until the next bounded slice has passing proof.
- Keep the current V6 slice stable while launch and outcome stages remain explicitly deferred.
