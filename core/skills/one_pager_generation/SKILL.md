# One-Pager Generation

## 1. Purpose

Generate single-page product summaries for sales enablement — value proposition, key metrics, customer quote, feature highlights, competitive differentiators, pricing summary, and CTA — print and digital ready.

## 2. Trigger / When To Use

Sales enablement content needed. Partner conversations. Buyer evaluation support. Quick reference for internal alignment.

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

1. Extract from messaging house: Load positioning, value props, and proof points.
2. Write value proposition: 2-3 sentence summary of what the product does, for whom, and why it is different.
3. Select key metrics: 2-4 compelling numbers (time saved, quality improvement, ROI).
4. Add customer quote: From beta testers, case studies, or generated from persona voice samples.
5. Icon + description feature highlights: 4-6 features with one-line descriptions. Benefit-first, not feature-first.
6. List competitive differentiators: 2-4 specific capabilities no competitor offers.
7. Summarize pricing: Starting price, tiers, free trial availability.
8. Add footer: Company name, compliance badges, website URL.
9. Ensure: Fits on one page. Scannable. Designed for both print (PDF) and digital (web page, email attachment).

## 6. Output Specification

Primary output: `one_pager` artifact

## 7. Guardrails

- Too dense for one page: Content overflows → cut to essential. One-pager is a hook, not a comprehensive document.
- Generic language: "Best-in-class AI tooling" → fix. Use specific capabilities.
- When to escalate: No customer quote available — one-pager feels impersonal. Pricing not finalized — cannot publish pricing summary.

## 8. Gold Standard Checklist

- [ ] Fits on single page (print or digital)
- [ ] Value proposition is specific, not generic
- [ ] Key metrics are compelling (time saved, $ saved, % improvement)
- [ ] Footer has compliance badges and contact info
- [ ] Framework: sales enablement one-pager standards, B2B SaaS marketing
- [ ] Framework alignment: Sales enablement, B2B SaaS marketing, one-pager design
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: messaging_house_construction, battle_card_generation, pricing_analysis
- **Downstream skills**: sales enablement, partner conversations, buyer evaluation
- **Schemas**: one_pager.schema.json

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
