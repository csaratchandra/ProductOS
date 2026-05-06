# PM Note Ingestion Skill

## 1. Purpose
Transform unstructured PM inputs (transcripts, meeting notes, voice memos) into structured artifact delta proposals for review and auto-propagation.

## 2. Trigger / When To Use
- PM adds note to inbox directory
- CLI ingest command with source file
- Scheduled inbox scan

## 3. Prerequisites
- Inbox directory exists with raw notes
- Target artifacts are loadable
- Workspace has active mission brief

## 4. Input Specification
- `source_note`: {note_path, note_type, summary}
- `workspace_dir`: Path to the workspace
- `note_type`: transcript | meeting_notes | voice_memo | screenshot | document

## 5. Execution Steps
1. Parse input file to extract text content
2. Identify entities: competitor mentions, customer quotes, feature requests, scope changes, stakeholder feedback
3. Map entities to existing artifacts in workspace
4. For each affected artifact:
   a. Propose structured delta (what should change)
   b. Assign confidence level (high/medium/low/needs_pm_clarification)
   c. Extract evidence quote from source note
   d. Create regeneration queue item reference
5. Emit `pm_note_delta_proposal.json` artifact
6. Queue proposals in regeneration queue with pm_review mode
7. Update intake_routing_state

## 6. Output Specification
- `pm_note_delta_proposal.json`: Structured delta proposals
- Regeneration queue items for each proposal
- Updated intake_routing_state

## 7. Guardrails
- Low confidence proposal → queue with "needs_pm_clarification" flag
- Proposal contradicts existing artifact → surface contradiction, require PM resolution
- No identifiable target artifact → log as "unrouted note", PM manually routes
- Multiple artifact proposals → show all, PM selects which to apply

## 8. Gold Standard Checklist
Every PM note produces actionable delta proposals with clear evidence quotes. Confidence levels are accurate. Contradictions with existing artifacts are surfaced immediately. PM can approve/reject/modify each proposal with one command.

## 9. Examples
- Excellent: Customer call transcript → 3 delta proposals (competitor dossier, persona narrative, problem brief) all with high confidence and clear evidence quotes
- Poor: Meeting notes → 1 vague proposal with no evidence quote, no confidence level

## 10. Cross-References
- Upstream: Inbox ingestion, voice memo transcription
- Downstream: `regeneration_queue_management`, `living_document_rendering`
- Related: `intake_routing_state`, `source_note_card`

## 11. Maturity Band Variations
- 0→1: Text transcripts only, manual entity mapping
- 1→10: Automated entity extraction with confidence scoring
- 10→100: Voice memo integration, Slack/email ingestion, learning from PM feedback

## 12. Validation Criteria
- `tests/test_v10_pm_note_ingestion.py`
- All proposals have required fields
- Confidence levels are valid enum values
- Evidence quotes are non-empty
