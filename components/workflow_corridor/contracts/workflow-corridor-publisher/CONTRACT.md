# Workflow-Corridor-Publisher Agent Contract

## Purpose

Publish workflow corridor outputs safely by enforcing corridor-specific proof, ownership, and audience gates before external sharing.

## Core responsibilities

- render corridor HTML from approved corridor artifacts
- enforce `corridor_publish_check` before publication
- block customer-safe output when proof, ownership, or filtering posture is weak
- keep corridor publication distinct from deck and PPT publishing

## Inputs

- `workflow_corridor_spec`
- `corridor_render_model`
- optional `corridor_proof_pack`
- target audience and publication context

## Outputs

- rendered HTML corridor
- `corridor_publish_check`
- explicit publish, hold, or bounded-release recommendation

## Required schemas

- `workflow_corridor_spec.schema.json`
- `corridor_render_model.schema.json`
- `corridor_proof_pack.schema.json`
- `corridor_publish_check.schema.json`

## Escalation rules

- escalate when customer-safe and internal-only content are being mixed
- escalate when the publication request would overstate certainty or hide blocked handoffs
- escalate when the requested output should route through the deck lane instead

## Validation expectations

- publish readiness must be explicit
- customer-safe filtering must already be reflected in the rendered corridor
- corridor publication must preserve visible proof and claim posture
