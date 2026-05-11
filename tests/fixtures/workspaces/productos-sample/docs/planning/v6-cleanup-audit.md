# V6 Cleanup Audit

Status: active
Audience: PM, engineering, repo maintainer
Owner: ProductOS PM
Updated At: 2026-03-27

## Goal

Keep the published ProductOS surface centered on `V6.0.0` without deleting older files that still protect V6 correctness, reproducibility, or release history.

## V6 Publish Surface

The active publish surface is:

- `core/`
- `scripts/`
- `productos`
- `templates/`
- the current reference docs and artifacts needed to prove `V6.0.0`
- `registry/releases/release_6_0_0.json`
- the current workspace and suite registrations

Older versions should not be presented as PM-facing download targets.

## Historical Files Still Supporting V6

These older surfaces are still intentionally retained because removing them would break V6 traceability, tests, or release history:

- prior release metadata under `registry/releases/`
- V5 lifecycle artifacts and tests that keep the prior stable slice reproducible
- `tests/fixtures/workspaces/productos-sample/archive/historical-artifacts/`
- `core/docs/archive/version-history/`
- tests that validate historical releases and archive bundles

## Safe Rule Right Now

- exclude older files from PM-facing distribution
- keep older files that are still referenced by runtime code, tests, or release records
- remove older files only after the dependency that still references them is deleted or rewritten

## Concrete Follow-Up Cleanup

Before deleting old material, clear these dependency classes first:

1. tests that explicitly validate V4 and V5 historical assets
2. runtime or docs that still reference archived release paths
3. release-history records that need earlier versions for provenance

## Current Finding

The main immediate problem was not older files existing in the repo.

The main immediate problem was active V6 docs still citing some V5 artifact ids. That has been corrected.
