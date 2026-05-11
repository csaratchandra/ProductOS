# Current ProductOS Plan

Status: active
Audience: PM, engineering, design, leadership
Owner: ProductOS PM
Updated At: 2026-05-12

## Active Plan

The active ProductOS plan is **PM Takeover Command Center**.

This plan treats the next ProductOS superpower as a takeover-first system for a PM inheriting an existing product, not as a generic PM OS expansion. The goal is that a new PM can import an existing product repo or workspace and quickly understand the old problem space, segment, persona, competitors, customer journey, product flows, roadmap state, evidence gaps, and next actions.

Ralph status for this plan: `inspect` is complete enough to implement. The repo already has strong building blocks across adoption, research, journey, visual, doc, and control-plane surfaces. The main gap is orchestration into one takeover flow, plus live external research depth and visual product understanding from screenshots and UI evidence.

## Current Baseline Assessment

Use two ratings for the current repo:

- `maturity`: how baked-in the feature is now
- `takeover value`: how much it helps a PM inherit an old product

| Feature | Maturity | Takeover Value | Notes |
|---|---:|---:|---|
| Workspace adoption / import | 5/5 | 5/5 | `import` and `adopt-workspace` already create a traceable adopted workspace, review queue, thread-review bundle, readable docs, and downstream discover/align compatibility. |
| Inbox ingestion and provenance | 4/5 | 4/5 | The repo has a clear inbox and normalization model, which is critical for messy takeover material. |
| Messy input to discover/PRD synthesis | 5/5 | 4/5 | The repo’s own scorecard treats this as superpower-grade, but it is stronger on synthesis than on full historical-product takeover. |
| Research planning and refresh | 4/5 | 5/5 | `plan-research`, `research-workspace`, `discover-research-sources`, and `run-research-loop` already map directly to takeover work. |
| Competitor, market, and customer intelligence | 4/5 | 5/5 | ProductOS already generates `competitor_dossier`, `customer_pulse`, `market_analysis_brief`, `landscape_matrix`, and related research outputs. |
| Segment and persona mapping | 4/5 | 5/5 | `segment_map` and `persona_pack` are already part of the artifact model and seeded/tested flows. |
| Customer journey and screen-flow visuals | 4/5 | 5/5 | Journey synthesis, HTML journey rendering, and screen-flow generation are already implemented and tested. |
| Living docs and rendered human-readable outputs | 4/5 | 5/5 | ProductOS already renders readable docs from structured truth, which is necessary for a takeover handoff. |
| Visual communication lanes | 4/5 | 4/5 | Deck, corridor, and map exports exist, but they are not yet unified around takeover understanding. |
| Prototype and story-map surfaces | 4/5 | 4/5 | Useful for grasping workflows and user paths, but not yet clearly framed as a takeover-first surface. |
| Cockpit, review, traceability, and lifecycle control | 4/5 | 4/5 | Strong governance and review posture already exist. |
| Feature scorecards, improvement loop, Ralph loop | 4/5 | 3/5 | Essential for hardening the superpower, but indirect for a PM’s first-day understanding. |
| Agent-context and adapter surfaces | 3/5 | 3/5 | Helpful for execution, but not the first bottleneck for takeover. |

Overall assessment: ProductOS already has most of the ingredients. The missing leap is a single takeover-oriented orchestration layer that turns those ingredients into one obvious PM command center.

## Implementation Changes

