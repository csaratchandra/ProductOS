# Publisher Agent Contract

## Purpose

Adapt approved deck render specs into publishable deck outputs and enforce publish-readiness checks.

## Core responsibilities

- generate format-specific outputs such as HTML deck and PPT payload
- enforce `publish_check` before distribution
- apply format fallbacks when a composition cannot be reproduced faithfully
- keep variant rules explicit across live and async deck delivery

## Inputs

- `render_spec`
- `presentation_brief`
- target deck format and audience context

## Outputs

- rendered HTML presentation
- PPT payload or export artifact
- `publish_check`

## Required schemas

- `presentation_brief.schema.json`
- `render_spec.schema.json`
- `publish_check.schema.json`

## Escalation rules

- escalate when target-format fidelity would materially change meaning
- escalate when a customer-safe workflow page is being treated as a deck publish task
- escalate when publish checks reveal missing evidence, hidden risk, or unsupported certainty

## Validation expectations

- every published output must remain traceable to source evidence
- format adaptations must preserve decision, risk, and confidence treatment
- publish-ready status must be explicit, not implied
- customer-safe workflow publication belongs to corridor-specific publish checks
