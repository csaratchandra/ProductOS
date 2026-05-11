# V6 Public Distribution Manifest

Status: active
Audience: PM, engineering, repo maintainer
Owner: ProductOS PM
Updated At: 2026-03-27

## Purpose

Define the exact V6-only publication boundary so git upload, repo maintenance, and PM download do not rely on guesswork.

## Decision

Git publishes the repository root, not a single workspace folder.

So if ProductOS is meant to publish as a V6-only repo, the public upload must be a clean export branch or separate clean repo that contains only the paths listed here.

Pushing the current working repo as-is would also publish historical releases, archive material, and reference history.

## Two Surfaces

There are two different surfaces that need to stay distinct:

- maintainable V6 source repo: the codebase a maintainer pushes to git
- PM usage surface: the starter workspace PMs use to create a new product workspace

The PM usage surface is not the same thing as the full source repo.

## Maintainable V6 Source Repo

Publish the repository root with these paths included:

### Root Files

- `.gitignore`
- `README.md`
- `package.json`
- `package-lock.json`
- `productos`

### ProductOS Core

- `components/presentation/`
- `core/agents/`
- `core/constitution/`
- `core/docs/` except `core/docs/archive/`
- `core/examples/`
- `core/packs/`
- `core/python/`
- `core/rubrics/`
- `core/schemas/`
- `core/templates/`
- `core/workflows/`

### Scripts

- `scripts/productos.py`
- `scripts/validate_artifacts.py`
- `scripts/export_presentation.py`
- `scripts/presentation_export_pptx.mjs`
- `scripts/promote_release.py`

### Registry

- `registry/releases/release_6_0_0.json`
- `registry/workspaces/ws_productos_v2.registration.json`
- `registry/suites/suite_productos.registration.json`

### Starter Workspace

- `templates/`

### Reference V6 Maintenance Slice

Keep the current reference workspace, but only as the trimmed V6 maintenance slice:

- `tests/fixtures/workspaces/productos-sample/README.md`
- `tests/fixtures/workspaces/productos-sample/workspace_manifest.yaml`
- `tests/fixtures/workspaces/productos-sample/artifacts/` excluding explicit V5 release files
- `tests/fixtures/workspaces/productos-sample/docs/` excluding explicit V5 planning files
- `tests/fixtures/workspaces/productos-sample/feedback/`
- `tests/fixtures/workspaces/productos-sample/handoffs/`
- `tests/fixtures/workspaces/productos-sample/inbox/`

### Current Test Surface

Keep the current generic and V6-focused test surface:

- `tests/conftest.py`
- `tests/fixtures/`
- `tests/test_artifact_schemas.py`
- `tests/test_component_consistency.py`
- `tests/test_entities.py`
- `tests/test_feature_scorecard_assets.py`
- `tests/test_lifecycle_trace_assets.py`
- `tests/test_lifecycle_trace_execution.py`
- `tests/test_productos_cli.py`
- `tests/test_release_promotion.py`
- `tests/test_v6_lifecycle_bundle.py`
- `tests/test_v6_release_assets.py`

## PM Usage Surface

The only PM-facing workspace surface is:

- `templates/`

PMs should clone the V6 repo and initialize a new workspace from `templates/`.

PMs should not work inside `tests/fixtures/workspaces/productos-sample/`.

## Exclude From Public V6 Upload

Do not include these paths in the public V6-only repo:

- `node_modules/`
- `.pytest_cache/`
- any `__pycache__/` directory
- any `.DS_Store` file
- `core/docs/archive/`
- `tests/fixtures/workspaces/productos-sample/archive/`
- `tests/fixtures/workspaces/productos-sample/artifacts/runtime_scenario_report_v5_lifecycle_traceability.json`
- `tests/fixtures/workspaces/productos-sample/artifacts/validation_lane_report_v5_lifecycle_traceability.json`
- `tests/fixtures/workspaces/productos-sample/artifacts/manual_validation_record_v5_lifecycle_traceability.json`
- `tests/fixtures/workspaces/productos-sample/artifacts/release_readiness_v5_lifecycle_traceability.json`
- `tests/fixtures/workspaces/productos-sample/artifacts/release_gate_decision_v5_lifecycle_traceability.json`
- `tests/fixtures/workspaces/productos-sample/artifacts/ralph_loop_state_v5_lifecycle_traceability.json`
- `tests/fixtures/workspaces/productos-sample/docs/planning/v5-candidate-note.md`
- `tests/fixtures/workspaces/productos-sample/docs/planning/v5-cutover-plan.md`
- `tests/fixtures/workspaces/productos-sample/docs/planning/v5-repo-cleanup-checklist.md`
- `registry/improvements/`
- `registry/releases/release_0_1_0.json`
- `registry/releases/release_0_2_0.json`
- `registry/releases/release_0_2_1.json`
- `registry/releases/release_2_0_0.json`
- `registry/releases/release_4_1_0.json`
- `registry/releases/release_4_2_0.json`
- `registry/releases/release_4_3_0.json`
- `registry/releases/release_4_4_0.json`
- `registry/releases/release_4_5_0.json`
- `registry/releases/release_4_6_0.json`
- `registry/releases/release_4_7_0.json`
- `registry/releases/release_5_0_0.json`
- `scripts/build_next_version_bundle.py`
- `scripts/build_v5_lifecycle_bundle.py`
- `tests/test_next_version_assets.py`
- `tests/test_next_version_execution.py`
- `tests/test_standalone_v2.py`
- `tests/test_v5_lifecycle_bundle.py`
- `tests/test_v5_release_assets.py`

## Transitional Runtime Blockers

Some older-looking runtime files still remain in the included `core/python/` surface because the current CLI imports them directly.

These are transitional blockers, not active PM-facing version lines:

- `core/python/productos_runtime/next_version.py`
- `core/python/productos_runtime/v5.py`
- `core/python/productos_runtime/v4.py`
- `core/python/productos_runtime/baseline.py`
- `core/python/productos_runtime/cutover.py`

Today, removing those files without first simplifying the CLI would break the current shipped runtime.

## Export Command

Use the repo-local exporter to build the clean public tree:

`./scripts/export_v6_public_repo.sh /path/to/ProductOS-V6`

The exported repo expects Python `3.10+` for `scripts/productos.py`, `./productos`, and `scripts/validate_artifacts.py`.

## Practical Rule

If the goal is to publish now:

1. publish a clean V6-only repo root built from the include list above
2. keep `templates/` as the only PM-facing workspace
3. keep the trimmed `tests/fixtures/workspaces/productos-sample/` maintenance slice so the shipped CLI and V6 tests still work
4. keep older runtime modules only where the current CLI still depends on them
5. do not publish historical archive, explicit V5 release files, or older release-history files

## Follow-Up Cleanup

To make the repo fully V6-native without transitional legacy runtime files, do this next:

1. remove V5 commands and V5 cutover paths from `scripts/productos.py`
2. remove `next_version` bundle dependencies from the current CLI surface
3. shrink `core/python/productos_runtime/__init__.py` to the V6 runtime surface
4. then delete obsolete runtime modules and their tests
