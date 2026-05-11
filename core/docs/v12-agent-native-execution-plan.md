# ProductOS V12 Agent-Native Execution Plan

**Status**: Approved for implementation  
**Stable Line**: V10.0.0 remains current until V11 passes dogfood validation  
**Target Duration**: 12 weeks  

---

## The Uncomfortable Truth

90 documented skills. 220 schemas. 37 CLI commands. 28 agent contracts. 75 workflows.

**Zero skills have runtime code.** All 90 `SKILL.md` files are beautifully documented contracts that an agent could theoretically follow — but nothing executes them programmatically. The V11 living system has real code but can only handle mechanical changes. Content-deep changes get marked "approved" but the JSON never changes. The markdown renderer uses `str.replace()`, not Jinja2. No prototype HTML is ever generated. No agent adapter — not OpenCode, not Codex, not Claude, not Windsurf, not Antigravity — has a single line of integration code.

**The gap between vision and execution is the entire product.**

This plan closes it in 12 weeks, not 2 years.

---

## The Radical Bet

Every PM tool today is built for humans first. Jira, Linear, Notion, Confluence — all have UIs designed for human eyes and human fingers. Agents scraping them fight HTML, auth, and unstructured data.

ProductOS is the **first PM tool built for agents first**: every artifact is structured JSON with a validated schema. Every operation is a CLI command returning machine-readable output. Git is the system of record — no proprietary database agents can't access.

**The bet**: Agents are becoming the primary consumer of tools. ProductOS is the only PM OS they can genuinely drive. Not scrape. **Drive.**

---

## The Plan at a Glance

| Phase | Weeks | Focus | Ships |
|---|---|---|---|
| **Phase 0: 5-Minute "Wow"** | 1-2 | Single-command workspace creation | `productos new` generates 8+ validated artifacts in <30s |
| **Phase 1: Living System — Actually Living** | 3-5 | Auto-propagation, Jinja2 rendering, content mutation | Change persona → PRD auto-regenerates with evidence footnotes |
| **Phase 2: Prototype + Journey Engine** | 6-7 | Interactive prototypes, journey maps, screen flows | Clickable prototype + visual journey with emotion curves |
| **Phase 3: Agent-Native Core** | 8-9 | OpenCode + Codex adapters, machine-readable CLI | Both agents autonomously run discovery |
| **Phase 4: Decision Intelligence + Launch** | 10-12 | Decision tools, content packs, docs, launch | ProductOS ships as free, agent-native PM OS |

**Post-launch (next iteration)**:
- Windsurf adapter (weeks 13-14, ~2 days with shared core)
- Claude + Antigravity adapters (TBD based on user demand)
- Remaining decision skills graduate from Skill Execution Runtime to dedicated runtimes based on usage data

---

## The 3 Killer Demos (North Star)

1. **"The 5-Minute PM"**: Paste a problem → get PRD + interactive prototype + competitive battle card. One command.
2. **"The Living Brief"**: Change a persona → watch PRD, user journey, and stakeholder update auto-regenerate with evidence footnotes.
3. **"The Autonomous Agent"**: An OpenCode agent initializes a workspace, runs discovery, validates artifacts, fixes errors, and produces a cockpit report — zero human intervention.

---

## Phase 0: The 5-Minute "Wow" (Weeks 1-2)

**Goal**: A PM pastes one problem statement. One command. One minute. Validated workspace with PRD, competitive intel, personas, market analysis, and a cockpit dashboard they can open in a browser. **This is the demo that converts skeptics.**

### Deliverables

1. **`productos new "AI-powered inventory forecasting for SMB retailers"`**
   - LLM-driven population of structured artifact schemas from raw text
   - Generates in one pipeline: `mission_brief.json`, `problem_brief.json`, `concept_brief.json`, `prd.json`, `competitor_dossier.json`, `persona.json`, `market.json`, `cockpit_state.json`
   - Every artifact validated against its JSON schema on generation
   - Renders `cockpit.html` — open in browser, see everything
   - **Time target**: <30 seconds end-to-end

2. **LLM abstraction layer** (`core/python/productos_runtime/llm.py`)
   - Works with OpenAI, Anthropic, Ollama, or any OpenAI-compatible endpoint
   - Prompt templates that map artifact schemas to structured generation instructions
   - Cost tracking per generation
   - Works fully offline with local models — no API key dependency

