# V7 Cutover Plan

Target Version: `7.0.0`
Source Baseline: `V6.0.0`
Current Stage: `externalize_lifecycle_publication`
Selection Status: `stable_active`
Promotion Gate: `ready`
Stable Release: `V7.0.0`

## Selected Bundle

- id: `v7_lifecycle_traceability_launch_and_outcome`
- name: `Lifecycle traceability through outcome review`
- scope: Extend item-first lifecycle traceability from release_readiness through launch_preparation and outcome_review.
- scope: Attach release communication and post-release learning evidence to the same canonical item trace.
- scope: Preserve discovery, delivery, launch, outcomes, and full_lifecycle snapshot parity across the reference and starter workspaces.
- scope: Keep external publication adapters and broader distribution packaging as later bounded releases.
- evidence: `tests/fixtures/workspaces/productos-sample/docs/delivery/lifecycle-launch-outcome-review.md`
- evidence: `templates/docs/delivery/launch-outcome-review.md`
- evidence: `tests/fixtures/workspaces/productos-sample/docs/planning/v7-candidate-note.md`

## Build Strategy

- keep V7.0.0 as the stable line for lifecycle traceability through outcome_review
- preserve full-lifecycle evidence, starter-workspace adoption parity, and launch-to-outcome traceability for the current slice
- extend beyond outcome_review only through a later bounded external-publication release

## Current Blockers

- ProductOS V7.0.0 is already the stable release.
- The next bounded expansion is external publication adapters and broader distribution packaging.
- Top priority feature remains `external_publication_adapters`.

## Required Steps

- Keep ProductOS V7.0.0 as the canonical stable line while preserving the selected full-lifecycle evidence.
- Extend ProductOS through external publication adapters only as a later bounded release.
- Keep the starter workspace as the default reusable adoption surface for the current V7 slice.

## Rules

- Do not broaden the V7 lifecycle headline beyond outcome_review until the next bounded externalization slice has passing proof.
- Keep the current V7 slice stable while publication adapters and broader distribution packaging remain explicitly deferred.

