# Prototype HTML Generation

## 1. Purpose

Generate interactive HTML prototypes with complete state coverage (loading, empty, normal, error, edge, onboarding), responsive design, WCAG 2.1 AA accessibility, realistic data, PM-editable overlays, annotation layers, shareable hosting, and user testing kits.

## 2. Trigger / When To Use

prototype_generation_plan approved. concept_brief reached validated status. PM requests design variant exploration.

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

1. Load generation plan: Extract variant count, differentiation axes, fidelity target, state coverage requirements, accessibility target, device targets.
2. Set up design token environment: Load design_token_set. Apply colors, typography, spacing, shadows, radii as CSS custom properties.
3. Generate component library: Create reusable components (buttons, cards, tables, forms, modals, navigation, alerts) from design tokens.
4. Build variant scaffolds: Per variant, create page structure with layout, navigation, and information architecture differentiated per plan axes.
5. Implement state variants: Per screen: loading state (skeleton/spinner), empty state (first-use messaging), normal state (populated with realistic data), error state (what went wrong + recovery), edge case (extreme data, unusual input), onboarding (first-run wizard/walkthrough).
6. Populate realistic data: No lorem ipsum. Every name, number, date, label is domain-appropriate. Use AI-generated realistic datasets.
7. Add accessibility: Semantic HTML. ARIA labels. Keyboard navigation (tab order, focus indicators). Screen reader announcements. Color contrast >=4.5:1 for text, >=3:1 for large text.
8. Build interaction layer: Click handlers, form validation, state transitions, micro-interactions (hover, active, focus), loading animations, success/error toasts.
9. Add PM features: Edit overlay (click any text to modify). Annotation layer (click to add note). A/B toggle (if multiple variants within a prototype).
10. Ensure responsive: Mobile (360px), Tablet (768px), Desktop (1440px). Breakpoints with appropriate layout changes.
11. Generate user test kit: Task scenarios for testers, moderator guide, observation template.
12. Deploy: Shareable URL or self-contained HTML file. Prototype record updated with all metadata.
13. Validate: Run prototype_quality_evaluation against all dimensions.

## 6. Output Specification

Primary output: `prototype_generation_plan, design_token_set, prototype_comparison_matrix` artifact

## 7. Guardrails

- Prototype too generic: Looks like a UI kit, not a product → reject. Must feel like a real product with domain-specific content.
- Accessibility violations: WCAG AA failures detected → block. Prototype must pass accessibility auto-check before delivery.
- State coverage incomplete: Missing error or empty state → block. Every screen needs all states.
- When to escalate: Prototype quality score <3/5 on any dimension. Accessibility target (AA) not met.

## 8. Gold Standard Checklist

- [ ] All 6 state variants present per screen across all variants
- [ ] WCAG 2.1 AA auto-validation passes (contrast, labels, keyboard, ARIA)
- [ ] Realistic data — no lorem ipsum anywhere
- [ ] PM-edit and annotation layers functional
- [ ] Responsive at 3 breakpoints
- [ ] User test kit included
- [ ] Framework: Material Design 3, WCAG 2.1 AA, Nielsen Norman interaction design heuristics
- [ ] Framework alignment: Material Design 3, WCAG 2.1 AA, NN/g interaction design heuristics, responsive web design
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: prototype_generation_plan, design_token_set, user_journey_map, persona_narrative_card
- **Downstream skills**: prototype_quality_evaluation, prototype_comparison_matrix, pm_selection
- **Schemas**: prototype_generation_plan.schema.json, design_token_set.schema.json, prototype_comparison_matrix.schema.json

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
