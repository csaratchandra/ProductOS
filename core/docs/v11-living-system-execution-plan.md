# ProductOS V11: The Living Product System — Execution Plan

**Status:** Approved for implementation  
**Dogfood Workspace:** Private local dogfood workspace  
**Target Release:** v11.0.0 — "The Living Product System"  
**Stable Line:** V10.0.0 remains current until V11 passes dogfood validation  

---

## Vision

**Today**, a PM spends 60% of their time reconciling scattered inputs into structured artifacts — copying research findings into PRDs, updating strategy briefs when competitors move, rewriting user journeys after stakeholder feedback, and manually regenerating presentations before every leadership review.

**With ProductOS V11**, the PM's experience is:

> *"I capture a voice memo after a customer call. ProductOS updates the persona narrative, flags the PRD for a scope delta, regenerates the user journey with the new pain point, and queues the competitive analysis brief for refresh. I open the cockpit, see 4 suggested artifact updates, approve 3, reject 1 with a note. My leadership deck exports from the current living state — never stale. When I'm ready to build, I export an agent-optimized brief from the same truth. No copy-paste. No version drift. No 'which document is current?' "*

That is the superpower. **One source of truth. Auto-propagation. Human approval at the edges.**

---

## Why V11 Is Needed

ProductOS V10 built world-class **individual capabilities**: research, strategy, prototyping, visual export, competitive intelligence. But these capabilities are **static artifacts**. The PM must manually:

1. Copy research findings into the PRD
2. Update the strategy brief when a competitor launches
3. Rewrite the user journey after a persona interview
4. Rebuild the prototype plan when scope changes
5. Regenerate the leadership deck from stale documents

V11 closes this gap with **the living system**: auto-propagation, delta review, and format-agnostic export.

---

## Current Foundation (What V10 Already Has)

After deep inspection of the repo, ProductOS V10 has remarkable infrastructure:

| Artifact / Skill | What It Does | Current Limitation |
|---|---|---|
| `document_sync_state.schema.json` | Tracks readable docs ↔ structured artifact sync, drift status, modification log | Records status but does not **auto-regenerate** markdown when sources change |
| `drift_and_impact_propagation/SKILL.md` | Detects drift, traces downstream dependencies, recommends regeneration sequence | Skill is documented but not **auto-triggered**; PM must manually invoke |
| `competitive_radar_scan/SKILL.md` | Auto-scans competitor surfaces, generates alerts | Downstream cascades are "recommended" not **auto-queued** |
| `external_research_feed_registry.schema.json` + `freshness_scoring` | Tracks research source cadence, staleness | No auto-refresh pipeline; no cascade into artifact regeneration |
| `user_journey_map.schema.json` | Deep per-step interaction specs | Static snapshot; does not auto-update when persona or problem brief changes |
| `prototype_generation_plan.schema.json` + `prototype_html_generation/SKILL.md` | Generates interactive HTML prototypes | Triggered manually; does not auto-reconcile when PRD scope changes |
| `cockpit_state` + `orchestration_state` | PM-visible control surface, route plan, approval queue | No "regeneration queue" visible to PM; no artifact-delta review lane |
| `pm_superpowers.py` | Mission log, phase packets, workspace tree, portfolio rollup | No concept of "artifact change review" or "living document delta" |

**V11 makes these capabilities live.**

---

## The Three New Systems

### 1. The Auto-Propagation Engine

When any source artifact changes (research finding, PM note, competitive alert, stakeholder feedback), ProductOS must:

- Compute the dependency graph (`impact_propagation_map`)
- Classify impact per downstream artifact (mechanical vs. content-deep)
- **Auto-execute** mechanical changes (reference updates, date stamps, version bumps)
- **Queue** content-deep changes for PM review with a delta preview
- Update `document_sync_state` for every affected readable doc

### 2. The Living Markdown Renderer

Readable documents (`docs/planning/prd.md`, `docs/discovery/problem-brief.md`) are **render targets**, not manually edited files. They are generated from structured artifacts + templates + evidence context. The PM edits the **structured artifact** or adds a **note/feedback**; the markdown regenerates automatically.