3. **Quality snapshot dashboard**
   - After generation: schema validation score per artifact (pass/fail with error paths)
   - Completeness score (what fraction of non-optional fields are populated?)
   - Cross-artifact contradiction scan (does PRD conflict with competitor_dossier?)
   - Green/yellow/red indicators — PM instantly knows what's solid vs needs work

### Success Criteria
- `./productos new "Build a tool for remote team async standups"` produces 8+ validated artifacts
- `./productos status` shows a green cockpit with all artifacts passing validation
- A PM who's never seen ProductOS can go from zero to a usable PRD in <5 minutes
- Works with local LLM (no API key required for basic usage)

### Friday Ships
- **Week 1**: `productos new` with schema-validated output for at least mission_brief, problem_brief, prd
- **Week 2**: Full 8-artifact generation, LLM abstraction layer, quality snapshot dashboard

---

## Phase 1: Living System — Actually Living (Weeks 3-5)

**Goal**: Make the V11 living system genuinely work. The code skeleton exists; it needs to actually mutate artifacts on content-deep changes and render professional documents. This is the core differentiator — no other tool regenerates downstream artifacts when upstream data changes.

### Deliverables

1. **Real Jinja2 renderer** — replaces `str.replace()` in `markdown_renderer.py`
   - Conditionals, loops, macros, template inheritance
   - Evidence footnotes with automatic source citation from `source_artifact_ids`
   - Narrative synthesis across artifacts: "Based on persona X's frustration, our PESTLE analysis, and competitive gap A, we recommend B"
   - 6 templates at 150+ lines: PRD, problem-brief, strategy-brief, user-journey, stakeholder-update, leadership-review

2. **Content-deep mutation engine**
   - `process_regeneration_item()` actually mutates target artifact JSON
   - Diff preview shows exactly which JSON fields will change before approval
   - `.prev.json` backup for instant rollback
   - Example: change persona pain point → find PRD's problem statement → update → regenerate downstream → re-validate

3. **Auto-propagation map generator**
   - Analyze schema `$ref` chains and artifact cross-references
   - Generate `impact_propagation_map.json` automatically — no manual maintenance
   - When new schemas added, map regenerates on next `queue build`

4. **Research auto-cascade**
   - `./productos run-research-loop` detects source changes → auto-triggers `queue build`
   - PM gets cockpit notification: "3 artifacts need review — competitor pricing changed"

5. **PM Note Ingestion**
   - Raw text → structured delta proposals with confidence scores
   - PM writes a note → ProductOS suggests which artifacts need updating → queue builds

### Success Criteria
- Change `customer_persona.json` pain point → `queue build` → 3 artifacts queued → approve 2, reject 1 → approved artifacts regenerate with new persona narrative in the PRD
- `./productos render doc --doc-key prd` produces narrative-quality document with evidence footnotes, persona quotes, competitive context, and a narrative arc — not a JSON field dump
- Research refresh → auto-cascade → cockpit shows "2 artifacts need review" without human triggering

### Friday Ships
- **Week 3**: Jinja2 renderer for PRD template, process_regeneration_item mutating content-deep changes
- **Week 4**: Auto-propagation map generator, research auto-cascade wiring
- **Week 5**: All 6 living doc templates, full content-deep mutation with diff preview and rollback

---

## Phase 2: Prototype + Journey Engine (Weeks 6-7)

**Goal**: Ship both the interactive prototype AND rich visual journey artifacts. The flagship superpowers — clickable prototypes and beautiful customer journey maps — that make PMs evangelize the product.

### Deliverables

#### Week 6 — Prototype Engine

1. **`components/prototype/`** — follows the component pattern from presentation and workflow_corridor
   - Input: `prd.json` + `user_journey.json` + `persona.json`
   - Output: standalone `prototype.html` (zero external dependencies)
   - 3-6 screens based on user journey stages
   - 6 state variants per screen (loading, empty, normal, error, edge, onboarding)
   - Responsive CSS: mobile, tablet, desktop breakpoints
   - WCAG 2.1 AA: ARIA labels, keyboard navigation, color contrast
   - Realistic data from persona artifacts (no lorem ipsum)
   - PM annotation overlay (`<!-- PM NOTE: ... -->` survives regeneration)
   - Click-through navigation between all screens

