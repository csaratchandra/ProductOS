# Export Pipeline Skill

## 1. Purpose
Render living artifacts to any format on demand (markdown, deck, agent brief, stakeholder update, battle card, one_pager) while maintaining traceability to source artifacts.

## 2. Trigger / When To Use
- PM requests export via CLI
- Regeneration queue item approved
- Scheduled export for leadership review
- Agent handoff requested

## 3. Prerequisites
- Source artifact exists and is valid
- `prd_scope_boundary_check` passed for agent brief exports
- Document sync state is current

## 4. Input Specification
- `artifact_ref`: Path to source artifact
- `format`: Export format (markdown, deck, agent_brief, stakeholder_update, battle_card, one_pager)
- `workspace_dir`: Path to the workspace

## 5. Execution Steps
1. Load source artifact from workspace
2. Validate artifact is current (check document_sync_state freshness)
3. Select export format handler
4. For agent_brief format:
   a. Run prd_scope_boundary_check first
   b. If boundaries weak, block export and require refinement
5. Render content using format-specific template
6. Add traceability metadata (source artifact ID, generated_at)
7. For agent brief: include explicit out_of_scope, acceptance criteria, user journey as state machine
8. Write exported content to output path
9. Log export in document_sync_state modification log

## 6. Output Specification
- Exported file in requested format
- Updated document_sync_state with export metadata
- Export log entry with timestamp and format

## 7. Guardrails
- Export from stale artifact → warn, suggest regeneration first
- Missing required source artifact for format → block, list missing refs
- Agent brief with weak boundaries → block, require prd_scope_boundary_check first
- No export format handler → raise ValueError with available formats

## 8. Gold Standard Checklist
Same artifact exports cleanly to all formats with no copy-paste drift. Agent briefs have strong boundaries that prevent scope creep. Leadership decks tell a coherent narrative. All exports are timestamped and traceable to source artifact version.

## 9. Examples
- Excellent: PRD exports to agent brief with 8 specific out-of-scope items, executable acceptance criteria, and user journey as state machine
- Poor: PRD exports to agent brief with vague boundaries ("other features not in scope")

## 10. Cross-References
- Upstream: `living_document_rendering`, `prd_scope_boundary_check`
- Downstream: Agent consumption, leadership review, stakeholder communication
- Related: `document_sync_state`, `presentation_brief`

## 11. Maturity Band Variations
- 0→1: Markdown and basic agent brief exports
- 1→10: All 6 formats with strong boundary enforcement
- 10→100: Adaptive exports that adjust depth and tone based on audience

## 12. Validation Criteria
- `tests/test_v10_export_pipeline.py`
- All export formats produce valid output
- Agent briefs have strong boundaries
- Exports are traceable to source artifacts