- Add a new top-level orchestration command: `./productos takeover --source <path> --dest <path> --workspace-id <id> --name <name> --mode research --live-research`.
- Make `takeover` wrap the existing adoption flow first, then run research planning, external research refresh, discover synthesis, doc rendering, and visual rendering in one bounded pipeline.
- Add a new render target: `./productos render takeover-atlas --workspace-dir <path>`.
- Emit one takeover-first HTML surface that links product overview, problem space, segments, personas, competitors, market, customer journey, key screens, roadmap state, and open gaps.
- Add four new first-class artifacts: `takeover_brief.json`, `problem_space_map.json`, `roadmap_recovery_brief.json`, and `visual_product_atlas.json`.
- Define `takeover_brief` as the executive synthesis for an inheriting PM: what the product is, who it serves, why it exists, what changed over time, where the evidence is weak, and what the PM should do in the first 30/60/90 days.
- Define `problem_space_map` as a linked graph from problems to segments, personas, workflows, evidence, competitors, and current product bets so historical reasoning is visible instead of scattered across artifacts.
- Define `roadmap_recovery_brief` as the now/next/later recovery surface derived from current artifacts such as `increment_plan`, `program_increment_state`, `decision_queue`, open PRD scope, and unresolved evidence gaps.
- Define `visual_product_atlas` as the normalized visual index for screenshots, UI evidence, journey stages, screen-flow nodes, and linked product workflows.
- Extend the current inbox normalization path so images and screenshots become structured visual evidence records with provenance, screen purpose, probable workflow stage, and linked artifact refs.
- Treat visual evidence as a first-class input into journey synthesis and screen-flow generation, not just an attachment sitting in inbox storage.
- Harden the live external research path around the existing `plan-research`, `discover-research-sources`, and `run-research-loop` surfaces instead of inventing a second research system.
- Keep live research gated by freshness, contradiction detection, source provenance, and explicit PM review. The next slice should support live refresh, but not claim unattended truth without review.
- Generate a dedicated `takeover_feature_scorecard.json` using the existing five ProductOS scoring dimensions, but with takeover-specific scenarios instead of generic discover scenarios.
- Add a takeover-focused cockpit section that highlights imported source coverage, unresolved evidence gaps, competitor freshness, segment/persona confidence, journey completeness, roadmap confidence, and required PM review actions.

## Test Plan

- Add a full fixture-driven test where `takeover` imports an existing repo or workspace containing docs, issue exports, screenshots, and a live-research manifest, then asserts that all takeover artifacts are produced.
- Add tests proving `takeover_brief` contains product summary, old problem framing, target segment, target persona, competitor summary, customer journey summary, roadmap summary, evidence gaps, and first PM actions.
- Add tests proving `problem_space_map` links problems to segments, personas, workflows, artifacts, and evidence refs without orphan nodes.
- Add tests proving screenshot and image ingestion creates normalized visual evidence records and that those records are linked into `visual_product_atlas`.
- Add tests proving live external research refresh updates competitor and market artifacts, preserves provenance, marks stale or contradictory evidence, and does not silently promote weak claims.
- Add tests proving `render takeover-atlas` outputs HTML containing product overview, competitor and market section, persona and segment section, customer journey section, key screens, roadmap section, and explicit open questions.
- Add tests proving takeover artifacts participate in living-system propagation so a change in persona, competitor, or PRD state queues the right downstream updates.
- Add a takeover-specific Ralph validation pass that ends with one explicit decision: `proceed`, `revise`, `defer`, or `block`.

## Assumptions And Defaults

- The plan optimizes for existing-product takeover first, not general PM autonomy.
- The next slice is allowed to cross today’s narrower bounded claim by planning live external research integration, but rollout must remain review-gated and evidence-backed.
- Existing artifacts such as `competitor_dossier`, `market_analysis_brief`, `customer_pulse`, `persona_pack`, `segment_map`, `customer_journey_map`, and rendered docs remain the foundation. The new takeover surfaces should compose them rather than replace them.
- The smallest coherent slice is one orchestrated takeover flow plus four synthesis artifacts plus one unified visual atlas, not a wholesale rewrite of ProductOS.
- Success means a new PM can answer, from one repo-backed workspace, these questions within the first session: what problem this product solves, for whom, against what alternatives, along which journey, with which current roadmap posture, and with which unresolved evidence gaps.

## Why This File Exists

This file is the canonical starting point for the active takeover-superpower plan so another thread can pick it up directly without reconstructing the intent from chat history.
