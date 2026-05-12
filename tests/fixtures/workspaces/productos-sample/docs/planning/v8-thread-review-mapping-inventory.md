# V8 Thread Review Mapping Inventory

Status: draft
Audience: PM, engineering, design
Owner: ProductOS PM
Updated At: 2026-04-09

## Purpose

This file defines the current explicit mapping contract for the thread-review surface.

Each section must declare:

- selector key
- expected lifecycle stage coverage
- preferred artifact types
- fallback policy
- backing mode rules

## Backing Modes

- `artifact_backed`: at least one canonical artifact payload is present and used as the primary summary source
- `lifecycle_fallback`: no primary artifact payload is available, but the section is still rendered from lifecycle state and stage summaries
- `deferred`: the stage is explicitly `not_started` and the section is shown to preserve end-to-end visibility without implying proof

## Section Inventory

### `problem_brief`

- Section id: `problem`
- Stages: `problem_framing`
- Preferred artifacts:
  - `problem_brief`
- Fallback:
  - lifecycle stage summary for `problem_framing`

### `segment_and_persona_pack`

- Section id: `segments_personas`
- Stages: `segmentation_and_personas`
- Preferred artifacts:
  - `segment_map`
  - `persona_pack`
- Fallback:
  - lifecycle stage summary for `segmentation_and_personas`

### `research_context`

- Section id: `market_context`
- Stages: `research_synthesis`
- Preferred artifacts:
  - `research_notebook`
  - `research_brief`
  - `competitor_dossier`
  - `market_analysis_brief`
- Fallback:
  - lifecycle stage summary for `research_synthesis`

### `concept_brief`

- Section id: `concept`
- Stages: `concept_shaping`
- Preferred artifacts:
  - `idea_record`
  - `concept_brief`
- Fallback:
  - lifecycle stage summary for `concept_shaping`

### `prototype_record`

- Section id: `prototype`
- Stages: `prototype_validation`
- Preferred artifacts:
  - `prototype_record`
  - `ux_design_review`
- Fallback:
  - lifecycle stage summary for `prototype_validation`

### `prd`

- Section id: `prd`
- Stages: `prd_handoff`
- Preferred artifacts:
  - `prd`
- Fallback:
  - lifecycle stage summary for `prd_handoff`

### `delivery_scope`

- Section id: `delivery`
- Stages:
  - `story_planning`
  - `acceptance_ready`
- Preferred artifacts:
  - `story_pack`
  - `acceptance_criteria_set`
- Fallback:
  - lifecycle stage summaries for `story_planning` and `acceptance_ready`

### `release_readiness`

- Section id: `release_readiness`
- Stages: `release_readiness`
- Preferred artifacts:
  - `release_readiness`
- Fallback:
  - lifecycle stage summary for `release_readiness`

### `release_note`

- Section id: `launch`
- Stages: `launch_preparation`
- Preferred artifacts:
  - `release_note`
- Fallback:
  - lifecycle stage summary for `launch_preparation`

### `outcome_review`

- Section id: `outcome_review`
- Stages: `outcome_review`
- Preferred artifacts:
  - `outcome_review`
- Fallback:
  - lifecycle stage summary for `outcome_review`

## Current Notes

- Adoption-generated threads currently mark:
  - `problem`, `segments_personas`, `market_context`, `concept`, `prd` as `artifact_backed`
  - `prototype` as `lifecycle_fallback`
  - `delivery`, `release_readiness`, `launch`, `outcome_review` as `deferred`
- Reference workspace V7.3 lifecycle threads should render most downstream sections as `artifact_backed`

## Next Hardening Target

The next code step should move the mapping rules above into a dedicated runtime mapping layer so the selectors and fallback policy are not distributed across one large runtime file.