2. **Prototype quality evaluator**
   - Scores 7 dimensions: interaction depth, visual consistency, accessibility, data realism, narrative alignment, responsive behavior, performance
   - Outputs `prototype_quality_report.json` with specific fix suggestions
   - Target: ≥7/10 on all dimensions

3. **Story map generator**
   - Jeff Patton-style story map HTML from features + user stories
   - Color-coded by priority, linked to prototype screens

#### Week 7 — Journey Visuals

4. **Customer journey map visual renderer** (`components/journey_engine/`):
   - **Slice 1 (render-first)**: Reads existing `customer_journey_map.json` → standalone interactive HTML
   - **Visual spec**: 11-stage horizontal scrollable timeline, SVG emotion curve (1–10 scale), color-coded stage bands using ProductOS design tokens (`semantic.error` → frustrated, `semantic.warning` → confused/neutral, `primary.base` → satisfied, `semantic.success` → delighted)
   - **Interactivity**: Click a stage → side panel expands with persona actions, thoughts, touchpoints, channels, pain-point badges (red callouts), drop-off risk gauge, persons involved
   - **Moment-of-truth markers**: Star/diamond icons on critical stages
   - **Opportunity blocks**: Below timeline, linked by `stage_id`, color-coded by effort/impact
   - **Zero external dependencies**: Embedded CSS (Inter/system-ui, 4/8/12/16/24/32 spacing, 8px/12px radii) + vanilla JS
   - **CLI wiring**: `./productos render journey-map --workspace-dir <dir>` emits `outputs/discover/customer_journey_map.html`
   - **Brand compliance**: Follows `design_token_set.schema.json` + `visual-style-system.md` (consultant-grade, story-led, evidence-close-to-claim)

5. **Customer journey synthesis runtime** (Slice 2 — post-render):
   - Input: `persona.json`, `research_brief.json`, `problem_brief.json`, `source_note_card`s
   - LLM-driven stage population with evidence traceability (cites source note cards)
   - Auto-extracts moments of truth, gap analysis, and opportunities
   - Outputs validated `customer_journey_map.json`
   - Integrated with living system: persona change → queue regenerate journey map

6. **User journey screen flow** runtime (expanded):
   - Journey map steps → linked prototype screen diagrams
   - Mermaid flow diagram showing screen → state → transition
   - Each screen node links to actual prototype variant
   - SVG export for embedding in PRDs and decks

7. **Integration**: customer journey → user journey screens → prototype.html — one connected pipeline
   - Change a customer pain point → journey re-renders → screen flow updates → prototype regenerates with new screens
   - This is a sub-demo of the Living System: a PM sees the entire chain update

### Success Criteria
- `./productos render journey-map --workspace-dir <dir>` produces `customer_journey_map.html` with all 11 stages from `customer_journey_map.json`, SVG emotion curve, and clickable stage detail panels
- `./productos run discover` → workspace has `customer_journey.html` (color-coded emotion journey) + `screen_flow.html` (linked to prototype) + `prototype.html` (clickable)
- PM opens journey map, clicks a pain point, jumps to the prototype screen that addresses it
- Prototype quality evaluator scores ≥7/10 on all 7 dimensions for well-formed workspace
- PM annotations (`<!-- PM NOTE: change CTA to "Start free trial" -->`) survive regeneration
- Visual regression test passes: `pytest tests/test_customer_journey_rendering.py` asserts stage count, emotion curve presence, pain-point badge count, and interactivity

### Friday Ships
- **Week 6**: Prototype HTML generator, quality evaluator, story map generator
- **Week 7 — Slice 1**: Customer journey map visual renderer (interactive HTML from existing JSON)
- **Week 7 — Slice 2**: Customer journey synthesis runtime (JSON generation from persona/research) + user journey screen flow with Mermaid diagrams + connected pipeline integration

---

## Phase 3: Agent-Native Core — OpenCode + Codex (Weeks 8-9)

**Goal**: OpenCode and Codex can drive ProductOS autonomously. Machine-readable output for all commands. Skill Execution Runtime makes the remaining documented skills executable.

### Deliverables

1. **Machine-readable JSON output for ALL commands**
   - `--format json` on every command returns structured JSON with typed error codes
   - `{"status": "ok", "data": {...}}` or `{"status": "error", "code": "VALIDATION_FAILED", "errors": [...]}`
   - This single change makes every existing command agent-parseable

