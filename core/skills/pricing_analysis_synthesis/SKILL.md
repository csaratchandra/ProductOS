# Pricing Analysis Synthesis

## 1. Purpose

Synthesize competitor pricing data, willingness-to-pay research, unit economics, and pricing model options into a comprehensive pricing recommendation with risk assessment and implementation roadmap.

## 2. Trigger / When To Use

New competitor pricing detected. Market entry or product launch planning. PM requests pricing strategy review. Before investor content generation (pitch deck, memo).

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

1. **Gather competitor pricing**: From competitive radar state and competitor dossier, collect all known competitor pricing data. Include: model type, tiers, features per tier, last updated dates.
2. **Build competitor pricing matrix**: Structure competitors side-by-side with tier comparison. Flag gaps (competitor includes feature we don't have, or vice versa). Identify pricing trends (are competitors moving upmarket? downmarket?).
3. **Synthesize willingness-to-pay**: From customer interviews, surveys, and research, estimate WTP per segment. Conservative approach: use the lower bound of the range for planning. Document synthesis method and evidence gaps.
4. **Analyze price sensitivity**: Apply appropriate method (Van Westendorp, Gabor-Granger, conjoint analysis synthesis, or research-based estimate). Identify optimal price point and sensitivity zones.
5. **Model unit economics**: Per segment: CAC, LTV, LTV/CAC ratio, payback period, gross margin. Identify which segments are profitable and which require cross-subsidy or are acquisition plays.
6. **Design pricing model options**: Generate 2-3 distinct pricing models (subscription tiers, usage-based, hybrid, freemium). Per model: pros, cons, best-fit segment, revenue projection.
7. **Build ROI calculator specification**: Define calculator inputs (what the customer enters), outputs (what value they see), and value proposition narrative.
8. **Generate recommendation**: Recommend specific model + starting price + tier structure. Document rationale, risks, and next implementation steps.

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Competitor pricing data is stale**: Pricing data >90 days old for a fast-moving competitor → response: mark analysis as time-sensitive. Recommend competitive scan refresh before decision.
- **Failure: WTP based on <5 data points**: Willingness-to-pay estimates from too few sources → response: mark WTP as low confidence. Surface specific N needed for moderate confidence.
- **When to escalate**: WTP estimates are below competitor pricing — cannot compete on price without margin sacrifice. All pricing models project revenue below sustainability threshold. Enterprise segment WTP is below minimum viable price while startup WTP is too low to cover CAC.

## 8. Gold Standard Checklist

- [ ] Competitor pricing data includes last_updated timestamps — freshness is explicit
- [ ] WTP estimates are per-segment with ranges, not single-point estimates
- [ ] Price sensitivity method is named and appropriate for available data
- [ ] Pricing model options are materially different — not variations on "charge X/month"
- [ ] Unit economics assessment is honest — unprofitable segments are labeled as such
- [ ] ROI calculator spec is concrete — a developer could build it from the specification
- [ ] Framework: Van Westendorp Price Sensitivity Meter, value-based pricing (Nagle/Hogan), SaaS pricing strategy

- [ ] Framework alignment: validates against Van Westendorp PSM, value-based pricing (Nagle, Hogan), SaaS pricing strategy, unit economics modeling
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: competitive_radar_scan, market_sizing_reasoning_check, persona_evidence_synthesis
- **Downstream skills**: pricing_model_design, investor_content_generation, battle_card_generation
- **Schemas**: pricing_analysis.schema.json, competitor_dossier.schema.json
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
- **Test file**: `tests/test_v10_pricing_analysis_synthesis.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