### 3. The PM Delta Review Lane

The cockpit gains a new review queue: **"Living Artifact Updates"**. The PM sees:

- *"Competitor dossier updated → Strategy brief delta: 3 claims outdated"*
- *"Persona interview added → Journey step 4 cognitive load flagged"*
- *"PRD scope boundary tightened → Prototype plan: 2 new screens required"*

The PM approves, rejects, or modifies each delta. ProductOS learns from rejections to improve future propagation classification.

---

## Architecture Principles

| Principle | Definition |
|---|---|
| **Evidence Traceability** | Every claim in every rendered document links to a source artifact or note |
| **Delta Transparency** | PM can see exactly what changed, why, and what it affects before approving |
| **Reversibility** | Every auto-executed change can be reverted; every PM rejection is recorded |
| **No Silent Drift** | No artifact updates without a corresponding `regeneration_queue` entry and `document_sync_state` log entry |
| **Human at the Edge** | Mechanical changes auto-execute; all content-deep changes require explicit PM approval |
| **Format Agnostic** | Source artifacts are the truth; all formats (markdown, deck, agent brief) are render targets |

---

## Complete Sprint Plan

### Sprint 0: Restore Dogfood Workspace (Week 1)

**Goal:** Reactivate ProductOS's original ethos: the PM building ProductOS uses ProductOS to build ProductOS.

**Background:** ProductOS previously had a private living workspace where ProductOS was used to manage itself. This was removed when restructuring for public release. V11 restores that private dogfood loop locally.

**Tasks:**

1. **Create a private dogfood workspace**
   - Document the dogfood workspace purpose locally
   - Reference the promotion rule: only approved reusable changes promote to `core/`
   - Keep the workspace out of the shared repo

2. **Create the private ProductOS V11 workspace**
   - Initialize from `templates/`
   - Set workspace_id: `ws_productos_v11_dogfood`
   - Set name: "ProductOS V11 Living System"
   - Set mode: `enterprise`

3. **Initialize V11 mission artifacts**
   - `artifacts/mission_brief.json` — V11 mission: "Make ProductOS artifacts live"
   - `artifacts/product_record.json` — lifecycle stage: `discovery`
   - `docs/planning/mission-log.md`
   - `docs/planning/discovery-backlog.md`

4. **Create `inbox/` structure**
   - `inbox/raw-notes/` — PM voice memos, meeting notes
   - `inbox/transcripts/` — Customer call transcripts
   - `inbox/screenshots/` — Competitive intelligence screenshots
   - `inbox/documents/` — Imported research documents

5. **Validate workspace**
   - Run `./productos status --workspace-dir /path/to/private-workspace`
   - Verify cockpit renders correctly
   - Verify workspace_manifest.yaml is complete

**Success Criteria:**
- Private dogfood workspace is a fully functional ProductOS workspace
- `./productos status` shows V11 mission in discovery phase
- Workspace is ready to receive PM notes and trigger auto-propagation in Sprint 5

---

### Sprint 1: Harden Prerequisites (Weeks 2–3)

**Goal:** Make prerequisite skills executable so the auto-propagation engine inherits strong guardrails.

**Task 1.1: Complete `prd_scope_boundary_check` skill**

The skill is currently a stub. Complete to V10 12-element standard:

| Element | Deliverable |
|---|---|
| 1. Purpose | One sentence: validate PRD scope boundaries are strong enough to prevent agent/execution scope creep |
| 2. Trigger | PRD created or updated; prototype generation plan requested; agent brief export requested |
| 3. Prerequisites | PRD artifact exists; `out_of_scope` field populated; linked artifacts available |
| 4. Input Spec | `prd.json`, `problem_brief.json`, `strategy_context_brief.json` |
| 5. Execution Steps | 8 steps: load PRD → check out_of_scope length → check boundary specificity → check upstream alignment → check downstream impact → flag ambiguous boundaries → suggest specific language → emit boundary report |
| 6. Output Spec | `prd_boundary_report` artifact: score (1-10), flagged boundaries, suggested fixes, approval status |
| 7. Guardrails | Boundary too vague ("etc.", "other features") → reject. Missing out_of_scope → block. Boundary contradicts upstream strategy → escalate |
| 8. Gold Standard | Every boundary is specific enough that a builder/agent would know what NOT to build |
| 9. Examples | Excellent (5/5): 8+ specific out-of-scope items with rationale. Poor (2/5): "Other features not in scope" |
| 10. Cross-References | Upstream: `concept_risk_surfacing`. Downstream: `prototype_html_generation`, `agent_context_package_generation` |
| 11. Maturity Band | 0→1: exhaustive boundaries. 1→10: deep boundaries with competitive context. 10→100: standard with API contract linkage |
| 12. Validation | `tests/test_v10_prd_scope_boundary_check.py` |

