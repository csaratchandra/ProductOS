# Visual Style System

Purpose: Define the shared visual language for ProductOS so different renderings stay coherent without becoming visually interchangeable.

## Design Bar

ProductOS visuals should be:

- consultant-grade
- modern
- elegant
- precise
- story-led
- business-ready

## Typography Hierarchy

- headline: decisive statement that carries the slide or visual message
- section label: compact orienting text for visual grouping
- body: concise explanatory text
- evidence note: supporting detail or source context

## Color Roles

- base: stable neutral for structure and whitespace
- primary emphasis: highlight the main message or current state
- caution: risk, watch, or dependency concern
- critical: blocked, incident, or publish-stopping condition
- success: validated, approved, or healthy state

## Style Primitives

- spacing scale: use consistent spacing steps of `4 / 8 / 12 / 16 / 24 / 32`
- grid: default to a 12-column grid for slides and a 6-column grid for memo/dashboard cards
- shape language: favor rectangles, soft-corner containers, and directional connectors over decorative illustration
- emphasis token: use one strong accent color per visual and avoid competing highlight colors
- evidence token: reserve a compact note treatment for source references, timestamps, and certainty cues
- risk token: encode watch, blocked, and no-go states consistently across diagrams and summaries

## Diagram Grammar

- nodes represent artifacts, decisions, teams, or workflow steps
- arrows represent directional dependency, handoff, or causal progression
- dashed connectors represent inferred or provisional links
- blocked states should use the critical token plus an explicit blocker label
- review-needed states should remain visually distinct from completed states

## Chart Selection Rules

- use bars for ranked comparison
- use timelines for sequence and dependency over time
- use matrices only when two axes both matter to the decision
- use trace diagrams when provenance and rationale must stay visible
- avoid pie charts unless composition is simple and exact shares matter less than order of magnitude

## Layout Rules

- use clear visual hierarchy before decorative styling
- keep one primary message per visual
- prefer layered layouts over dense tables when narrative matters
- preserve whitespace discipline so emphasis is intentional
- keep supporting evidence close to the claim it justifies
- do not let legends or footnotes carry the primary interpretation

## Diagram Conventions

- workflows should show state, handoff direction, and blocked points
- dependency maps should distinguish directional dependency from shared context
- trace views should preserve source-to-decision lineage
- risk views should separate severity from certainty

## Surface Ownership

- shared visual rules live in `core/docs/`
- deck-specific rendering grammar lives in `components/presentation/`
- workflow corridor grammar lives in `components/workflow_corridor/`
- public workflow pages should feel HTML-native, not like slides stacked in a browser

## Map Selection Rules

- use roadmap views for sequencing, milestones, and dependency tradeoffs over time
- use user journey maps for experience stages, pain points, and opportunity discovery
- use process flows for actor, input, output, and bottleneck clarity
- use workflow maps for handoffs, owners, and operational state
- use capability maps for platform or operating-model coverage and gaps
- use product maps and feature maps for scope structure and relationship clarity
- use mind maps for decomposition, brainstorming, and root-cause exploration
- use SWOT only for strategy framing where internal and external factors both matter
- use impact-effort matrices for prioritization and decision tradeoffs

## Map Payload Rules

- every map should declare one primary decision or use case
- map payloads should preserve nodes, stages, lanes, axes, and certainty notes explicitly
- different map families should not collapse into the same bullet layout across HTML and PPT

## Component Reuse Model

- reuse one shared `visual_map_spec` contract across roadmap, journey, process, workflow, capability, product, feature, and mind-map views
- route non-matrix maps through the same canvas primitives: stage row, lane row, axis chips, map-item cards, and evidence rail
- route SWOT and impact-effort through one shared matrix primitive with four cells, axis labels, certainty chips, and evidence rail
- only vary the payload and the selected map family; keep rendering primitives shared unless a map family truly needs a different geometry

## Multi-Format Rule

The same visual source should be adaptable for:

- slide visuals
- memo visuals
- dashboard views
- workshop boards
- customer-safe illustrations

## Quality Standard

A strong ProductOS visual should be:

- immediately understandable
- structurally elegant
- narratively aligned
- visually distinctive
- consistent with the message
