# Readable Doc Review And Sync Workflow

Purpose: Keep readable documents aligned with their source artifacts, review feedback, and publication rules instead of letting drift accumulate silently.

## Inputs

- readable markdown document under `workspaces/<workspace>/docs/`
- `document_sync_state`
- relevant source artifacts
- `validation_lane_report`
- optional `manual_validation_record`

## Outputs

- revised readable markdown document
- updated `document_sync_state`
- revise / proceed / block guidance

## Operating Sequence

1. Compare the current readable document against its declared source artifacts and latest review findings.
2. Name any drift in claims, metadata, status, audience, or evidence placement.
3. Update the document or mark it as drifted when the gap cannot be safely resolved in the current pass.
4. Refresh `document_sync_state` so the sync state and next action are explicit.
5. Re-run the required validation lanes before the document advances to publication or stakeholder use.

## Rules

- drift must be named explicitly; do not bury it inside general review notes
- if source artifacts changed materially, regenerate or revise the doc instead of patching around the mismatch
- if manual validation requests changes, feed them back into the source-linked doc path rather than creating an uncontrolled side copy