**Task 1.2: Make `drift_and_impact_propagation` executable**

The skill contract exists but needs executable runtime integration:

1. Add `regeneration_mode` classification to step 5:
   - `mechanical` — reference updates, date stamps, version bumps, link corrections
   - `content_deep` — claims, strategy, scope, positioning changed
   - `structural` — artifact schema or relationships changed

2. Add execution hooks in `living_system.py` (Sprint 2):
   - Mechanical items auto-execute via `process_regeneration_item()`
   - Content-deep items queue in `regeneration_queue.json`
   - Structural items always escalate to PM

3. Add test coverage:
   - `tests/test_v10_drift_and_impact_propagation.py`
   - Test: competitor dossier update → strategy brief auto-queued
   - Test: PRD scope change → prototype plan auto-queued
   - Test: circular dependency → escalation to PM

**Success Criteria:**
- `prd_scope_boundary_check` skill passes 12-element contract test
- `drift_and_impact_propagation` auto-triggers from artifact changes
- `./pytest tests/test_v10_prd_scope_boundary_check.py` passes
- `./pytest tests/test_v10_drift_and_impact_propagation.py` passes

---

### Sprint 2: Auto-Propagation Engine (Weeks 4–5)

**Goal:** Build the core system that makes artifacts live.

**New Schema:** `core/schemas/artifacts/regeneration_queue.schema.json`

```json
{
  "schema_version": "1.0.0",
  "regeneration_queue_id": "rq_ws_myproduct_001",
  "workspace_id": "ws_myproduct",
  "trigger_event": {
    "event_type": "artifact_updated|competitive_alert|pm_note_added|research_fresh|stakeholder_feedback",
    "source_artifact_ref": "...",
    "change_summary": "CompetitorAlpha pricing page changed"
  },
  "queued_items": [
    {
      "item_id": "rq_item_001",
      "target_artifact_ref": "artifacts/competitor_dossier.json",
      "impact_classification": "mechanical|content_deep|structural",
      "regeneration_mode": "auto|pm_review|full_rebuild",
      "status": "pending|auto_executed|approved|rejected|completed",
      "delta_preview": "Pricing table row updated; 3 feature claims need re-verification",
      "pm_note": "",
      "executed_at": "...",
      "execution_log": []
    }
  ],
  "dependency_sequence": ["artifacts/competitor_dossier.json", "artifacts/strategy_context_brief.json", "docs/strategy/competitive-brief.md"],
  "status": "active|paused|completed",
  "pm_review_required": true,
  "auto_executed_count": 0,
  "pm_review_count": 0,
  "generated_at": "..."
}
```

**New Skill:** `core/skills/regeneration_queue_management/SKILL.md` (V10 12-element standard)

**Execution Pattern:**
1. Receive `drift_detection_alert` from `drift_and_impact_propagation`
2. Classify each downstream artifact: mechanical / content-deep / structural
3. Auto-execute mechanical items (reference updates, date stamps, version bumps)
4. Generate delta preview for content-deep items (what specifically changed, what it affects)
5. Order queue by dependency depth (deepest first)
6. Emit `regeneration_queue.json` artifact
7. Update cockpit queue recommendations
8. Log all actions in `document_sync_state`

**New Runtime Module:** `core/python/productos_runtime/living_system.py`

