# ProductOS Presentation Component

This vendored component ships the presentation capability used by the current ProductOS V5.0.0 line.

## What It Owns

- narrative pipeline runtime for `presentation_brief -> evidence_pack -> presentation_story -> render_spec`
- derived packaging artifacts such as `publish_check`, `slide_spec`, and `ppt_export_plan`
- HTML rendering
- native PPT export adapters
- presentation schemas and examples
- presentation docs, workflows, and contracts

## Integration Surface

This repository exposes the component through:

- `components/presentation/python/productos_presentation/runtime.py`
- `components/presentation/node/export_presentation_pptx.mjs`

This repository also ships thin CLI adapters over that runtime:

- `scripts/export_presentation.py`
- `scripts/presentation_export_pptx.mjs`

Historical workspace bundle generation used the same runtime through:

- `core/python/productos_runtime/v4.py`

## Update Model

The vendored component version stays aligned to the current ProductOS core stable line.
To upgrade another project, copy `components/presentation/` first.
Copy the `scripts/` adapters only if the target project wants the same CLI surface.
