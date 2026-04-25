# ProductOS Presentation Component

This component owns the deck lane in ProductOS: internal or executive HTML presentations plus native PPT export.

## What It Owns

- narrative pipeline runtime for `presentation_brief -> evidence_pack -> presentation_story -> render_spec`
- derived packaging artifacts such as `publish_check`, `slide_spec`, and `ppt_export_plan`
- HTML deck rendering
- native PPT export adapters
- presentation schemas and examples
- presentation docs, workflows, and contracts

## What It Does Not Own

- customer-safe public workflow pages
- HTML-first workflow publication
- workflow corridor-specific publish gates

## Integration Surface

This repository exposes the component through:

- `components/presentation/python/productos_presentation/runtime.py`
- `components/presentation/node/export_presentation_pptx.mjs`

This repository also ships thin CLI adapters over that runtime:

- `scripts/export_presentation.py`
- `scripts/presentation_export_pptx.mjs`

Canonical ProductOS CLI surface:

- `./productos visual export deck <presentation_brief.json>`
- `./productos visual export deck <presentation_brief.json> --node-ppt-output <output.pptx>`

Historical workspace bundle generation used the same runtime through:

- `core/python/productos_runtime/v4.py`

## Update Model

Compatibility scripts remain supported, but `./productos visual export deck` is the canonical repo-level command.