Key functions:
- `build_regeneration_queue(trigger_event, workspace_dir)` → produces `regeneration_queue.json`
- `process_regeneration_item(item, workspace_dir)` → auto-executes mechanical changes
- `classify_impact(source_change, target_artifact)` → returns mechanical/content_deep/structural
- `generate_delta_preview(source_change, target_artifact)` → human-readable diff description

**CLI Extension:**
- `./productos run operate` — extended to process regeneration queue
- `./productos queue review --workspace-dir ... --item-id ... --action approve|reject|modify`

**Guardrails:**
- Circular dependency → block, escalate to PM
- >10 queued items → split into batches with summary
- Critical artifact (PRD, release_readiness) → always `pm_review`
- Content-deep item without delta preview → reject, require refinement

**Test:** `tests/test_v10_regeneration_queue.py`

**Success Criteria:**
- Mechanical changes auto-execute without PM intervention
- Content-deep changes queue with meaningful delta previews
- PM can approve/reject via CLI; rejections are logged for learning
- Cockpit shows queue status
- All changes are traceable in `document_sync_state` modification logs

---

### Sprint 3: Living Markdown Renderer (Weeks 6–7)

**Goal:** Readable documents become render targets, not manually edited files.

**System:** `core/python/productos_runtime/markdown_renderer.py`

**Function:** `render_living_document(doc_key, workspace_dir)`

1. Read `document_sync_state` for the doc_key
2. Load source artifacts referenced in `source_artifact_refs`
3. Load template for doc_key from `core/templates/living_docs/`
4. Render markdown with:
   - Frontmatter: `generated_at`, `source_artifact_refs`, `regeneration_queue_item_id`, `template_version`
   - Evidence traceability: every claim links to source note card or research finding via footnote
   - Modification log: append-only, shows what changed and why
   - PM annotations: callout boxes for manual notes that survive re-rendering
5. Write to `docs/[path]`

**Template Design Principle:**
Templates are **narrative-first, evidence-backed**. They tell the story of the product, not just dump structured data. The PM edits the **structured artifact**; the template renders the **story**.

**New Templates:**

| Template | Source Artifacts | Narrative Focus |
|---|---|---|
| `prd.md.jinja2` | `prd.json` + `problem_brief.json` + `research_notebook.json` + `acceptance_criteria_set.json` | Problem → Solution → Evidence → Scope → What We're NOT Building |
| `problem-brief.md.jinja2` | `problem_brief.json` + `customer_pulse.json` + `persona_narrative_card.json` | Customer Pain → Why Now → Evidence Quotes → Segments Affected |
| `strategy-brief.md.jinja2` | `strategy_context_brief.json` + `competitor_dossier.json` + `landscape_matrix.json` | Market Position → Wedge → Competitive Dynamics → Right to Win |
| `user-journey.md.jinja2` | `user_journey_map.json` + `persona_narrative_card.json` + `empathy_map.json` | Step-by-Step Flow → Cognitive Load → Error Recovery → Accessibility Notes |

**Template Language:** Jinja2 (lightweight, human-readable, Python-native)

**Schema Extension:** `document_sync_state.schema.json`

Add per-document entry:
- `auto_render_enabled` (boolean)
- `template_ref` (string) — template path
- `last_rendered_at` (datetime)
- `render_trigger` — `auto|manual|pm_note|regeneration_queue`

**CLI Extension:**
- `./productos render docs --workspace-dir ...` — manual trigger for all living docs
- `./productos render doc --doc-key prd --workspace-dir ...` — single doc

**Guardrails:**
- Missing source artifact → skip, log warning, show in cockpit
- Template not found → block, use fallback plain-text dump
- Render produces empty section → flag in quality check
- PM manual annotation in markdown → preserve across renders (parse and re-inject)

**Test:** `tests/test_v10_living_document_renderer.py`

**Success Criteria:**
- `docs/planning/prd.md` regenerates when `artifacts/prd.json` changes
- Every claim traceable to source artifact
- Modification log shows what changed and why
- PM can add manual annotations that survive re-rendering
- Template produces world-class narrative quality (not data dump)

---

### Sprint 4: PM Delta Review Lane (Weeks 8–9)

**Goal:** Cockpit becomes the artifact-delta review surface.

