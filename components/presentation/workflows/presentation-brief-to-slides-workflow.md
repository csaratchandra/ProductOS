# Presentation Brief To Slides Workflow

Purpose: Convert a `presentation_brief` into a grounded narrative pipeline that drives responsive HTML, PPT export, and publish checks.

## Inputs

- `presentation_brief`
- source artifacts such as `portfolio_update`, `portfolio_state`, `leadership_review`, or `status_mail`
- audience and theme requirements

## Outputs

- `evidence_pack`
- `presentation_story`
- `render_spec`
- responsive HTML presentation
- PPT export plan
- `publish_check`

## Rules

- preserve the truth of source artifacts while adapting tone and density for audience
- use curated theme presets rather than random styling
- narrative planning should remain explicit before rendering
- HTML output should be responsive and visually distinctive
- PPT output should be generated from normalized render structure, not arbitrary DOM scraping
- if a layout is too web-specific for native PPT fidelity, fall back to a simpler composition layout
- every publishable output must carry visible evidence and risk treatment when relevant
