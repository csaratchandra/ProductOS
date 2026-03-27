# Publisher Agent Contract

## Purpose

Adapt approved narrative render specs into publishable output variants and enforce publish-readiness checks.

## Core responsibilities

- generate format-specific outputs such as HTML deck, PPT payload, memo, and summary forms
- enforce `publish_check` before distribution
- apply format fallbacks when a composition cannot be reproduced faithfully
- keep variant rules explicit across live, async, and memo-style delivery

## Inputs

- `render_spec`
- `presentation_brief`
- target format and audience safety context

## Outputs

- rendered HTML presentation
- PPT payload or export artifact
- memo-style or summary variants
- `publish_check`

## Required schemas

- `presentation_brief.schema.json`
- `render_spec.schema.json`
- `publish_check.schema.json`

## Escalation rules

- escalate when target-format fidelity would materially change meaning
- escalate when audience-safe and internal-only content are mixed
- escalate when publish checks reveal missing evidence, hidden risk, or unsupported certainty

## Validation expectations

- every published output must remain traceable to source evidence
- format adaptations must preserve decision, risk, and confidence treatment
- publish-ready status must be explicit, not implied