**Cockpit Enhancement:** New panel "Living Artifact Updates"

The PM opens the cockpit and sees:

```
┌─────────────────────────────┐
│ Living Artifact Updates     │
│ 4 queued changes            │
├─────────────────────────────┤
│ Competitor dossier updated  │
│ → Strategy brief delta:     │
│   3 claims outdated         │
│ [Review] [Approve] [Reject] │
├─────────────────────────────┤
│ Persona interview added     │
│ → Journey step 4: cognitive  │
│   load flagged as high      │
│ [Review] [Approve] [Reject] │
├─────────────────────────────┤
│ PRD scope tightened         │
│ → Prototype plan: 2 new      │
│   screens required          │
│ [Review] [Approve] [Reject] │
├─────────────────────────────┤
│ Research notebook refreshed │
│ → Problem brief: 1 new      │
│   evidence source           │
│ [Review] [Approve] [Reject] │
└─────────────────────────────┘
```

**Schema Extension:** `cockpit_state.schema.json`

```json
"living_updates_queue": [
  {
    "update_id": "lu_001",
    "regeneration_queue_item_ref": "rq_item_001",
    "source_change": "Competitor dossier updated",
    "target_artifact": "artifacts/strategy_context_brief.json",
    "delta_summary": "3 claims outdated: pricing advantage, feature parity, segment targeting",
    "impact_classification": "content_deep",
    "pm_action": "pending|approved|rejected|modified",
    "pm_note": "",
    "reviewed_at": "..."
  }
]
```

**CLI:**
- `./productos review delta --workspace-dir ... --update-id lu_001 --action approve`
- `./productos review delta --workspace-dir ... --update-id lu_001 --action reject --note "Competitor pricing is temporary promotion, don't change strategy yet"`
- `./productos review delta --workspace-dir ... --update-id lu_001 --action modify --modification '{"claim_3": "revise to account for promotional pricing"}'`

**Runtime Integration:**
- `enrich_runtime_states()` in `pm_superpowers.py` extended to include `living_updates_queue`
- Cockpit HTML template updated with new panel
- `./productos run improve` — processes approved deltas, regenerates downstream

**Learning Loop:**
- Rejected deltas are logged with PM rationale
- Over time, propagation classification accuracy is scored
- If PM consistently rejects "content_deep" items that were classified as "mechanical", the classification model is flagged for refinement

**Test:** `tests/test_v10_cockpit_living_updates.py`

**Success Criteria:**
- PM sees all pending artifact updates in cockpit
- Can approve/reject/modify with one command
- Rejections prevent downstream propagation
- Approved deltas trigger regeneration queue automatically
- Rejection patterns are logged for model improvement

---

### Sprint 5: PM Note Ingestion (Weeks 10–11)

**Goal:** PM's raw notes become structured artifact delta proposals.

**New Skill:** `core/skills/pm_note_ingestion/SKILL.md` (V10 12-element standard)

**Trigger:** PM adds note to inbox (text transcript, meeting notes, voice memo → text)

**Execution:**
1. Parse input: identify entities (competitor mentions, customer quotes, feature requests, scope changes, stakeholder feedback)
2. Map to artifacts: which existing artifact(s) does this affect?
3. Propose delta: structured diff for target artifact
4. Queue in `regeneration_queue` with `pm_review` mode
5. Update `intake_routing_state`

**New Schema:** `core/schemas/artifacts/pm_note_delta_proposal.schema.json`

```json
{
  "schema_version": "1.0.0",
  "pm_note_delta_proposal_id": "pndp_001",
  "workspace_id": "ws_myproduct",
  "source_note": {
    "note_path": "inbox/raw-notes/customer-call-may6.txt",
    "note_type": "transcript|meeting_notes|voice_memo|screenshot|document",
    "summary": "Customer mentioned CompetitorAlpha's new AI feature..."
  },
  "proposed_deltas": [
    {
      "delta_id": "pd_001",
      "target_artifact_ref": "artifacts/competitor_dossier.json",
      "proposed_change": "Add CompetitorAlpha AI feature launch to competitive timeline",
      "confidence": "high",
      "evidence_quote": "'CompetitorAlpha just launched an AI PRD generator that seems similar to our V10 roadmap'",
      "regeneration_queue_item_id": "rq_item_001"
    }
  ],
  "generated_at": "..."
}
```

