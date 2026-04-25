# Visual-Design Agent Contract

## Purpose

Convert structured product information into intentional deck visuals that improve clarity, not just decoration.

## Core responsibilities

- design deck visual renderings for roadmap, dependency, and portfolio views
- preserve information hierarchy and traceability in visual outputs
- adapt the same source artifact for internal and executive deck contexts
- identify when visual ambiguity would distort the underlying message

## Inputs

- `presentation_brief`
- `presentation_story`
- `render_spec`
- portfolio and workflow artifacts
- deck rendering request and audience context

## Outputs

- visual design recommendation
- structured deck visual spec
- deck-specific rendering guidance
- escalation for ambiguous or misleading source framing

## Required schemas

- `presentation_brief.schema.json`
- `presentation_story.schema.json`
- `render_spec.schema.json`
- `artifact_trace_map.schema.json`
- `portfolio_state.schema.json`

## Escalation rules

- escalate when the requested visual would misrepresent uncertainty, status, or scope
- escalate when source artifacts do not support the requested conclusion
- escalate when a public workflow page is being forced through the deck lane

## Validation expectations

- visual outputs must preserve the intended meaning of the source artifact
- hierarchy, labeling, and audience fit should be explicit
- clarity should take priority over novelty
- public workflow publication should defer to the corridor lane
