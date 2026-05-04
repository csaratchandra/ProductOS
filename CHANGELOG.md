# Changelog

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
- public examples and runtime evidence refs now use generic workspace-relative paths instead of assuming a tracked `internal/ProductOS-Next/` checkout
- self-hosting-only CLI commands now require `--workspace-dir` when no private default workspace is present

### Validation

- `python3 scripts/validate_artifacts.py`
- `pytest -q`

### Upgrade Notes

- use `templates/` as the supported public adoption surface
- keep private self-hosting work outside product workspaces and promote only reusable repo surfaces
- pass `--workspace-dir` explicitly when running self-hosting-only CLI commands from a checkout without a private internal workspace
