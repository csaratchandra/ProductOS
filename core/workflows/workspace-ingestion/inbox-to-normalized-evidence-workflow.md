# Inbox To Normalized Evidence Workflow

Purpose: Convert raw workspace inbox inputs into reusable structured evidence with provenance so downstream ProductOS workflows do not repeatedly re-parse raw sources.

## Inputs

- inbox items such as docs, PDFs, spreadsheets, emails, images, screenshots, transcripts, and exports
- optional workspace manifest
- optional connector metadata

## Outputs

- normalized evidence bundle
- structured extraction outputs
- optional `handoff_contract` to research, transcript-to-notes, issue maintenance, or change assessment workflows

## Rules

- capture provenance for every input before downstream use
- summarize each raw input once and reuse that normalized output
- extract decisions, action items, owners, due dates, issues, and open questions from transcripts
- retain source references so validation and critique can trace back to originals
- if the input conflicts with current approved workspace state, escalate instead of silently overwriting downstream artifacts
- if critical fields are missing for a high-stakes workflow, route through validation before publish-driving use
