# ProductOS Workflow Corridor System

Purpose: Define the dedicated customer-safe visual lane for configurable workflow pages.

Canonical ProductOS CLI:

`./productos visual export corridor <workflow_corridor_spec_or_source_bundle.json>`

Compatibility adapter:

`python3 scripts/export_workflow_corridor.py <source_bundle.json>`

## Pipeline

Recommended corridor pipeline:

`source artifacts + workspace inputs -> workflow_corridor_spec -> corridor_proof_pack -> corridor_narrative_plan -> corridor_render_model -> corridor_publish_check -> HTML page`

## Required corridor primitives

- stage cards
- ownership and handoff connectors
- terminal outcome branches
- scenario delta panels
- persona visibility matrix
- KPI and proof rail
- evidence and provenance notes
- explicit blocked, watch, inferred, and approved states

## Rules

- one primary message per screen section
- visible distinction between observed proof and bounded inference
- customer-safe filtering happens in render logic, not as a post-process
- public publication is blocked when proof, ownership, or reading path is weak
- the page should behave like a corridor narrative, not a deck turned into HTML
