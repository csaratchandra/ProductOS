# ProductOS V11.0.0 Candidate Release Note

**Release Date:** TBD
**Release Tag:** TBD
**Stable Line:** V10.0.0 remains current
**Previous Stable:** V10.0.0

---

## Executive Summary

ProductOS V11 introduces the **Living Product System** — a fundamental shift from static artifact generation to auto-propagating, self-rendering, delta-reviewed product management.

> *"I capture a voice memo after a customer call. ProductOS updates the persona narrative, flags the PRD for a scope delta, regenerates the user journey with the new pain point, and queues the competitive analysis brief for refresh. I open the cockpit, see 4 suggested artifact updates, approve 3, reject 1 with a note. My leadership deck exports from the current living state — never stale."*

That is the V11 superpower. **One source of truth. Auto-propagation. Human approval at the edges.**

---

## What's New

### 1. Auto-Propagation Engine

When any source artifact changes, ProductOS computes the dependency graph, classifies impact, and either auto-executes mechanical changes or queues content-deep changes for PM review.

- `core/python/productos_runtime/living_system.py`
- `core/schemas/artifacts/regeneration_queue.schema.json`
- CLI: `./productos queue build`, `./productos queue review`

### 2. Living Markdown Renderer

Readable documents are render targets, not manually edited files. Templates are narrative-first, evidence-backed, and preserve PM annotations across re-renders.

- `core/python/productos_runtime/markdown_renderer.py`
- Templates: `prd.md.jinja2`, `problem-brief.md.jinja2`, `strategy-brief.md.jinja2`, `user-journey.md.jinja2`
- CLI: `./productos render doc --doc-key prd`

### 3. PM Delta Review Lane

The cockpit gains a "Living Artifact Updates" panel. PMs see exactly what changed, why, and what it affects — then approve, reject, or modify each delta with one command.

- Extended `cockpit_state.schema.json` with `living_updates_queue`
- CLI: `./productos review-delta --update-id ... --action approve`

### 4. Export Pipeline

Same artifact exports to any format: markdown, deck, agent brief, stakeholder update, battle card, one pager. No copy-paste drift between formats.

- `core/python/productos_runtime/export_pipeline.py`
- Agent briefs include explicit out_of_scope and executable acceptance criteria
- CLI: `./productos export --artifact ... --format agent_brief`

### 5. PM Note Ingestion

PM notes (transcripts, meeting notes, voice memos) become structured delta proposals with confidence scores and evidence quotes.

- `core/skills/pm_note_ingestion/SKILL.md`
- `core/schemas/artifacts/pm_note_delta_proposal.schema.json`

---

## Architecture Principles

| Principle | Definition |
|---|---|
| Evidence Traceability | Every claim links to a source artifact or note |
| Delta Transparency | PM sees exactly what changed and why before approving |
| Reversibility | Every auto-executed change can be reverted |
| No Silent Drift | No updates without regeneration_queue entry and document_sync_state log |
| Human at the Edge | Mechanical auto-executes; content-deep requires PM approval |
| Format Agnostic | Source artifacts are truth; all formats are render targets |

---

## New Skills

| Skill | Sprint | Purpose |
|---|---|---|
| `regeneration_queue_management` | 2 | Orchestrates artifact regeneration |
| `living_document_rendering` | 3 | Renders narrative-first living docs |
| `pm_note_ingestion` | 5 | Transforms PM notes to delta proposals |
| `export_pipeline` | 6 | Renders artifacts to any format |

## Enhanced Skills

| Skill | Enhancement |
|---|---|
| `prd_scope_boundary_check` | Completed to full 12-element contract with boundary scoring (1-10) |
| `drift_and_impact_propagation` | Added regeneration_mode classification (mechanical/content_deep/structural) |

---

## Dogfood Validation

V11 is being validated in a private local dogfood workspace that is not included in the shared repo.

- Mode: `enterprise`
- Mission: "Make ProductOS artifacts live"

---

## Upgrade Notes

1. V10 workspaces are fully backward-compatible
2. New V11 features are opt-in via CLI commands
3. Existing `document_sync_state` artifacts auto-upgrade on first V11 render
4. No silent migration — PM must explicitly enable `auto_render_enabled` per document

---

## Validation

```bash
pytest tests/test_v11_living_system.py
python3 scripts/validate_artifacts.py
./productos --workspace-dir /path/to/workspace queue build --source-artifact artifacts/prd.json
```

---

*Status: candidate only until public release metadata is aligned*  
*Release Operator: V11 Living System*
