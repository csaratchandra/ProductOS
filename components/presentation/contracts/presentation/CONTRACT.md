# Presentation Agent Contract

## Purpose

Turn structured source artifacts into presentation-ready renderings without making the presentation itself the source of product truth.

## Core responsibilities

- create `presentation_brief` artifacts
- generate `evidence_pack`, `presentation_story`, and normalized `render_spec` outputs
- choose appropriate theme presets for audience and objective
- preserve traceability from source artifacts into rendered slides

## Inputs

- `presentation_brief`
- `status_update`
- `leadership_review`
- `portfolio_update`
- `portfolio_state`
- other source artifacts when relevant

## Outputs

- `evidence_pack`
- `presentation_story`
- `render_spec`
- responsive HTML presentation
- PPT export plan or payload
- `publish_check`

## Required schemas

- `presentation_brief.schema.json`
- `evidence_pack.schema.json`
- `presentation_story.schema.json`
- `render_spec.schema.json`
- `publish_check.schema.json`
- `status_update.schema.json`
- `leadership_review.schema.json`
- `portfolio_update.schema.json`

## Escalation rules

- escalate when a requested presentation would overstate certainty or hide material risk
- escalate when executive compression would drop a required decision, blocker, or dependency
- escalate when a layout request cannot be reproduced cleanly for the target format

## Validation expectations

- source-of-truth must remain outside the rendered deck
- every presentation should be traceable to input artifacts
- tone may change by audience, but the underlying facts may not
