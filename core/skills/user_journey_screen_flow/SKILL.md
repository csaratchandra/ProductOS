# User Journey Screen Flow

## 1. Purpose

Map user interaction flow at screen level with per-step cognitive load assessment, accessibility evaluation, error recovery paths, first-time vs returning user variants, multi-device continuity modeling, offline scenario planning, collaboration context, notification handling, power user shortcut definition, and visual flow rendering spec — producing screen-level UX specifications ready for prototyping.

## 2. Trigger / When To Use

- `customer_journey_map` complete for target persona — screen flow zooms into specific stages
- `concept_brief` ready for prototyping — need detailed interaction specification
- PM requests detailed UX specification for a key workflow
- Accessibility audit needed before development handoff
- Design team needs interaction-level detail for a new feature

## 3. Prerequisites

- `customer_journey_map` identifying the journey stage(s) to detail
- `persona_narrative_card` or `persona_archetype_pack` for persona behavior context
- Use case defined (primary or secondary from persona card)
- (Recommended) `empathy_map` for cognitive and emotional context
- (Optional) Existing design system or `design_token_set`

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `journey_context` | `object` | `customer_journey_map.schema.json` | Yes | Which stage(s) are being detailed |
| `persona_context` | `object` | `persona_narrative_card.schema.json`, `persona_archetype_pack.schema.json` | Yes | Behavior, tools, preferences |
| `use_case` | `object` | From persona_card.use_cases | Yes | Which use case the flow serves |

## 5. Execution Steps

1. **Scope the flow**: Select specific journey stage(s) and use case to detail. Define start trigger and end state. Identify device context.
2. **Decompose into steps**: Break the interaction into 3-15 discrete steps. Each step: trigger (what starts it), user action, user thought, system response. Steps must be concrete — a wireframe could be drawn from each description.
3. **Score cognitive load per step**: low (automatic, familiar), medium (requires attention), high (requires focus/decision), very_high (complex, error-prone). Identify the highest-load steps.
4. **Define time expectations**: Per step, how long should this take? Informed by persona behavior and interaction complexity.
5. **Identify potential errors per step**: What can go wrong at each step? User errors (wrong input, wrong path) and system errors (timeout, failure). Each error needs a detection mechanism and recovery path.
6. **Accessibility assessment**: Per step, note WCAG considerations. Build overall accessibility score: screen reader findings, keyboard navigation, contrast. Identify improvement items.
7. **Model first-time vs returning experience**: How does this flow differ for a new user vs an experienced user? What's the progressive disclosure strategy?
8. **Address multi-device continuity**: If flow spans devices, how does state persist? What layout differences exist?
9. **Plan for offline, collaboration, notifications**: What happens without connectivity? What if multiple users are involved? What notifications fire during the flow?
10. **Define power user shortcuts**: Keyboard shortcuts, command palette actions, templates and presets for experienced users.
11. **Design visual flow spec**: Configure rendering: screens visible, sentiment overlay, annotations, rendering mode.
12. **Assemble user_journey_map artifact**: Link evidence refs. Validate completeness.

## 6. Output Specification

- `user_journey_map` → `core/schemas/artifacts/user_journey_map.schema.json`

## 7. Guardrails

- **Steps too vague for prototyping**: A step description is "user does something" or "system responds" → reject. Every step must be specific enough for a prototype to implement.
- **Accessibility gaps ignored**: Accessibility assessment marked compliant but individual steps have no accessibility_notes → flag. Compliance requires per-step consideration.
- **When to escalate**: Cognitive load profile is "overwhelming" — flow is too complex and needs redesign. Accessibility score is "major_gaps" or "inaccessible" — blocks development handoff.

## 8. Gold Standard Checklist

- [ ] Every step has: trigger, user_action, system_response, cognitive_load, time_expected, potential_errors
- [ ] Error paths include detection mechanism AND recovery path — not just error description
- [ ] First-time vs returning experience are materially different descriptions
- [ ] Accessibility notes exist per step (not just overall assessment)
- [ ] Power user shortcuts are specific (actual keys or commands, not "add shortcuts someday")
- [ ] Framework: NN/g UX journey mapping, WCAG 2.1 AA, Don Norman's interaction design principles

## 9. Examples

See `core/examples/artifacts/user_journey_map.example.json`

## 10. Cross-References

- **Upstream**: `customer_journey_synthesis`, `persona_narrative_generation`, `empathy_map_generation`
- **Downstream**: `prototype_html_generation`, `api_contract_generation`, `non_functional_requirement_extraction`
- **Schemas**: `user_journey_map.schema.json`, `customer_journey_map.schema.json`, `empathy_map.schema.json`

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full 12+ step flow with all cross-cutting concerns. Deep qualitative focus. |
| 1→10 | Deep: 8-12 step flow. Accessibility depth. First-time experience prioritized. |
| 10→100 | Standard: 6-8 step flow. Error paths + accessibility focus. Power user shortcuts included. |
| 100→10K+ | Focused: 4-6 step flow. Error recovery + accessibility only. Quantitative UX metrics preferred. |

## 12. Validation Criteria

- **Schema**: `user_journey_map.schema.json`
- **Test**: `tests/test_v10_user_journey.py`
- **Example**: `core/examples/artifacts/user_journey_map.example.json`