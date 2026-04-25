# ProductOS Workflow Corridor Component

This component owns the HTML-first workflow corridor lane for customer-facing ProductOS experiences.

## What It Owns

- `workflow_corridor_spec -> corridor_proof_pack -> corridor_narrative_plan -> corridor_render_model`
- corridor-specific publish checks that can block public output
- customer-safe HTML rendering for `configurable_workflow_corridor`
- artifact-driven generation with curated override support

## What It Does Not Own

- slide-oriented presentations and PPT export
- internal memo or deck transport
- ad hoc public demo pages without typed corridor inputs

## Current Entry Points

- `components/workflow_corridor/python/productos_workflow_corridor/runtime.py`
- `scripts/export_workflow_corridor.py`
- `./productos visual export corridor <workflow_corridor_spec_or_source_bundle.json>`

## Positioning

Use this component for public or product-browse workflow pages.

Keep `components/presentation/` for deck and slide workflows.
Once this lane is available, weaker ad hoc HTML prototype paths should not be treated as acceptable public workflow demo output.
