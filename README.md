# ProductOS

ProductOS V10.0.0 is the current stable ProductOS Core line.

> The repo includes an in-progress V11 **Living Product System** slice: auto-propagating artifact changes, living markdown documents rendered from structured truth, PM delta review lanes, and format-agnostic export pipelines. See `core/docs/v11-living-system-execution-plan.md` for the implementation architecture.

ProductOS is distributed under the Apache License 2.0. Forks, improvements, and
suggestions are welcome through issues and pull requests.

This repository contains:

- `core/`: reusable ProductOS capabilities such as schemas, workflows, agent contracts, and rubrics
- `components/workflow_corridor/`: HTML-first workflow corridor lane for customer-safe public workflow pages
- `components/presentation/`: deck lane for internal/executive HTML presentations and PPT export
- `templates/`: the starter surface for creating a new product workspace
- `tests/fixtures/`: bundled regression fixtures, including the sample workspace used by CLI and runtime tests
- `registry/`: release, workspace, suite, and improvement records
- `workspaces/`: reserved for real product workspaces and intentionally empty in the shared repo

For PM adoption on a new product, the canonical starting surface is [templates](/Users/sarat/Documents/code/ProductOS/templates).

## Operating Model

ProductOS V10.0.0 is organized around the PM lifecycle plus governed research, decision, and living-system loops:

The current stable line remains V10.0.0. The repo also contains the in-progress V11 Living Product System slice: auto-propagation of artifact changes through dependency graphs, living markdown documents rendered from structured truth, PM delta review lanes with approve/reject/modify actions, and format-agnostic export pipelines (agent briefs, stakeholder updates, battle cards, decks).

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

See [vendor-neutral-agent-harness-standard.md](core/docs/vendor-neutral-agent-harness-standard.md) for the tool-agnostic agent operating standard, [ralph-loop-model.md](core/docs/ralph-loop-model.md) for the inspect, implement, refine, validate, fix, and revalidate quality loop, and [autonomous-pm-swarm-model.md](core/docs/autonomous-pm-swarm-model.md) for the internal governed swarm extension path.

## PM Adoption

If you want to use ProductOS for a new product or feature:

1. clone this repo
2. use Python `3.10+`
3. initialize a new workspace from `templates/`
4. treat that new workspace as your product-specific operating surface
5. keep `workspaces/` for product-specific folders only if you intentionally store them in this repo

Recommended command:

`./productos start`

The guided `start` flow keeps day-1 choices small:

- `Start a new workspace`
- `Bring existing work into ProductOS`

For a new workspace, ProductOS asks for:

- the workspace name
- where to create it
- `Startup` or `Enterprise`
- what you want ProductOS to help you create first

ProductOS then fills the first mission defaults and recommends the next command.

Recommended next step:

- `./productos --workspace-dir /path/to/new-workspace run discover`

V11 Living System commands:

- `./productos --workspace-dir /path/to/workspace queue build --source-artifact artifacts/prd.json --change-summary "Scope tightened"`
- `./productos --workspace-dir /path/to/workspace queue review --item-id rq_item_001 --action approve`
- `./productos --workspace-dir /path/to/workspace render doc --doc-key prd`
- `./productos --workspace-dir /path/to/workspace review-delta --update-id lu_001 --action approve --pm-note "Looks correct"`

Advanced startup commands:

- `./productos start --non-interactive --dest /path/to/new-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode startup --title "Your mission" --customer-problem "Customer problem" --business-goal "Business goal"`
- `./productos start --kind import --non-interactive --source /path/to/existing-product-folder --dest /path/to/adopted-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode enterprise`
- `./productos init-workspace --dest /path/to/new-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode startup`
- `./productos --workspace-dir /path/to/new-workspace init-mission --title "Your mission" --target-user "Product manager" --customer-problem "Customer problem" --business-goal "Business goal" --success-metric "time to reviewable PM package"`
- `./productos --workspace-dir /path/to/new-workspace phase plan validation`
- `./productos --workspace-dir /path/to/new-workspace cockpit build`
- `./productos portfolio build --workspace /path/to/workspace-a --workspace /path/to/workspace-b --suite-id suite_pm_superpowers`

Canonical visual export commands:

- `./productos visual export deck components/presentation/examples/artifacts/presentation_brief.example.json`
- `./productos visual export corridor core/examples/artifacts/workflow_corridor_spec.example.json`
- `./productos visual export map core/examples/artifacts/visual_map_spec.example.json`

Visual studio workflow:

- `./productos visual plan deck components/presentation/examples/artifacts/presentation_brief.example.json`
- `./productos visual build /tmp/path/to.visual-direction-plan.json`
- `./productos visual review /tmp/path/to/output-dir`

For an existing product workspace, start with:

`./productos start`

If you want the lower-level adoption command directly:

`./productos import --source /path/to/existing-product-folder --dest /path/to/adopted-workspace --workspace-id ws_your_product --name "Your Product Workspace" --mode research --emit-report --emit-thread-page`

The repo also accepts the entrypoint names `./ProductOS`, `./productOS`, and `./PRODUCTOS`.

The mission, phase, cockpit, and portfolio surfaces are bounded PM control-plane helpers. They improve repo-native reviewability and coordination, but they do not broaden the public `V10.0.0` claim boundary on their own.

## Validation And Testing

Validation and tests are intentionally local and simple:

- `./validate-artifacts`
- `pytest`
- `pytest tests/test_v11_living_system.py`
- `./productos visual export deck components/presentation/examples/artifacts/presentation_brief.example.json`
- `./productos visual export corridor core/examples/artifacts/workflow_corridor_spec.example.json`
- `./productos visual export map core/examples/artifacts/visual_map_spec.example.json`
- `./productos v6 --output-dir /tmp/productos-v6-lifecycle`
- `./productos v7 --output-dir /tmp/productos-v7-lifecycle`
- `./productos v9 --output-dir /tmp/productos-v9-lifecycle`
- `./productos --workspace-dir /path/to/workspace queue build --source-artifact artifacts/prd.json`

The shell entrypoints select a Python `3.10+` interpreter automatically when one is available on `PATH`.

These checks verify that:

- artifact examples match schemas
- entity examples match schemas
- key invalid fixtures fail as expected
- ProductOS remains standalone from V1 runtime paths
- latest stable release assets remain present

## Release Ops

Use the public release operator when a bounded feature slice is ready to become the next stable ProductOS line:

`./productos release --slice-label "public release operator slice" --push`

This flow updates tracked public release surfaces, commits them, tags the release commit, and pushes branch plus tag in order. It intentionally excludes `workspaces/` from the release commit.

For approved agent tools, start with [AGENTS.md](/Users/sarat/Documents/code/ProductOS/AGENTS.md) before deeper repo docs.

## Standalone Rule

ProductOS may use V1 as historical reference material, but current runtime files, validation, and examples must not depend on V1 paths or imports.
