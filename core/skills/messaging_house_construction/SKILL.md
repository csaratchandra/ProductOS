# Messaging House Construction

## 1. Purpose

Construct a complete messaging house with positioning statement, value propositions with proof points, tagline variants for different use cases, segment-specific messages, and competitive differentiation — validated against April Dunford's positioning framework.

## 2. Trigger / When To Use

PRD and persona work complete. Launch planning begins. PM requests marketing content generation. Before investor pitch deck.

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

1. Synthesize positioning from artifacts: Extract target customer, problem, solution, differentiation from PRD, persona cards, competitive matrix.
2. Write positioning statement: For [target] who [need], [product] is a [category] that [benefit]. Unlike [alternatives], we [differentiation].
3. Craft value propositions: 2-4 distinct value props. Each: headline, description, functional benefit, emotional benefit, linked proof points.
4. Source proof points: Extract from: beta tester feedback, competitive feature matrix, PM survey data, prototype quality scores. Each: specific claim with evidence type and ref.
5. Generate tagline variants: Hero (website), Social (shorter), Elevator pitch (descriptive). Variants for different use cases.
6. Write segment messages: Per target segment: key message, why-switch statement, primary benefit. Tailored to segment-specific concerns.
7. Define competitive differentiation: 2-3 sentences comparing ProductOS against named competitors. Specific capability gaps.
8. Document anti-claims: What ProductOS does NOT claim. Prevents over-promising.

## 6. Output Specification

Primary output: `messaging_house` artifact

## 7. Guardrails

- Positioning is generic: Any PM tool could use the same statement → reject. Must reference specific capabilities NOT offered by competitors.
- Proof points without evidence: "PMs love ProductOS" with no source → flag. Every proof point needs evidence type + ref.
- When to escalate: No competitive differentiation exists — product is at parity with all competitors. Requires strategy re-evaluation.

## 8. Gold Standard Checklist

- [ ] Positioning statement follows 'for X who need Y, Z is a...' structure
- [ ] Every value prop has both functional AND emotional benefit
- [ ] Proof points are specific and sourced (not "industry leading")
- [ ] Segment messages are tailored (not same message with segment name swapped)
- [ ] Anti-claims prevent over-promising
- [ ] Framework: April Dunford Obviously Awesome positioning, Andy Raskin strategic narrative
- [ ] Framework alignment: April Dunford Obviously Awesome, Andy Raskin strategic narrative, Bobette Kyle positioning framework
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: persona_narrative_generation, competitive_feature_matrix, pricing_analysis, win_loss_analysis
- **Downstream skills**: battle_card_generation, investor_content_generation, blog_post_brief_generation, one_pager
- **Schemas**: messaging_house.schema.json

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