**Ingestion Surface:**
- `docs/inbox/` — PM drops notes here
- `./productos ingest --source docs/inbox/customer-call-may6.txt --workspace-dir ...`

**Priority (Sprint 5):** Text transcripts first (structured, parseable)
**Sprint 5b:** Voice memos (transcription integration)
**Sprint 5c:** Slack threads, email exports

**Guardrails:**
- Low confidence proposal → queue with "needs_pm_clarification" flag
- Proposal contradicts existing artifact → surface contradiction, require PM resolution
- No identifiable target artifact → log as "unrouted note", PM manually routes
- Multiple artifact proposals → show all, PM selects which to apply

**Test:** `tests/test_v10_pm_note_ingestion.py`

**Success Criteria:**
- Text transcript about competitor launch → queued proposal to update competitor dossier
- Meeting notes with customer feedback → queued proposal to update persona + problem brief
- All proposals require PM approval before artifact mutation
- Low-confidence proposals flagged for clarification

---

### Sprint 6: Generic Export & Agent Brief (Weeks 12–13)

**Goal:** Living artifacts render to any format on demand.

**System:** `core/python/productos_runtime/export_pipeline.py`

**Function:** `export_artifact(artifact_ref, format, workspace_dir)`

Formats:
- `markdown` — living doc (already exists via renderer)
- `deck` — presentation brief → visual export pipeline
- `agent_brief` — structured ACP for AI agent consumption
- `stakeholder_update` — executive summary
- `battle_card` — competitive snapshot
- `one_pager` — product overview

**Agent Brief Template:** `core/templates/exports/agent-brief.md.jinja2`

Renders from `prd.json` + `user_journey_map.json` + `acceptance_criteria_set.json`

Structure:
```markdown
# Agent Brief: [Mission Title]

## 1. Intent & Boundaries
- Problem summary, outcome summary, value hypothesis
- EXPLICIT OUT_OF_SCOPE: [bulleted list — agent must NOT build these]

## 2. User Journey as State Machine
| Step | Trigger | User Action | System Response | Error Recovery | States Required |

## 3. Executable Acceptance Criteria
| ID | Criterion | Test Method | Priority | Notes |

## 4. Design & Quality Constraints
- Device targets, accessibility, required states, data realism

## 5. Evidence & Context
- Why this matters: [customer quotes, research findings]
- Competitor context: [if relevant]
```

**Human PM reviews** this markdown before sending to agent.  
**Agent consumes** the same markdown.  
**ProductOS parses** the markdown back into structured objects for automated fidelity checking (Sprint 8).

**New Skill:** `core/skills/export_pipeline/SKILL.md` (V10 12-element standard)

**CLI:**
- `./productos export --artifact artifacts/prd.json --format deck --workspace-dir ...`
- `./productos export --artifact artifacts/prd.json --format agent_brief --workspace-dir ...`
- `./productos export --artifact artifacts/strategy_context_brief.json --format stakeholder_update --workspace-dir ...`

**Guardrails:**
- Export from stale artifact → warn, suggest regeneration first
- Missing required source artifact for format → block, list missing refs
- Agent brief with weak boundaries → block, require `prd_scope_boundary_check` first

**Test:** `tests/test_v10_export_pipeline.py`

**Success Criteria:**
- Same artifact exports to deck for leadership, agent brief for Windsurf, stakeholder update for Slack
- All exports timestamped and traceable to source artifact version
- No copy-paste drift between formats

---

### Sprint 7: Research Auto-Cascade (Weeks 14–15)

**Goal:** Competitive research feeds auto-refresh and cascade into all artifacts.

**Tasks:**

1. **Auto-refresh wiring**
   - `external_research_feed_registry` gets scheduler integration
   - Feed refresh triggers `competitive_radar_scan` → `competitive_shift_analysis`
   - High/critical shifts auto-trigger `drift_and_impact_propagation` → `regeneration_queue`