2. **Shared adapter core** (`core/agents/adapters/shared/`)
   - Common logic shared across adapters: workspace state queries, command execution, artifact I/O, validation loops
   - Agent-specific layer handles formatting, tool definitions, prompts
   - This architecture makes adding Windsurf (next iteration) a ~2-day task instead of 2 weeks

3. **OpenCode adapter** (`core/agents/adapters/opencode/`)
   - Tool definition file (ProductOS operations as OpenCode-callable tools)
   - `productos agent-context --target opencode` — generates mission context + workspace state as system prompt
   - Conformance test: OpenCode init workspace → run discovery → generate PRD → validate → fix errors → cockpit report

4. **Codex adapter** (`core/agents/adapters/codex/`)
   - Same pattern as OpenCode adapter, formatted for Codex's tool definition format
   - `productos agent-context --target codex` — Codex-optimized context pack
   - Conformance test: identical pass/fail criteria

5. **Skill Execution Runtime** (`core/python/productos_runtime/skill_executor.py`)
   - Reads any fleshed-out `SKILL.md`, parses 12-element contract, executes steps via LLM
   - Validates output against specified schema
   - Converts all 43 fleshed-out skills into "executable" capabilities overnight
   - Skills that prove high demand graduate to dedicated Python runtimes in later phases

### Adapter Roadmap

| Adapter | Status | Target |
|---|---|---|
| OpenCode | Phase 3 (week 8) | Shipped |
| Codex | Phase 3 (week 9) | Shipped |
| Windsurf | Next iteration | Week 13-14 |
| Claude | Later | TBD |
| Antigravity | Later | TBD |

### Success Criteria
- Both OpenCode and Codex pass conformance test suite: autonomous discovery, artifact generation, schema validation, error fixing, cockpit report
- CLI returns valid JSON for every command via `--format json`
- Adding Windsurf post-launch takes <2 days with shared adapter core

### Friday Ships
- **Week 8**: Shared adapter core, OpenCode adapter, machine-readable JSON output for all commands, agent-context generator
- **Week 9**: Codex adapter, Skill Execution Runtime, conformance tests passing for both agents

---

## Phase 4: Decision Intelligence & Launch (Weeks 10-12)

**Goal**: Ship the 8 highest-value decision and content skills with dedicated runtimes. Polish everything. Launch.

### Deliverables

#### Decision Intelligence Runtimes (5 skills)

1. **`prd_scope_boundary_check`**
   - Flags vague language ("should," "maybe," "consider"), checks alignment against problem_brief and strategy_brief
   - Scores PRD boundaries 1-10 with fix suggestions

2. **`trade_off_analysis`**
   - Weighted scoring matrix with stakeholder inputs
   - Visual output as radar chart in HTML

3. **`decision_tree_construction`**
   - Probability-weighted decision trees with expected value computation
   - Tree diagram HTML output

4. **`premortem_analysis`**
   - Failure scenario generation with early warning indicators
   - Report HTML with scenario cards

5. **`battle_card_generation`**
   - Competitor dossier → sales-ready HTML battle cards with win/loss pattern integration

#### Content Pack Generators (3 skills)

6. **`investor_content_generation`**
   - One-pager, pitch memo, demo video script from strategy artifacts

7. **`api_contract_generation`**
   - OpenAPI YAML from PRD acceptance criteria

8. **`stakeholder_management`**
   - Stakeholder map + communication matrix + objection playbooks

#### Launch-Ready Packaging

- `pip install productos` — one command
- 10 example workspaces covering: startup B2B, enterprise B2C, internal tool, marketplace, API product, mobile app, AI feature, platform play, growth experiment, portfolio review
- `./productos demo` — pre-built showcase workspace
- 5-minute getting started guide with GIFs
- 3 killer demo videos (under 3 minutes total)
- FAQ: "How is this different from Jira Product Discovery?" — front and center

### Success Criteria
- `./productos run improve` flags 3+ vague requirements with specific rewrite suggestions
- `./productos visual export deck` produces a leadership deck with competitive positioning and evidence citations
- `./productos demo` wows on first run
- ProductOS ships as free, agent-native PM operating system

### Friday Ships
- **Week 10**: prd_scope_boundary_check + trade_off_analysis + decision_tree_construction runtimes
- **Week 11**: premortem_analysis + battle_card_generation + investor_content + api_contract + stakeholder runtimes
- **Week 12**: Packaging, example workspaces, demo workspace, documentation, launch

