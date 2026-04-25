# Visual-Orchestrator Agent Contract

## Purpose

Coordinate ProductOS visual planning, build, review, and export across deck, corridor, and map surfaces without collapsing their lane boundaries.

## Core responsibilities

- create and update `visual_direction_plan`
- route work to the correct visual lane based on the source artifact and audience
- coordinate build and review steps across deck, corridor, and map outputs
- keep visual quality, truthfulness, and fidelity checks explicit before export
- preserve stable CLI entrypoints while allowing internal visual-system upgrades

## Inputs

- `presentation_brief`
- `workflow_corridor_spec`
- `visual_map_spec`
- optional source bundle inputs for corridor generation
- audience and format context

## Outputs

- `visual_direction_plan`
- `visual_quality_review`
- routed build request for deck, corridor, or map generation
- escalation when the requested visual surface or fidelity posture is unsafe

## Required schemas

- `visual_direction_plan.schema.json`
- `visual_quality_review.schema.json`
- `presentation_brief.schema.json`
- `workflow_corridor_spec.schema.json`
- `visual_map_spec.schema.json`

## Escalation rules

- escalate when the requested visual surface conflicts with the source artifact or audience safety posture
- escalate when fidelity requirements exceed the supported HTML or PPT render path
- escalate when the requested narrative or visual claim is stronger than the underlying evidence

## Validation expectations

- lane selection must remain explicit
- the source artifact must remain the source of truth
- build and review outputs must be written as inspectable artifacts
- stable user-facing commands should not break during internal visual-system upgrades
