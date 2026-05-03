# Investor Content Generation

## 1. Purpose

Generate investor-grade pitch deck (12 slides) and investor memo with executive summary, problem, solution, market opportunity, competitive advantage, traction, team, financials, use of funds, and key risks.

## 2. Trigger / When To Use

Funding round approaching. PM requests investor materials. Strategic review requires investment justification.

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

1. Gather source data: Market sizing, competitive analysis, PESTLE, pricing model, team data, traction metrics, financial projections.
2. Build pitch deck structure: 12 slides — Title, Problem, Solution, Why Now, Market Size, Product, Traction, Business Model, Competition, Team, Financials, Ask.
3. Write per slide: Action title (insight, not topic label), key message, supporting data, source.
4. Build investor memo: Executive summary (standalone — investor can read only this). Sections: Problem, Solution, Market, Competitive Advantage, GTM, Traction, Team, Financials, Use of Funds, Risks.
5. Validate claims: Every claim must be defensible. "We will capture 10% of market" → requires adoption model. "No competitor offers X" → requires competitive matrix evidence.
6. Link evidence: Every key claim cites a source artifact (market sizing, competitive matrix, PM survey, beta test results).

## 6. Output Specification

Primary output: `investor_pitch_deck, investor_memo` artifact

## 7. Guardrails

- Inflated market claims: "We are targeting a $100B market" with 0.1% relevance → flag. Market sizing must be honest about addressable portion.
- Missing risk section: Investor memo without risks → block. Investors expect risks to be acknowledged, not hidden.
- When to escalate: Financial projections are entirely speculative (no historical data). Competitive advantage claims contradict competitive feature matrix.

## 8. Gold Standard Checklist

- [ ] Every slide has an action title, not a topic label
- [ ] Market sizing shows TAM/SAM/SOM with methodology
- [ ] Competitive advantage claims are supported by evidence
- [ ] Investor memo executive summary is standalone-readable
- [ ] Risks are acknowledged — not hidden
- [ ] Framework: Sequoia pitch deck structure, Y Combinator investment memo format
- [ ] Framework alignment: Sequoia pitch deck, Y Combinator memo format, venture capital best practices
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: messaging_house_construction, pricing_analysis, market_trend_extrapolation, competitive_feature_matrix
- **Downstream skills**: investor meetings, board presentations, strategic reviews
- **Schemas**: investor_pitch_deck.schema.json, investor_memo.schema.json

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
