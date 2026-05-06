# Product Workspace Starter Guide

Purpose: Explain how to use the ProductOS starter template for a normal product workspace.

## Choose The Right Workspace

- use `templates/` when you want a clean starting point for another product workspace
- keep ProductOS sample fixtures and release records separate from PM product workspaces

## Starter Workspace Contents

The starter workspace includes:

- `inbox/` for raw notes, transcripts, screenshots, docs, spreadsheets, and support exports
- `artifacts/` for normalized operating artifacts
- `handoffs/` for execution context and markdown handoff material
- `feedback/` for product-specific feedback inputs
- `workspace_manifest.yaml` wired to the minimum discovery, delivery, launch, and inbox-ingestion workflows
- one canonical lifecycle item that demonstrates the bounded V6 trace through `release_readiness`
- lifecycle snapshots for `discovery`, `delivery`, `launch`, `outcomes`, and `full_lifecycle`
- starter delivery artifacts such as `story_pack`, `acceptance_criteria_set`, and `release_readiness`

## Recommended Start Path

1. Clone the repo.
2. Run `./productos start`.
3. Choose either `Start a new workspace` or `Bring existing work into ProductOS`.
4. If you start a new workspace, choose `Startup` or `Enterprise`, then choose what you want ProductOS to help you create first.
5. Replace the seeded starter artifacts with your product evidence as it becomes available.
6. Keep ProductOS Core in `core/` and treat the new workspace as the place where product reality lives.

## What PMs Should Reuse

PMs should reuse:

- the workspace structure
- the starter artifact shapes
- the lifecycle trace model
- the CLI entry points
- the readable-doc and review workflow patterns

PMs should not reuse:

- ProductOS sample-workspace backlog history
- ProductOS release records
- ProductOS internal feedback logs
- ProductOS-specific discovery claims as if they were their own product evidence

## Minimum PM Workflow

For a new product or feature, the shortest useful path is:

1. run `./productos start`
2. let the guided flow create the workspace and first mission defaults
3. ingest raw notes and evidence into the new workspace
4. replace starter discovery artifacts with real product artifacts
5. carry one canonical item through the bounded lifecycle trace
6. use readable docs and lifecycle snapshots for review instead of manual reconstruction

## Advanced Commands

Use the lower-level commands only when you need more explicit control:

- `./productos start --non-interactive ...`
- `./productos init-workspace ...`
- `./productos --workspace-dir /path/to/workspace init-mission ...`
- `./productos import ...`

## Distribution Note

If this repo is published for PM use, the starter workspace should be positioned as the download surface.

Do not mix ProductOS sample fixtures or release records with a PM product workspace.

## Rule

Do not repurpose ProductOS sample-fixture artifacts for unrelated products. Use the starter template so ProductOS-as-a-product records do not mix with another product's history.