2. **Battle card auto-update**
   - When `competitor_dossier` changes, `regeneration_queue` auto-queues `battle_card` refresh
   - Mechanical updates (pricing, feature list) auto-execute
   - Strategic implications (positioning, differentiation) queue for PM review

3. **Strategy brief cascade**
   - `strategy_context_brief` auto-updates from refreshed research + competitive data
   - PM sees delta in cockpit: *"3 PESTLE factors changed since last strategy review"*

4. **Customer pulse propagation**
   - `customer_pulse` updates trigger persona narrative refresh
   - Persona changes trigger user journey re-assessment
   - Journey changes trigger prototype plan updates

**Test:** `tests/test_v10_research_auto_cascade.py`

**Success Criteria:**
- Competitive feed refresh → battle card updated within 1 hour
- High-severity shift → strategy brief queued for PM review
- Customer pulse update → persona → journey → prototype cascade completes
- All cascades are traceable in `regeneration_queue` and `document_sync_state`

---

### Sprint 8: Dogfood Validation (Weeks 16–17)

**Goal:** Run the full V11 loop on the private dogfood workspace.

**Validation Scenarios:**

| Scenario | Input | Expected Output |
|---|---|---|
| 1. Competitive alert | PM drops screenshot of CompetitorAlpha launch in `inbox/screenshots/` | `competitor_dossier` updated → `strategy_context_brief` queued → PM reviews delta → approves → `docs/strategy/competitive-brief.md` regenerated |
| 2. Customer interview | PM adds transcript to `inbox/transcripts/` | `persona_narrative_card` queued → `problem_brief` queued → PM reviews both → approves → `docs/discovery/problem-brief.md` + `user_journey_map.json` regenerated |
| 3. Scope change | PM tightens PRD scope boundary | `prototype_generation_plan` queued with 2 new screens → PM approves → `docs/planning/prototype-plan.md` regenerated |
| 4. Leadership deck | PM requests deck export | All living docs render to `presentation_brief.json` → deck generated → no stale claims |
| 5. Agent handoff | PM exports agent brief | `agent-brief.md` generated from current PRD + journey + AC → agent builds → fidelity report validates |

**Metrics:**
- PM rewrite rate: target <10% (down from ~40% baseline)
- Time from inbox note to artifact update: target <2 hours for mechanical, <24 hours for content-deep
- Artifact freshness score: target >90% (no artifact >7 days stale)
- Delta approval rate: target >80% (PM approves most proposals without modification)

**Ralph Loop:**
- Inspect: review dogfood metrics
- Implement: fix gaps
- Refine: improve delta preview quality, classification accuracy
- Validate: re-run scenarios
- Fix: address failures
- Revalidate: confirm metrics meet target

**Success Criteria:**
- All 5 validation scenarios pass
- PM rewrite rate <10%
- Artifact freshness >90%
- `./productos doctor --workspace-dir /path/to/private-workspace` reports green

---

### Sprint 9: Release Prep (Weeks 18–19)

**Goal:** Promote V11 to stable line.

**Tasks:**
1. Feature scorecards for all V11 capabilities
2. Blueprint trace matrix update
3. Release note: `core/docs/v11-release-note.md`
4. Bounded claim document: `core/docs/v11-bounded-claim.md`
5. `./productos release --slice-label "v11-living-system" --push`

**Success Criteria:**
- All schema + example + test passing
- Ralph loop complete for every sprint
- Dogfood workspace proves PM leverage
- Release tag created: `v11.0.0`

---

## Complete Artifact Registry

### New Schemas
| Schema | Sprint | Purpose |
|---|---|---|
| `regeneration_queue.schema.json` | 2 | Orchestrates artifact regeneration after source changes |
| `pm_note_delta_proposal.schema.json` | 5 | Structured delta proposed from unstructured PM input |

### Extended Schemas
| Schema | Sprint | Change |
|---|---|---|
| `document_sync_state.schema.json` | 3 | Add `auto_render_enabled`, `template_ref`, `last_rendered_at`, `render_trigger` |
| `cockpit_state.schema.json` | 4 | Add `living_updates_queue` |
| `execution_session_state.schema.json` | 4 | Add `living_doc_regeneration` session type |

