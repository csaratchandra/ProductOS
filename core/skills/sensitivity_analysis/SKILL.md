# Sensitivity Analysis

## 1. Purpose

Test how sensitive a decision recommendation is to changes in underlying assumptions — identifying which assumptions are critical (small change flips decision) and which are robust (decision holds across wide ranges).

## 2. Trigger / When To Use

After any decision analysis. When PM questions a recommendation's robustness. Before committing to high-impact decisions (impact >=4).

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

1. **Identify key assumptions**: List all assumptions underlying the current recommendation. Assumptions come from: cost estimates, timeline estimates, market growth rates, competitor behavior predictions, customer adoption curves.
2. **Prioritize assumptions**: Score each assumption on: impact on decision (if wrong, how much does the recommendation change?), uncertainty (how confident are we in this assumption?). Highest impact × uncertainty = test first.
3. **Define base values and test ranges**: Per assumption, document current base value. Define test range: realistic best case and worst case. Do not test impossible extremes.
4. **Run one-at-a-time sensitivity**: For each assumption, vary across the test range while holding others constant. At what value does the recommended option stop being the winner? This is the flip point.
5. **Classify sensitivity**: Robust (flips decision only at extreme/impossible values), Moderately sensitive (flips at realistic but unlikely values), Highly sensitive (flips at small, realistic changes — decision is fragile).
6. **Surface critical assumptions**: Assumptions classified as highly sensitive — these are the ones PM should monitor most closely. If any of these are wrong, the decision recommendation is wrong.
7. **Conclude**: State the boundary conditions within which the decision holds. "This decision is correct unless assumption X changes by more than Y, or assumption Z proves false." 

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Testing irrelevant assumptions**: Assumption being tested has no material impact on the decision outcome → response: deprioritize. Focus sensitivity budget on high-impact assumptions.
- **Failure: Over-narrow test ranges**: Ranges that are too tight miss the point of sensitivity analysis → response: ensure test ranges span at least ±50% from base for high-uncertainty assumptions.
- **When to escalate**: Multiple assumptions are classified as highly sensitive — the decision is fragile. Critical assumption uncertainty is high and no cheap learning method exists to reduce it.

## 8. Gold Standard Checklist

- [ ] All assumptions are explicitly stated — nothing is implicit or taken for granted
- [ ] Test ranges are realistic (not testing values that would never occur)
- [ ] Flip points are identified per assumption — at what value does the decision change?
- [ ] Critical assumptions are flagged for PM monitoring with specific triggers
- [ ] Conclusion clearly states: "This decision holds UNLESS [conditions]" 

- [ ] Framework alignment: validates against Sensitivity analysis (Saltelli, Global Sensitivity Analysis), tornado diagram methodology, Monte Carlo simulation principles
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: trade_off_analysis, decision_tree_construction, market_trend_extrapolation
- **Downstream skills**: premortem_analysis, decision communication, review trigger definition
- **Schemas**: decision_analysis.schema.json
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
- **Test file**: `tests/test_v10_sensitivity_analysis.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
