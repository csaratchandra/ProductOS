# Changelog

## Upcoming V14.0.0

ProductOS V14.0 introduces the intent-driven architecture runtime: one natural-language command that decomposes intent, synthesizes a cross-linked architecture, validates consistency, analyzes gaps, simulates bottlenecks, applies domain intelligence, and exports a PM-ready output bundle.

### Added

- `productos architect` with `--dry-run`, `--wizard`, and `--auto` execution modes
- V14 intent, architecture, gap, simulation, domain, and exporter runtimes
- V14 artifact schemas, examples, skills, and dedicated test coverage
- domain activation, enrichment, and compliance reporting in the architect pipeline
- PDF executive summary output plus explicit architecture-sidecar JSON outputs

### Changed

- architecture synthesis now builds the independent artifact groups concurrently
- cross-layer links now stay within the registered artifact graph used by consistency and gap analysis
- README and bounded-claim surfaces now separate the promoted stable line from the in-repo V14 candidate posture until release

### Validation

- `pytest tests/test_v14_*.py`
- `pytest -q`

---

## Upcoming V13.0.0

ProductOS V13 makes product inheritance a first-class PM flow through multi-modal takeover understanding, visual atlas synthesis, agent-native spec exports, and portfolio intelligence.

### Added

- V13 takeover, atlas, ingestion, spec-chain, export, and portfolio intelligence surfaces
- V13 bounded claim and release-note documentation

### Validation

- `pytest tests/test_v13_*.py`
- `pytest -q`

## V12.0.0

ProductOS V12 completes the repo-backed V11 Living Product System and adds the missing V12 agent-native execution surfaces: one-command workspace generation, cockpit HTML and quality snapshots, prototype generation, adapter context packs, installable packaging, demo flow, and example workspaces.

### Added

- `productos new` now creates 8+ starter artifacts, renders `cockpit.html`, and writes a machine-readable quality snapshot.
- `components/prototype/` now ships a standalone prototype HTML generator, story map HTML, and `prototype_quality_report`.
- `core/agents/adapters/shared/`, `core/agents/adapters/codex/`, and `core/agents/adapters/opencode/` now provide repo-backed adapter context definitions.
- `productos agent-context --target codex|opencode` emits agent-optimized context packs and runtime adapter registry data.
- `core/python/productos_runtime/skill_executor.py` and dedicated decision/content runtime entrypoints now exist for named V12 launch skills.
- `render docs`, `render prototype`, `export artifact --artifact ... --format ...`, and `demo` CLI surfaces are now available.
- `pyproject.toml` exposes installable `productos` packaging metadata.
- `examples/workspaces/` now contains 10 lightweight showcase workspace starters.
- `prd_boundary_report.schema.json`, `tests/test_v10_prd_scope_boundary_check.py`, and `tests/test_v10_drift_and_impact_propagation.py` close the missing proof gaps called out by the V11/V12 audit.

### Changed

- Living-system queue review now persists queue state by default, syncs cockpit living updates, writes rollback `.prev.json` backups, and records rejection feedback.
- `run discover` now auto-synthesizes the connected journey, screen-flow, and prototype pipeline when workspace data is available.
- `run-research-loop` now auto-builds downstream regeneration queues and cockpit notifications when refreshed research artifacts imply living-system work.

### Validation

- `pytest -q`
- `pytest tests/test_v10_prd_scope_boundary_check.py tests/test_v10_drift_and_impact_propagation.py tests/test_v12_agent_native_core.py tests/test_v12_prototype_engine.py`

---

## Upcoming V11.0.0

ProductOS V11 transforms static artifacts into a Living Product System: auto-propagating changes, self-rendering readable documents, PM delta review lanes, and format-agnostic exports.

### Added

- **Auto-Propagation Engine** (`core/python/productos_runtime/living_system.py`)
  - `build_regeneration_queue()`: Builds regeneration queues from trigger events
  - `classify_impact()`: Classifies changes as mechanical / content_deep / structural
  - `process_regeneration_item()`: Auto-executes mechanical changes, queues content-deep for PM review
  - `detect_circular_dependencies()`: Detects and blocks circular dependencies in artifact graphs
  - `generate_delta_preview()`: Human-readable delta descriptions for every queued item