### New Skills (V10 12-element standard)
| Skill | Sprint |
|---|---|
| `regeneration_queue_management` | 2 |
| `living_document_rendering` | 3 |
| `pm_note_ingestion` | 5 |
| `export_pipeline` | 6 |

### New Runtime Modules
| Module | Sprint | Functions |
|---|---|---|
| `core/python/productos_runtime/living_system.py` | 2 | `build_regeneration_queue`, `process_regeneration_item`, `classify_impact`, `generate_delta_preview` |
| `core/python/productos_runtime/markdown_renderer.py` | 3 | `render_living_document`, `load_template`, `resolve_source_artifacts`, `preserve_annotations` |
| `core/python/productos_runtime/export_pipeline.py` | 6 | `export_artifact`, `render_agent_brief`, `render_deck_brief`, `render_stakeholder_update` |

### New Templates
| Template | Sprint | Format |
|---|---|---|
| `core/templates/living_docs/prd.md.jinja2` | 3 | Narrative PRD from structured artifacts |
| `core/templates/living_docs/problem-brief.md.jinja2` | 3 | Problem framing with evidence |
| `core/templates/living_docs/strategy-brief.md.jinja2` | 3 | Market position and wedge |
| `core/templates/living_docs/user-journey.md.jinja2` | 3 | Step-by-step flow |
| `core/templates/exports/agent-brief.md.jinja2` | 6 | Agent-optimized brief |
| `core/templates/exports/stakeholder-update.md.jinja2` | 6 | Executive summary |

### New Tests
| Test | Sprint | Coverage |
|---|---|---|
| `tests/test_v10_regeneration_queue.py` | 2 | Schema + runtime + skill contract |
| `tests/test_v10_living_document_renderer.py` | 3 | Render pipeline + traceability |
| `tests/test_v10_cockpit_living_updates.py` | 4 | Cockpit integration + PM actions |
| `tests/test_v10_pm_note_ingestion.py` | 5 | Ingestion + delta proposal |
| `tests/test_v10_export_pipeline.py` | 6 | Multi-format export |
| `tests/test_v10_research_auto_cascade.py` | 7 | End-to-end research cascade |

---

## Risk & Mitigation

| Risk | Mitigation |
|---|---|
| Auto-propagation creates noise | Strict mechanical vs. content-deep classification; PM can tune sensitivity per artifact type |
| Template rendering loses PM voice | Templates are narrative-first, evidence-backed; PM edits structured artifacts with voice, template renders the story |
| Circular dependencies in propagation | Detected by `drift_and_impact_propagation` guardrail; blocked with PM alert |
| Over-automation reduces PM judgment | Design principle: AI handles reconstruction, PM handles decisions. Every strategic delta requires approval. |
| Dogfood workspace becomes stale | Auto-refresh on startup; weekly regeneration queue scan; PM prompted to review if >7 days stale |

---

## World-Class Quality Criteria

Every sprint must satisfy:

1. **Evidence Traceability** — Every claim in every rendered document links to a source artifact or note
2. **Delta Transparency** — PM can see exactly what changed, why, and what it affects before approving
3. **Reversibility** — Every auto-executed change can be reverted; every PM rejection is recorded
4. **No Silent Drift** — No artifact updates without a corresponding `regeneration_queue` entry and `document_sync_state` log entry
5. **Human at the Edge** — Mechanical changes auto-execute; all content-deep changes require explicit PM approval
6. **Format Agnostic** — Source artifacts are the truth; all formats (markdown, deck, agent brief) are render targets

---

## Next Action

This plan is stored at `core/docs/v11-living-system-execution-plan.md`.

The next thread should begin **Sprint 0**: restore the private dogfood workspace and initialize it for V11 mission work.

Then proceed sequentially through Sprints 1–9, with each sprint's deliverables validated before proceeding to the next.

**Ralph loop applies to every sprint:** inspect, implement, refine, validate, fix, revalidate.

---

*Plan generated: 2026-05-06*  
*Approved by: ProductOS PM*  
*Workspace: private local dogfood workspace*
