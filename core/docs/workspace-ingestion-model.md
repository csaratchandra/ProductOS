# Workspace Ingestion Model

Purpose: Define how ProductOS receives raw workspace inputs, normalizes them once, captures provenance, and reuses structured outputs across downstream workflows.

## Inbox Model

Each workspace should support an `inbox` for raw or semi-structured inputs such as:

- docs
- PDFs
- spreadsheets
- emails
- images
- screenshots
- transcripts
- tool exports

The inbox is a staging area, not a long-term operating model. ProductOS should normalize inputs into structured summaries or records that downstream workflows can reuse.

In V3 runtime terms, this operational state should be visible through `intake_routing_state` so the PM can see what entered the workspace, what was routed, and what is blocked.

## Normalization Rules

- every inbox item must keep a stable source reference and capture timestamp
- every normalized item must declare its input type explicitly
- raw files should be summarized once and reused rather than repeatedly re-read by downstream workflows
- normalization should preserve enough context to recover the original source when critique, validation, or audit is required

## Provenance Rules

Each normalized record should capture:

- source system
- source reference or original file path
- capture timestamp
- capture actor or importer

When multiple files contribute to one derived output, ProductOS should keep the list of originating input identifiers.

## Structured Extraction Outputs

Recommended extraction outputs by input type:

- docs and PDFs: concise summary, cited evidence points, unresolved questions
- spreadsheets and exports: structured rollup of rows, totals, anomalies, and changed fields
- emails: sender, decision signals, asks, deadlines, and follow-ups
- images and screenshots: view summary, UI or artifact context, notable changes, open questions
- transcripts: decisions, action items, owners, due dates, issues, and open questions

## Reuse Rule

Once an inbox item is normalized, downstream workflows should consume the normalized summary or structured extraction rather than repeatedly parsing the raw source.

This applies especially to:

- transcript to notes
- issue log maintenance
- status mail generation
- research brief generation
- change impact assessment

## Escalation Guidance

- if provenance is missing, the item should not become a publish-driving source without PM review
- if extracted owners, due dates, or source references are missing for high-stakes outputs, route through validation or critic before publish
- if two normalized inputs conflict on customer-facing commitments, pause publish and escalate
