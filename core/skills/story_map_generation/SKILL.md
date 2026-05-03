# Story Map Generation

## 1. Purpose

Generate visual story maps (Jeff Patton style) from PRD scope and user stories — decomposing backbone activities into user tasks, arranging stories by priority, defining release slices, and rendering a visual execution plan.

## 2. Trigger / When To Use

story_pack complete. PRD scope defined. Sprint planning approaching. PM requests visual execution plan.

## 3. Prerequisites

- Relevant upstream artifacts for the skill domain
- Evidence sources (source note cards, research artifacts, competitive data)
- Defined scope from PM or mission context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `primary_input` | `object` | Upstream artifact schemas | Yes | Core input for the skill |
| `context` | `array[object]` | Supporting artifacts | No | Additional context |

## 5. Execution Steps

1. Extract backbone from PRD: Identify the major activities a user performs. These are the columns of the map. Order left to right chronologically.
2. Decompose into user tasks: Per backbone activity, identify discrete tasks. These are the rows.
3. Arrange stories: Per task, place individual user stories. Order top-to-bottom by priority (must-now at top, later at bottom).
4. Define release slices: Group stories into releases that deliver a complete, testable outcome. Each slice: name, target outcome, story_ids.
5. Assign sprint estimates: Optional — if capacity model data available, map to sprints.
6. Render visual map: Horizontal swimlanes layout. Color-coded by priority. Release slice boundaries marked.

## 6. Output Specification

Primary output: `story_map, story_pack, prd` artifact

## 7. Guardrails

- Backbone activities not MECE: Overlapping or incomplete activity set → flag. Backbone should cover the FULL user workflow.
- Stories not in priority order: Must-now story placed below later story → fix ordering.
- When to escalate: Release slice contains only 1 story — too granular to deliver an outcome. Backbone is >8 activities — decompose into sub-maps.

## 8. Gold Standard Checklist

- [ ] Backbone covers the complete user workflow without gaps
- [ ] Stories are in priority order within each task
- [ ] Release slices deliver complete, testable outcomes
- [ ] Visual map is generated from source data (not manually composed)
- [ ] Framework: Jeff Patton User Story Mapping
- [ ] Framework alignment: Jeff Patton User Story Mapping, agile release planning
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: story_decomposition_and_ambiguity_detection, prd_scope_boundary_check
- **Downstream skills**: developer_handoff_pack, sprint planning, roadmap_scenario_generation
- **Schemas**: story_map.schema.json, story_pack.schema.json, prd.schema.json

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full depth with qualitative exploration |
| 1→10 | Deep: comprehensive coverage |
| 10→100 | Standard: focused on highest-impact outputs |
| 100→10K+ | Focused: data-driven, portfolio-level |

## 12. Validation Criteria

- **Schema conformance**: validates against associated artifact schemas
- **Test file**: TBD in validation sprint
- **Example fixture**: associated `.example.json` files
