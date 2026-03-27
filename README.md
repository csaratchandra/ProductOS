# ProductOS

ProductOS V6.0.0 is the current stable ProductOS Core line.

This repository contains:

- `core/`: reusable ProductOS capabilities such as schemas, templates, workflows, agent contracts, and rubrics
- `workspaces/productos-v2/`: the legacy-named self-hosting ProductOS workspace used to build and operate ProductOS itself
- `workspaces/product-starter/`: the clean starter workspace for using ProductOS on another product
- `registry/`: release, workspace, suite, and improvement records

The canonical current-plan entry point is [current-plan.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/planning/current-plan.md).

For PM adoption on a new product, the canonical starting surface is [product-starter](/Users/sarat/Documents/code/ProductOS/workspaces/product-starter).

## Operating Model

ProductOS V6.0.0 is organized around the PM lifecycle plus governed research and improvement loops:

1. current-state assessment
2. discovery
3. prioritization and planning
4. delivery execution
5. launch readiness and release communication
6. post-launch learning
7. ProductOS improvement loop

The separation between `core/` and `workspaces/` is strict:

- ProductOS Core defines the operating system
- Product workspaces define product-specific reality
- core upgrades do not silently rewrite workspace artifacts

See [vendor-neutral-agent-harness-standard.md](core/docs/vendor-neutral-agent-harness-standard.md) for the tool-agnostic agent operating standard and [ralph-loop-model.md](core/docs/ralph-loop-model.md) for the inspect, implement, refine, validate, fix, and revalidate quality loop.

## Self-Hosting Workspace

`workspaces/productos-v2/` is the self-hosting ProductOS workspace for the ProductOS product itself.

It is used to:

- assess current ProductOS state
- run discovery and prioritization workflows
- generate delivery and launch artifacts
- capture post-launch learning
- feed improvements back into ProductOS Core

This self-hosting and self-improvement loop is an internal ProductOS development method.

It is used to dogfood ProductOS while building later versions, but it is not a PM-facing ProductOS feature and should not be treated as external product positioning.

The path name remains `productos-v2` for continuity, even though the active core line is now `6.0.0`.

For non-self-hosting adoption, start from `workspaces/product-starter/` and follow [product-workspace-starter-guide.md](core/docs/product-workspace-starter-guide.md).

## PM Adoption

If you want to use ProductOS for a new product or feature:

1. clone this repo
2. use Python `3.10+`
3. initialize a new workspace from `product-starter`
4. treat that new workspace as your product-specific operating surface
5. leave `workspaces/productos-v2/` for ProductOS self-hosting only

Recommended command:

`./productos init-workspace --template product-starter --dest /path/to/new-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode startup`

## Validation And Testing

Validation and tests are intentionally local and simple:

- `python3 scripts/validate_artifacts.py`
- `pytest`
- `./productos v6 --output-dir /tmp/productos-v6-lifecycle`
- `./productos cutover --output-path workspaces/productos-v2/docs/planning/v6-cutover-plan.md`

If you need the current release plan first, start with [current-plan.md](/Users/sarat/Documents/code/ProductOS/workspaces/productos-v2/docs/planning/current-plan.md).

These checks verify that:

- artifact examples match schemas
- entity examples match schemas
- key invalid fixtures fail as expected
- ProductOS remains standalone from V1 runtime paths
- latest stable release assets remain present

## Standalone Rule

ProductOS may use V1 as historical reference material, but current runtime files, validation, and examples must not depend on V1 paths or imports.
