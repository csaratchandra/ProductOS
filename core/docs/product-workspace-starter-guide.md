# Product Workspace Starter Guide

Purpose: Explain how to use the promoted ProductOS V6 starter workspace for a normal product without copying the self-hosting ProductOS workspace by hand.

## Choose The Right Workspace

- use `workspaces/productos-v2/` when ProductOS itself is the product
- use `workspaces/product-starter/` when you want a clean starting point for another product

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
2. Run `./productos init-workspace --template product-starter --dest /path/to/new-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode startup`.
3. Replace the seeded starter artifacts with your product evidence as it becomes available.
4. Keep ProductOS Core in `core/` and treat the new workspace as the place where product reality lives.

## What PMs Should Reuse

PMs should reuse:

- the workspace structure
- the starter artifact shapes
- the lifecycle trace model
- the CLI entry points
- the readable-doc and review workflow patterns

PMs should not reuse:

- ProductOS self-hosting backlog history
- ProductOS release records
- ProductOS internal feedback logs
- ProductOS-specific discovery claims as if they were their own product evidence

## Minimum PM Workflow

For a new product or feature, the shortest useful path is:

1. initialize a new workspace from `product-starter`
2. ingest raw notes and evidence into the new workspace
3. replace starter discovery artifacts with real product artifacts
4. carry one canonical item through the bounded lifecycle trace
5. use readable docs and lifecycle snapshots for review instead of manual reconstruction

## Distribution Note

If this repo is published for PM use, the starter workspace should be positioned as the download surface.

Do not present `workspaces/productos-v2/` as the starter for external use. That workspace exists for ProductOS self-hosting only.

## Rule

Do not repurpose the self-hosting ProductOS workspace for unrelated products. Use the starter workspace so ProductOS-as-a-product records do not mix with another product's history.
