# ProductOS Presentation System

Purpose: Define how ProductOS turns structured product artifacts into modern HTML slides and exportable PowerPoint presentations.

## 1. Source Of Truth

The source of truth for presentation content is not raw HTML.

Use:

- `presentation_brief` for audience, objective, decision context, and source artifacts
- `evidence_pack` for findings, confidence, and source references
- `presentation_story` for storyline, headline intent, and speaker notes
- `render_spec` for normalized rendering structure and theme selection

This keeps content and visual rendering separate.

## 2. Rendering Pipeline

Recommended pipeline:

`portfolio_update / leadership_review / status_mail / other artifacts -> presentation_brief -> evidence_pack -> presentation_story -> render_spec -> slide_spec / ppt_export_plan -> html renderer / native ppt exporter`

## 3. Theme Presets

Initial theme presets:

- `signal`: bold product status look with strong contrast and dashboard energy
- `atlas`: warm editorial strategy deck with clean geometry and leadership tone
- `editorial`: typography-first narrative style for concept or portfolio storytelling

## 4. Responsive HTML

HTML slides should:

- work on desktop and mobile
- use modern responsive layout primitives
- avoid generic default web-app styling
- preserve readability when aspect ratio changes

## 5. PPT Export

Native PPT export should be produced from `render_spec`, `slide_spec`, and `ppt_export_plan`, not arbitrary DOM scraping.

Current adapter model:

- use Python `python-pptx` for the default native `.pptx` generation path
- keep the Node `PptxGenJS` adapter available as an optional alternative path
- map normalized narrative compositions to native PPT text and shape objects where possible
- use fixed aspect ratios such as `16:9` and `4:3`
- fall back to simplified layouts when a web layout cannot be reproduced cleanly

Current implementation status:

- HTML renderer exists in Python and can write responsive `.html` output
- `render_spec`, `slide_spec`, and `ppt_export_plan` exports exist as typed artifacts
- Python runtime can now write native `.pptx` files directly
- the canonical Node exporter lives at `components/presentation/node/export_presentation_pptx.mjs`
- a thin repo-level adapter exists at `scripts/presentation_export_pptx.mjs`
- Node `.pptx` generation still requires `npm install` to install `pptxgenjs`

## 5A. Current commands

HTML, payload, and native PPTX export:

```bash
python3 scripts/export_presentation.py components/presentation/examples/artifacts/presentation_brief.example.json
```

Optional Node PPTX export after installing Node dependencies:

```bash
npm install
node scripts/presentation_export_pptx.mjs tmp/presentations/presentation_brief_pm_ops_q2/presentation_brief_pm_ops_q2.render-spec.json tmp/presentations/presentation_brief_pm_ops_q2/presentation_brief_pm_ops_q2.node-export.pptx
```

## 6. Internet Templates

External design systems and template references can be used as inspiration, but ProductOS should keep:

- its own normalized theme presets
- its own rendering contracts
- its own licensing-clean assets and CSS

## 7. Rule

Do not let presentation tooling become the source of product truth.

Presentations are renderings of source artifacts, not a separate planning system.
