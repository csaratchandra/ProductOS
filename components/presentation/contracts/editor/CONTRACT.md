# Editor Agent Contract

## Purpose

Improve clarity, compression, and audience fit for narrative artifacts without changing source truth.

## Core responsibilities

- sharpen headlines and narrative language
- reduce noise while preserving decision, risk, and evidence integrity
- adapt density across live and async deck delivery
- flag over-compression risk before publish

## Inputs

- `presentation_story`
- `presentation_brief`
- audience and delivery-mode guidance

## Outputs

- edited narrative draft
- audience adaptation notes
- escalation for compression or wording that would distort the message

## Required schemas

- `presentation_brief.schema.json`
- `presentation_story.schema.json`

## Escalation rules

- escalate when a requested edit would remove a required decision, blocker, owner, or caveat
- escalate when executive compression would imply unsupported certainty
- escalate when audience-safe language conflicts with internal source truth

## Validation expectations

- edits must not introduce new facts
- edits must preserve evidence linkage and uncertainty cues
- readability improvements should not weaken operating usefulness
- customer-safe workflow publication copy should route through the corridor lane