- **Living Markdown Renderer** (`core/python/productos_runtime/markdown_renderer.py`)
  - `render_living_document()`: Renders readable docs from structured artifacts + Jinja2 templates
  - `preserve_annotations()`: Preserves PM manual annotations across re-renders
  - `resolve_source_artifacts()`: Loads all source artifacts referenced by a document
  - Templates: `prd.md.jinja2`, `problem-brief.md.jinja2`, `strategy-brief.md.jinja2`, `user-journey.md.jinja2`
- **Export Pipeline** (`core/python/productos_runtime/export_pipeline.py`)
  - `export_artifact()`: Renders artifacts to any format: markdown, deck, agent_brief, stakeholder_update, battle_card, one_pager
  - Agent-optimized briefs with explicit out_of_scope and executable acceptance criteria
  - Stakeholder update format for executive summaries
- **New Schemas**
  - `regeneration_queue.schema.json`: Orchestrates artifact regeneration with queued items, dependency sequences, and PM approval tracking
  - `pm_note_delta_proposal.schema.json`: Structured delta proposals from unstructured PM inputs
- **Extended Schemas**
  - `document_sync_state.schema.json`: Added `auto_render_enabled`, `template_ref`, `last_rendered_at`, `render_trigger`
  - `cockpit_state.schema.json`: Added `living_updates_queue` panel for PM delta review
- **New Skills** (V10 12-element standard)
  - `regeneration_queue_management`: Orchestrates artifact regeneration after source changes
  - `living_document_rendering`: Renders narrative-first, evidence-backed living documents
  - `pm_note_ingestion`: Transforms PM notes into structured delta proposals
  - `export_pipeline`: Renders artifacts to any format on demand
- **Enhanced Skills**
  - `prd_scope_boundary_check`: Completed to full 12-element contract with boundary scoring (1-10), gold standard criteria, and maturity band variations
  - `drift_and_impact_propagation`: Added `regeneration_mode` classification (mechanical/content_deep/structural) with auto-execution and PM review hooks
- **V11 CLI Commands**
  - `./productos queue build --source-artifact ... --change-summary ...`: Build regeneration queue from trigger event
  - `./productos queue review --item-id ... --action approve|reject|modify`: Process queued regeneration items
  - `./productos render doc --doc-key prd|problem-brief|strategy-brief|user-journey`: Render living document
  - `./productos review-delta --update-id ... --action approve|reject|modify --pm-note ...`: PM delta review lane
- **Tests**
  - `tests/test_v11_living_system.py`: Comprehensive tests for regeneration queue, markdown renderer, export pipeline, and schema validation

### Changed

- V11 implementation slice added without changing the current stable release line
- Readable documents (`docs/*.md`) are now render targets, not manually edited files
- Mechanical artifact changes auto-execute without PM intervention
- Content-deep changes always require explicit PM approval via delta review lane
- All artifact updates are traceable through `regeneration_queue` and `document_sync_state` logs

### Validation

- `python3 scripts/productos.py queue build --help`
- `python3 scripts/productos.py render doc --help`
- `pytest tests/test_v11_living_system.py`
- `./productos --workspace-dir /path/to/workspace queue build --source-artifact artifacts/prd.json`

---

## Upcoming V10.1.0

ProductOS V10.1.0 narrows the Day-1 PM experience around a simpler startup path instead of a flag-heavy CLI contract.

### Added

- guided `./productos start` flow for first-time PM setup
- two Day-1 setup paths: start a new workspace or bring existing work into ProductOS
- beginner `Startup` and `Enterprise` mode selection in the guided flow
- first-win deliverable selection that maps to initial mission defaults
- guided import path routed through the existing workspace adoption engine
- CLI tests covering guided new-workspace setup and guided import setup

### Changed

