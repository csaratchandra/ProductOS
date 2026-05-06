# Living Document Rendering Skill

## 1. Purpose
Render readable markdown documents from structured artifacts using narrative-first templates, ensuring every claim is traceable to source evidence.

## 2. Trigger / When To Use
- Regeneration queue item approved
- PM requests manual render via CLI
- Artifact updated with significant changes
- Scheduled refresh (weekly)

## 3. Prerequisites
- Source artifacts exist and are valid
- Template exists in `core/templates/living_docs/`
- `document_sync_state` entry exists for the document

## 4. Input Specification
- `doc_key`: Document identifier (e.g., "prd", "problem-brief")
- `workspace_dir`: Path to the workspace
- `template_name`: Jinja2 template file name

## 5. Execution Steps
1. Read `document_sync_state` for the doc_key
2. Load all source artifacts referenced in sync state
3. Load template from `core/templates/living_docs/`
4. Validate all required source artifacts are present
5. Render markdown with:
   - Frontmatter: generated_at, source_artifact_refs, template_version
   - Evidence traceability: every claim links to source via footnote
   - Modification log: append-only change history
   - PM annotations: preserved from existing document
6. Write rendered markdown to `docs/[doc_key].md`
7. Update `document_sync_state` with last_rendered_at and render_trigger
8. Log modification entry in sync state

## 6. Output Specification
- `docs/[doc_key].md`: Rendered markdown document
- Updated `document_sync_state` with render metadata
- Modification log entry in sync state

## 7. Guardrails
- Missing source artifact → skip, log warning, show in cockpit
- Template not found → block, use fallback plain-text dump
- Render produces empty section → flag in quality check
- PM manual annotation in markdown → preserve across renders

## 8. Gold Standard Checklist
Rendered document reads like a professional product document written by a senior PM. Every claim traces back to a source artifact or research finding. PM annotations survive re-rendering. Template produces narrative flow, not data dumps.

## 9. Examples
- Excellent: PRD renders as Problem → Solution → Evidence → Scope → Out of Scope narrative with footnotes to research findings
- Poor: PRD renders as JSON dump with no narrative structure, claims without evidence links

## 10. Cross-References
- Upstream: `regeneration_queue_management`
- Downstream: `export_pipeline`
- Related: `document_sync_state`, `source_note_card`

## 11. Maturity Band Variations
- 0→1: Basic template rendering with required fields
- 1→10: Narrative-first templates with evidence traceability
- 10→100: Adaptive templates that adjust tone and depth based on audience

## 12. Validation Criteria
- `tests/test_v10_living_document_renderer.py`
- Rendered document contains all required sections
- All claims have evidence footnotes
- PM annotations preserved across renders
