# Visual System Boundaries

Purpose: Define the canonical visual lanes in ProductOS so PMs can choose the right output without mixing deck transport, workflow publication, and shared design rules.

## Canonical lanes

- `components/presentation/` owns decks:
  internal or executive HTML decks, narrative packaging, and PPT export.
- `components/workflow_corridor/` owns public workflow pages:
  customer-safe, HTML-first workflow corridors with corridor-specific publish gates.
- `core/` owns shared visual foundations:
  style rules, skill primitives, lane-selection guidance, and agent routing.

## Selection rule

Use the deck lane when the PM needs to:

- brief leadership
- drive a review meeting
- produce an async deck
- export native PPT

Use the corridor lane when the PM needs to:

- explain a workflow on one customer-safe page
- show ownership, handoffs, and proof posture directly in HTML
- publish a workflow without turning slides into a webpage

## Canonical commands

- `./productos visual plan deck|corridor|map <input.json>`
- `./productos visual build <visual_direction_plan.json>`
- `./productos visual review <output-dir-or-output-file>`
- `./productos visual export deck <presentation_brief.json>`
- `./productos visual export corridor <workflow_corridor_spec_or_source_bundle.json>`
- `./productos visual export map <visual_map_spec.json>`

Repo-level scripts remain available as compatibility adapters:

- `scripts/export_presentation.py`
- `scripts/export_workflow_corridor.py`

## Non-goals

- decks do not own customer-safe public workflow publication
- corridor pages do not replace PPT or meeting-deck workflows
- shared visual rules do not duplicate component-specific rendering grammar
