# Prototype Quality Evaluation

## 1. Purpose

Evaluate generated prototypes against all quality dimensions — visual design, interaction depth, IA clarity, accessibility compliance, state completeness, data realism, user test readiness — producing a scored quality report.

## 2. Trigger / When To Use

New prototype generated. Prototype iterated after feedback. Before prototype presentation to stakeholders.

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

1. Load prototype: Open generated HTML prototype. Verify it renders correctly across all target devices.
2. Score visual quality: Polish, professionalism, aesthetic appeal. Consistency with design tokens. Typography hierarchy. Spacing rhythm. Color harmony.
3. Score interaction depth: Ease of use, flow clarity, micro-interactions, form behavior, error handling, loading states, feedback mechanisms.
4. Score IA clarity: Information organization, discoverability, navigation patterns, label clarity, progressive disclosure.
5. Auto-check accessibility: Run WCAG 2.1 AA compliance scan. Contrast ratios, ARIA labels, keyboard navigation, heading hierarchy, alt text. Generate violation list.
6. Verify state completeness: Every screen has loading, empty, normal, error, edge case states represented.
7. Score data realism: Is data domain-appropriate? Any lorem ipsum? Are numbers, dates, names realistic for the target domain?
8. Assess user test readiness: Can a PM run a moderated user test with this prototype today? Are task scenarios clear? Is the moderator guide complete?
9. Generate quality report: Per dimension: score (1-10), specific findings, improvement items. Overall score. Recommendation: promote, iterate, or rework.
10. Link to prototype record: Update prototype record with quality report reference.

## 6. Output Specification

Primary output: `prototype_quality_report, prototype_record` artifact

## 7. Guardrails

- Accessibility violations are blockers: WCAG AA failures → dimension score capped at 3/10. Must fix before stakeholder presentation.
- State coverage below 80%: More than 20% of screens missing required states → overall score capped at 5/10.
- When to escalate: Overall score <5/10 — prototype needs significant rework. Accessibility score <3/10 — blocks any external sharing.

## 8. Gold Standard Checklist

- [ ] Every dimension has a specific score (not "good" / "bad")
- [ ] Accessibility violations listed with specific WCAG criteria references
- [ ] Improvement items are actionable (not "make it better")
- [ ] Recommendation is clear: promote, iterate, or rework
- [ ] Framework: WCAG 2.1 AA, SUS (System Usability Scale), heuristic evaluation (Nielsen)
- [ ] Framework alignment: WCAG 2.1 AA, SUS (System Usability Scale), NN/g heuristic evaluation, design quality rubrics
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: prototype_html_generation
- **Downstream skills**: prototype_comparison_matrix, pm_selection
- **Schemas**: prototype_quality_report.schema.json, prototype_record.schema.json

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