---

## The 20 Runtime-Backed Skills

| # | Skill | Phase | Runtime Location | Visual Output |
|---|---|---|---|---|
| 1 | protoytpe_html_generation | 2 | `components/prototype/` | Interactive HTML prototype |
| 2 | prototype_quality_evaluation | 2 | `components/prototype/` | Scorecard JSON + HTML |
| 3 | user_journey_screen_flow | 2 | `components/prototype/` | Mermaid/SVG screen flow diagrams |
| 4 | story_map_generation | 2 | `components/prototype/` | HTML story map |
| 5 | customer_journey_map_visual_renderer | 2 | `components/journey_engine/` | Interactive HTML journey map (11 stages, SVG emotion curve, clickable detail panels) |
| 6 | customer_journey_synthesis | 2 | `core/python/.../journey_synthesis.py` | `customer_journey_map.json` generation from persona/research artifacts |
| 7 | user_journey_screen_flow | 2 | `components/prototype/` | Mermaid/SVG screen flow diagrams |
| 8 | story_map_generation | 2 | `components/prototype/` | HTML story map |
| 9 | living_document_rendering | 1 | `core/python/.../markdown_renderer.py` | Jinja2-rendered markdown |
| 10 | regeneration_queue_management | 1 | `core/python/.../living_system.py` | — |
| 11 | pm_note_ingestion | 1 | `core/python/.../living_system.py` | — |
| 12 | prd_scope_boundary_check | 4 | `core/python/.../` | Boundary report HTML |
| 13 | trade_off_analysis | 4 | `core/python/.../` | Radar chart HTML |
| 14 | decision_tree_construction | 4 | `core/python/.../` | Tree diagram HTML |
| 15 | premortem_analysis | 4 | `core/python/.../` | Failure scenario report HTML |
| 16 | battle_card_generation | 4 | `core/python/.../` | Sales battle card HTML |
| 17 | investor_content_generation | 4 | `core/python/.../` | One-pager + pitch memo HTML |
| 18 | api_contract_generation | 4 | `core/python/.../` | OpenAPI YAML |
| 19 | stakeholder_management | 4 | `core/python/.../` | Stakeholder map HTML |
| 20 | drift_and_impact_propagation | 1 | `core/python/.../living_system.py` | — |
| 6 | living_document_rendering | 1 | `core/python/.../markdown_renderer.py` | Jinja2-rendered markdown |
| 7 | regeneration_queue_management | 1 | `core/python/.../living_system.py` | — |
| 8 | pm_note_ingestion | 1 | `core/python/.../living_system.py` | — |
| 9 | prd_scope_boundary_check | 4 | `core/python/.../` | Boundary report HTML |
| 10 | trade_off_analysis | 4 | `core/python/.../` | Radar chart HTML |
| 11 | decision_tree_construction | 4 | `core/python/.../` | Tree diagram HTML |
| 12 | premortem_analysis | 4 | `core/python/.../` | Failure scenario report HTML |
| 13 | battle_card_generation | 4 | `core/python/.../` | Sales battle card HTML |
| 14 | investor_content_generation | 4 | `core/python/.../` | One-pager + pitch memo HTML |
| 15 | api_contract_generation | 4 | `core/python/.../` | OpenAPI YAML |
| 16 | stakeholder_management | 4 | `core/python/.../` | Stakeholder map HTML |
| 17 | drift_and_impact_propagation | 1 | `core/python/.../living_system.py` | — |

---

## What Gets Cut (Deprecated)

**47 stub skills** → `core/skills/_deferred/` with note: "Community contributions welcome. See CONTRIBUTING.md for how to propose a skill implementation."

**28 fleshed-out skills without dedicated runtimes** → available through Skill Execution Runtime (LLM-executed from their `SKILL.md` contracts). Can graduate to dedicated runtimes when user demand proves it.

