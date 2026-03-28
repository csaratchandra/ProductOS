# Cockpit Modes

Purpose: Define the PM-facing operating modes that the cockpit can recommend and route through without requiring manual specialist selection.

## `ask`

Use when the PM is asking for clarification, interpretation, or direct answers rather than artifact creation.

Expected behavior:

- answer directly when confidence is sufficient
- cite source artifacts or assumptions
- recommend a workflow only if the request naturally turns into execution

## `plan`

Use when the PM needs task framing, sequencing, or next-step recommendation.

Expected behavior:

- restate the task
- surface missing context
- surface relevant decision and follow-up queue actions when they affect the next step
- propose a controlled execution path

## `research`

Use when evidence is missing, stale, uncertain, or contradictory.

Expected behavior:

- route to research artifacts and research workflows
- prefer clarification, evidence gathering, and synthesis over premature scope decisions

## `prototype`

Use when ambiguity around usability, feasibility, trust, or experience is still too high for PRD commitment.

Expected behavior:

- recommend a prototype or experiment
- define what uncertainty the prototype is meant to reduce

## `draft`

Use when the PM wants ProductOS to generate a first-pass artifact or communication draft from structured state.

Expected behavior:

- produce a review-ready artifact
- preserve traceability
- avoid inventing unsupported detail

## `review`

Use when an artifact, plan, or recommendation needs validation, critique, or approval support.

Expected behavior:

- apply validation and critique rules
- surface gaps, contradictions, and risks
- prepare explicit review questions where needed

## `status`

Use when the PM needs recurring status outputs or operational visibility.

Expected behavior:

- generate concise updates from workspace state
- distinguish signal from noise
- preserve owner, due-date, and blocker visibility
- highlight queue items that should be reviewed or escalated now

## `leadership`

Use when the audience is director, CPO, portfolio, or similar leadership contexts.

Expected behavior:

- compress detail into decision-relevant summary
- preserve strategic risks, dependencies, and asks
- avoid losing traceability beneath executive tone
