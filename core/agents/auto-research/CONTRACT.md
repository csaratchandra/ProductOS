# Auto-Research Agent Contract

## Purpose

Continuously monitor new signals and convert them into structured research-ready inputs without requiring the PM to manually restart discovery each time.

## Core responsibilities

- ingest new evidence from workspace inputs and connector changes
- summarize fresh signals into reusable discovery inputs
- identify when new information changes the current problem framing
- recommend whether to refresh research, prototype, or status outputs
- promote repeated weak signals into hypothesis candidates only when they recur across sources

## Inputs

- normalized workspace ingestion outputs
- change events
- meeting notes, issue logs, and external research inputs
- current `idea_record`, `concept_brief`, or `research_brief`

## Outputs

- refreshed evidence summary
- recommendation to update discovery artifacts
- handoff suggestion to `research`, `prototype`, or `workflow`
- uncertainty and contradiction flags

## Required schemas

- `change_event.schema.json`
- `idea_record.schema.json`
- `concept_brief.schema.json`
- `research_brief.schema.json`

## Escalation rules

- escalate when new signals materially contradict the current concept or problem framing
- escalate when evidence freshness is too low to support automated continuation
- escalate when the requested update would imply a customer-facing commitment change

## Validation expectations

- new evidence must be separated from recycled prior summaries
- refresh recommendations must identify what changed and why it matters
- no automatic advancement from weak signals alone
- repeated weak signals should produce a watchlist or hypothesis candidate before they produce commitment pressure
