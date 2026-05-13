# ProductOS

ProductOS V13.0.0 is the current stable ProductOS Core line.

> ProductOS V12 ships the Living Product System plus agent-native execution surfaces: auto-propagating artifact changes, living markdown documents rendered from structured truth, PM delta review lanes, format-agnostic export pipelines, prototype generation, adapter context packs, packaging, and demo-ready workspace surfaces.

ProductOS is distributed under the Apache License 2.0. Forks, improvements, and
suggestions are welcome through issues and pull requests.

This repository contains:

- `core/`: reusable ProductOS capabilities such as schemas, workflows, agent contracts, and rubrics
- `components/workflow_corridor/`: HTML-first workflow corridor lane for customer-safe public workflow pages
- `components/presentation/`: deck lane for internal/executive HTML presentations and PPT export
- `templates/`: the starter surface for creating a new product workspace
- `tests/fixtures/`: bundled regression fixtures, including the sample workspace used by CLI and runtime tests
- `registry/releases/`: stable release metadata
- `workspaces/`: reserved for real product workspaces and intentionally empty in the shared repo

For PM adoption on a new product, the canonical starting surface is [templates](/Users/sarat/Documents/code/ProductOS/templates).

## Operating Model

ProductOS V13.0.0 is organized around the PM lifecycle plus governed research, decision, living-system, inheritance, and agent-native execution loops:

The current stable line is ProductOS `V13.0.0`. The repo includes the shipped V11/V12 living-system and agent-native execution surfaces plus the V13 inheritance, atlas, spec-pipeline, and portfolio-intelligence surfaces.

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

## V14 Candidate: Intent-Driven Architecture

ProductOS includes an in-repo V14 candidate surface for **intent-driven architecture**. It is implemented and test-backed in the repo, but it is not the current promoted stable line until the V14 release proof is cut.

### `productos architect` Command

```bash
# Full pipeline (candidate auto mode)
./productos architect --intent "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"

# Dry-run: decomposition only, no artifact generation
./productos architect --intent "..." --dry-run

# Wizard mode: step-by-step with confirmation points
./productos architect --intent "..." --wizard

# Specify output directory
./productos architect --intent "..." --output-dir /path/to/outputs
```

### Pipeline Phases

1. **Intent Decomposition** → extracts problem, personas, outcomes, domain, constraints with confidence scores
2. **Architecture Synthesis** → 6 parallel engines generate persona packs, workflows, components, journey maps, API contracts, and zoom navigation
3. **Gap Intelligence** → cross-layer gap detection with narrative impact explanations and fix suggestions
4. **Predictive Simulation** → Monte Carlo simulation with bottleneck ranking and what-if scenarios
5. **Output Bundle** → all 12 formats including JSON artifacts, Markdown PRDs, interactive HTML atlas, PM Briefing

### 12 Output Formats

JSON artifacts | Markdown PRDs | Interactive HTML atlas | Adaptive prototype | Simulation dashboard | Executive summary | Mermaid diagrams | Analytics spec | Outcome cascade | AI layer plan | Experience plan | PM Briefing with confidence

V12 Living System and Agent-Native commands:

- `./productos --workspace-dir /path/to/workspace queue build --source-artifact artifacts/prd.json --change-summary "Scope tightened"`
- `./productos --workspace-dir /path/to/workspace queue review --item-id rq_item_001 --action approve`
- `./productos --workspace-dir /path/to/workspace render doc --doc-key prd`
- `./productos --workspace-dir /path/to/workspace render docs`
- `./productos --workspace-dir /path/to/workspace render prototype --workspace-dir /path/to/workspace`
- `./productos --workspace-dir /path/to/workspace export artifact --artifact artifacts/prd.json --format agent_brief`
- `./productos --workspace-dir /path/to/workspace agent-context --target codex`
- `./productos --workspace-dir /path/to/workspace review-delta --update-id lu_001 --action approve --pm-note "Looks correct"`
- `./productos new "AI-powered inventory forecasting for SMB retailers"`
- `./productos demo --dest /tmp/productos-demo`

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

The mission, phase, cockpit, adapter, prototype, and portfolio surfaces are bounded PM control-plane helpers. They improve repo-native reviewability and coordination, but they do not broaden the public `V12.0.0` claim boundary past the proof in this repo.

## Validation And Testing

Validation and tests are intentionally local and simple:

- `./validate-artifacts`
- `pytest`
- `pytest tests/test_v11_living_system.py`
- `pytest tests/test_v10_prd_scope_boundary_check.py tests/test_v10_drift_and_impact_propagation.py tests/test_v12_agent_native_core.py tests/test_v12_prototype_engine.py`
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

This flow stages only the tracked public release surface, updates stable release metadata, commits the bounded release set, tags the release commit, and pushes branch plus tag in order.

For approved agent tools, start with [AGENTS.md](/Users/sarat/Documents/code/ProductOS/AGENTS.md) before deeper repo docs.

## Standalone Rule

ProductOS may use V1 as historical reference material, but current runtime files, validation, and examples must not depend on V1 paths or imports.
