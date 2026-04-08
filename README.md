# ProductOS

ProductOS V7.1.0 is the current stable ProductOS Core line.

ProductOS is distributed under the Apache License 2.0. Forks, improvements, and
suggestions are welcome through issues and pull requests.

This repository contains:

- `core/`: reusable ProductOS capabilities such as schemas, workflows, agent contracts, and rubrics
- `templates/`: the starter surface for creating a new product workspace
- `registry/`: release, workspace, suite, and improvement records
- `workspaces/`: reserved for real product workspaces and intentionally empty in the shared repo

For PM adoption on a new product, the canonical starting surface is [templates](/Users/sarat/Documents/code/ProductOS/templates).

## Operating Model

ProductOS V7.1.0 is organized around the PM lifecycle plus governed research and improvement loops:

1. current-state assessment
2. discovery
3. prioritization and planning
4. delivery execution
5. launch readiness and release communication
6. post-launch learning
7. ProductOS improvement loop

The separation between ProductOS assets and PM workspaces is strict:

- ProductOS Core defines the operating system
- `templates/` defines the reusable starter surface
- product workspaces define product-specific reality
- core upgrades do not silently rewrite workspace artifacts

See [vendor-neutral-agent-harness-standard.md](core/docs/vendor-neutral-agent-harness-standard.md) for the tool-agnostic agent operating standard and [ralph-loop-model.md](core/docs/ralph-loop-model.md) for the inspect, implement, refine, validate, fix, and revalidate quality loop.

## PM Adoption

If you want to use ProductOS for a new product or feature:

1. clone this repo
2. use Python `3.10+`
3. initialize a new workspace from `templates/`
4. treat that new workspace as your product-specific operating surface
5. keep `workspaces/` for product-specific folders only if you intentionally store them in this repo

Recommended command:

`./productos init-workspace --dest /path/to/new-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode startup`

## Validation And Testing

Validation and tests are intentionally local and simple:

- `./validate-artifacts`
- `pytest`
- `./productos v6 --output-dir /tmp/productos-v6-lifecycle`
- `./productos v7 --output-dir /tmp/productos-v7-lifecycle`

The shell entrypoints select a Python `3.10+` interpreter automatically when one is available on `PATH`.

These checks verify that:

- artifact examples match schemas
- entity examples match schemas
- key invalid fixtures fail as expected
- ProductOS remains standalone from V1 runtime paths
- latest stable release assets remain present

## Standalone Rule

ProductOS may use V1 as historical reference material, but current runtime files, validation, and examples must not depend on V1 paths or imports.
