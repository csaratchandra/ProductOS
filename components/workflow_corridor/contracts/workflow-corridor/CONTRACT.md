# Workflow-Corridor Agent Contract

## Purpose

Turn typed workflow inputs into a customer-safe corridor narrative that explains stages, ownership, proof posture, and overlays on one HTML-first page.

## Core responsibilities

- create `workflow_corridor_spec` artifacts from bounded workflow inputs
- generate `corridor_proof_pack`, `corridor_narrative_plan`, and `corridor_render_model`
- keep ownership, handoffs, and proof posture explicit in the rendered corridor
- preserve customer-safe filtering as part of the corridor runtime rather than a post-process

## Inputs

- `workflow_corridor_spec`
- workflow source artifacts and workspace input refs
- audience and publication context

## Outputs

- `corridor_proof_pack`
- `corridor_narrative_plan`
- `corridor_render_model`
- customer-safe HTML corridor

## Required schemas

- `workflow_corridor_spec.schema.json`
- `corridor_proof_pack.schema.json`
- `corridor_narrative_plan.schema.json`
- `corridor_render_model.schema.json`

## Escalation rules

- escalate when workflow ownership is ambiguous enough to distort the corridor
- escalate when proof posture is too weak for the requested publication mode
- escalate when the requested output is really a deck or PPT workflow rather than a corridor

## Validation expectations

- the corridor must explain one canonical workflow without presenter narration
- ownership transitions and blocked or watch states must remain visible
- scenario overlays must stay secondary to the baseline workflow
