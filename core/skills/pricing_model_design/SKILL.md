# Pricing Model Design

## 1. Purpose

Design and compare multiple pricing model options (subscription, usage-based, hybrid, freemium, tiered) with detailed pros/cons, segment fit analysis, revenue projections, feature-tier mapping, and implementation considerations.

## 2. Trigger / When To Use

After pricing_analysis synthesis provides competitor context and WTP estimates. Product launch or replatforming requires pricing model selection. Revenue modeling needed for investor or board materials.

## 3. Prerequisites

- Current product strategy context (strategy option set or market strategy brief)
- Relevant evidence artifacts (competitive intelligence, market data, persona research) for the decision domain
- Decision question or trade-off scenario defined by PM
- (Recommended) PESTLE analysis for environmental context
- (Recommended) Hypothesis portfolio for aligned hypothesis context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `decision_question` | `string` | PM input | Yes | The decision to be analyzed |
| `options` | `array[object]` | PM input + artifact references | Yes | Options to evaluate (min 2) |
| `context_artifacts` | `array[object]` | Various schemas | Yes | Evidence context for the decision |
| `criteria` | `array[object]` | PM input | Yes | Decision criteria with weights |

## 5. Execution Steps

1. **Review pricing analysis context**: Confirm WTP estimates, competitor landscape, and unit economics from pricing_analysis synthesis.
2. **Generate model options**: Design 2-4 distinct models. Each model: type (subscription, usage-based, hybrid, etc.), tier structure with prices and features, pros, cons, best-fit segments, annual revenue projection.
3. **Map features to tiers**: Per model, define what goes in each tier. Follow value-based tiering: features escalate based on value delivered, not arbitrary bundling. Enterprise features (SSO, audit, SLA) always in top tier.
4. **Validate against segments**: For each model, check alignment with segment WTP and behavior. If a model's pricing exceeds a segment's WTP range, flag it — either model or target segment needs adjustment.
5. **Project revenue**: Model revenue under conservative adoption assumptions. Show 3-year trajectory if applicable. Flag if revenue projections rely on optimistic adoption assumptions.
6. **Recommend model**: Based on segment fit, revenue projection, competitive positioning, and implementation complexity. Justify the recommendation with specific trade-offs.
7. **Implement tier spec**: If model selected, produce executable tier definition that feeds into pricing page, billing system, and sales enablement.

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Tiers are arbitrary bundles**: Features grouped by convenience, not value delivery → response: require value-based tier rationale. Each tier should answer: "who is this for and what job does it do?"
- **Failure: Revenue projections rely on hero numbers**: "If we capture 10% of TAM" with no adoption model → response: require bottom-up adoption model (conversion rates, expansion rates, churn assumptions).
- **When to escalate**: All models project revenue below sustainability threshold. No model fits both enterprise and startup segments simultaneously — requires trade-off decision on which segment to prioritize.

## 8. Gold Standard Checklist

- [ ] Each model option has 2+ pros AND 2+ cons — honest about trade-offs
- [ ] Feature-tier mapping is value-based, not arbitrary
- [ ] Revenue projections have explicit adoption assumptions (not "10% of market")
- [ ] Segment fit analysis per model — which segments are well-served vs underserved?
- [ ] Implementation complexity is acknowledged — "usage-based pricing requires metering infrastructure" 

- [ ] Framework alignment: validates against SaaS pricing (Patrick Campbell/ProfitWell), tiered pricing strategy, value-based tiering
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: pricing_analysis_synthesis, segment_priority_scoring, market_sizing_reasoning_check
- **Downstream skills**: messaging_house_construction, investor_content_generation, battle_card_generation
- **Schemas**: pricing_analysis.schema.json
- **Related workflows**: `core/workflows/decision-intelligence/`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements |
|---|---|---|
| 0→1 | Exhaustive: full analysis with all decision types. Deep qualitative context. Multiple scenario modeling. | Multi-source evidence on every assumption. Expert input required for high-impact decisions. |
| 1→10 | Deep: full analysis. Quantitative scoring where data exists. 2+ scenarios tested. | Mix of qualitative + any available quantitative data. |
| 10→100 | Standard: core analysis types only. Data-driven scoring prioritized. | Quantitative data preferred. Statistical rigor where possible. |
| 100→10K+ | Focused: highest-impact decisions only. Portfolio-level analysis. | Quantitative data required. Statistical models for uncertainty. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/decision_analysis.schema.json`
- **Test file**: `tests/test_v10_pricing_model_design.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