- `./productos start` no longer requires all workspace and mission flags up front
- guided startup now derives `workspace_id`, mode-aligned `maturity_band`, and initial mission defaults automatically
- PM-facing setup language now centers on the first deliverable to create instead of `success_metric = time to reviewable PRD`
- public onboarding docs now lead with `./productos start` and move flag-heavy commands into advanced usage

### Validation

- `python3 scripts/productos.py start --help`
- `pytest tests/test_productos_cli.py`

## V10.0.0 — 2026-05-03

ProductOS V10 transforms PMs from manual compilers into strategic decision-makers with autonomous, living, world-class AI capabilities.

### Added

- 36 new artifact schemas across Intelligence, Discovery, Decision, Roadmap, Prototype, Marketing, Investor, Stakeholder, and Living System layers
- Autonomous PESTLE environmental analysis (6 factors, 3-horizon projections, spider chart)
- Competitive Intelligence Engine: continuous radar scanning 19+ surfaces, structured alerts, auto-updating feature matrix
- Full-depth persona system: 12+ dimensional profiles, empathy maps, narrative cards, voice samples, decision journeys
- Complete customer and user journey mapping (11 stages, emotion curves, accessibility, screen-level flows)
- Decision Intelligence: trade-off analysis, decision trees, sensitivity analysis, premortems, reversibility scoring
- Pricing Intelligence: competitor matrix, WTP synthesis, pricing model options, unit economics
- Hypothesis Portfolio Management: tree decomposition, kill criteria, risk prioritization, auto-route to prototypes
- 3-variant AI prototype generation: interactive HTML with visual/interaction/IA differentiation, WCAG accessibility
- Developer Handoff Pack: PRD + INVEST stories + ACs + API contracts + NFRs + story maps + dependency graphs
- Full marketing content pack: messaging house, battle cards, blog briefs, email sequences, investor pitch deck + memo
- Stakeholder Management: power/interest maps, objection playbooks, meeting briefs, alignment dashboards
- Living System: freshness monitoring, drift detection, auto-refresh triggers, impact propagation
- Product Health Dashboard: single-surface product universe with autonomous alerts and top-5 recommended actions
- Autonomous Review Gates: composite f(confidence, impact, maturity) — auto-publish or PM review routing
- Gold Standard Validation: per-artifact excellence criteria against named external frameworks (McKinsey, NN/g, Forrester, etc.)
- 12-element skill contract standard applied to 36 skills (purpose, trigger, prerequisites, inputs, steps, outputs, guardrails, gold standard, examples, cross-refs, maturity bands, validation)
- OpenCode adapter parity: full support alongside Codex, Claude, Windsurf, and Antigravity
- Structured feedback capture with downstream auto-trace and regeneration
- Maturity band intelligence: adaptive behavior across 0→1, 1→10, 10→100, 100→10K+ product stages

### Changed

- Baseline version promoted to 10.0.0
- Skill system upgraded from 7-element V9 format to 12-element V10 depth
- Discovery artifacts enriched to exceptional depth across all phases

## V7.0.0 - 2026-04-08

ProductOS V7.0.0 promotes lifecycle traceability through `outcome_review`.

### Added

- `./productos v7` for the promoted V7 lifecycle bundle
- public V7 cutover planning support
- starter-template `release_note` and `outcome_review` artifacts
- starter-template launch and outcome review documentation
- public V7 lifecycle bundle tests

### Changed

- the stable ProductOS line is now `V7.0.0`
- the promoted lifecycle claim now extends from `release_readiness` through `launch_preparation` and `outcome_review`
- public examples and runtime evidence refs now use generic workspace-relative paths instead of assuming a tracked private workspace checkout
- workspace-bound CLI commands now require `--workspace-dir` when no explicit workspace is selected

### Validation

- `python3 scripts/validate_artifacts.py`
- `pytest -q`

### Upgrade Notes

- use `templates/` as the supported public adoption surface
- keep product-specific work outside shared repo surfaces and promote only reusable repo assets
- pass `--workspace-dir` explicitly when running workspace-bound CLI commands from a checkout without a selected workspace