Skills deferred include: experiment_design, roadmap_scenario_generation, win_loss_pattern_detection, pricing_analysis_synthesis, pricing_model_design, sensitivity_analysis, weak_signal_detection, competitive_radar_scan, competitive_shift_analysis, empathy_map_generation, freshness_and_staleness_scan, messaging_house_construction, non_functional_requirement_extraction, persona_evidence_synthesis, persona_narrative_generation, pestle_synthesis, one_pager_generation, export_pipeline, help_manual_generation, hypothesis_portfolio_management, market_trend_extrapolation, and others.

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Journey visuals + prototype in 2 weeks is tight | Week 6: prototype engine (reuse presentation component patterns). Week 7: journey visuals (simpler rendering — SVG/HTML, not full interactive UIs like prototypes). The presentation engine's HTML pipeline provides proven rendering patterns. |
| Building 2 adapters + shared core in 2 weeks | OpenCode adapter builds first. Codex adapter reuses 80% of shared core. Week 8 ships OpenCode. Week 9 ships Codex. Shared core amortizes future adapter work to ~2 days each. |
| Windsurf deferred but users want it now | Windsurf ships in next iteration (2 weeks post-launch). The shared adapter core makes it a fast follow, not a re-build. |
| Customer journey without real research data is shallow | Phase 0's LLM layer generates synthetic but schema-valid research data. Journey synthesis works with that. Real research loops enhance it over time. |
| LLM cost for `productos new` is too high for free product | Local Ollama mode for free tier. API mode for quality. Both paths work. PM chooses. |
| Prototype HTML quality is too low for real use | Week 6 ships basic version. Week 7 ships polished. PM feedback loop between Fridays. |
| 47 deprecated stubs anger contributors | They're deferred, not deleted. Available via Skill Execution Runtime. Anyone can propose a dedicated runtime via PR. |
| Competitors ship faster | They can't match repo-first + agent-native architecture. It requires a fundamental rewrite. Our moat is architectural, not feature-count. |

---

## Success Metrics (Measured at Week 12)

- `productos new` completes in <30 seconds, produces ≥8 validated artifacts
- `productos queue build` correctly auto-propagates content-deep changes with diff previews
- `productos render doc --doc-key prd` produces narrative document ≥150 lines with evidence footnotes
- Prototype quality evaluator scores ≥7/10 on all 7 dimensions for well-formed workspace
- OpenCode and Codex adapters pass conformance test: init workspace, run discovery, generate + validate artifacts, fix errors
- Customer journey HTML renders with color-coded emotion curves, pain point callouts, persona quotes, and clickable stage detail panels
- `./productos render journey-map` produces standalone interactive HTML with zero external dependencies
- User journey screen flow links each screen node to its prototype variant
- `productos run improve` detects ≥3 vague requirements in PRD with fix suggestions
- 10 example workspaces cover major PM use cases, each validated against all relevant schemas
- All 38 existing tests stay green through every phase
- 20 new test files added (one per runtime-backed skill + adapter conformance tests)

---

## Competitive Positioning

| | Jira/Linear | Notion/Confluence | ProductOS |
|---|---|---|---|
| **Artifact model** | Proprietary, opaque | Proprietary, flexible | Open schemas, validated JSON |
| **Agent access** | Scrape HTML | Scrape HTML | Read/write structured files |
| **Staleness** | Requirements rot | Documents drift | Living artifacts auto-regenerate |
| **Validation** | None | None | Schema validation on every artifact |
| **Repo integration** | Separate tools | Separate tools | Same git repo as code |
| **Portability** | SaaS lock-in | SaaS lock-in | Files in a folder. Fork it. Own it. |
| **Prototypes** | None | None | Generated from PRDs |
| **Customer journeys** | None | None | Visual journey maps with emotion curves |

**Tagline**: "Requirements shouldn't rot. Artifacts shouldn't drift. PM tools shouldn't trap your data in a silo."

---

## Business Model

**Free** for all individual PMs. Everything in this plan ships as free, open-source capabilities. Monetization considered for future iterations (team features, hosted option) — but not part of this 12-week execution plan.

---

## Guiding Principles

1. **Ruthless prioritization**: 17 skills get runtime. 73 get deferred or served through Skill Execution Runtime.
2. **Agent-native from commit 1**: Every new feature ships with OpenCode tool definitions. Agents are the primary consumer. Humans are the beneficiary.
3. **The 3 Killer Demos drive everything**: Every sprint produces an output that advances at least one demo.
4. **Ship every Friday**: No feature stays in development longer than 5 days without shipping something usable.
5. **Repo-first always**: No SaaS, no cloud, no auth. Everything stays in the filesystem and git.