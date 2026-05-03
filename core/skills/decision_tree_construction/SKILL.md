# Decision Tree Construction

## 1. Purpose

Map complex decisions with sequential branches, probabilities, and outcomes into a structured evaluable tree — calculating expected values and identifying the optimal path through uncertainty.

## 2. Trigger / When To Use

Decision involves multiple sequential choices or uncertain outcomes. Decision impact score >=4 (high stakes). PM wants to model uncertainty with explicit probabilities.

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

1. **Define root decision**: Identify the initial decision node. What choice opens the tree?
2. **Map branches**: For each possible action, map the chain of events: decisions (controllable choices), chance nodes (uncertain outcomes), outcomes (terminal states with values).
3. **Assign probabilities**: Per chance node, assign probability for each branch. Probabilities from the same node must sum to 1.0. Base on evidence, not intuition — cite probability sources.
4. **Value outcomes**: Assign outcome values to terminal nodes. Use consistent units (revenue impact, PM hours saved, market share points). Can be negative for undesirable outcomes.
5. **Calculate expected values**: EV = Σ (outcome_value × probability) for each path. Roll back from terminals to root. Compare EVs to identify optimal path.
6. **Conduct one-way sensitivity**: Test which probability estimates most affect the EV comparison. If a 10% change in one probability flips the recommended path, flag it.
7. **Recommend path**: Recommend the highest-EV path. Acknowledge that EV is a decision input, not a decision — low-probability catastrophic outcomes may override EV reasoning.

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Probabilities from intuition, not data**: Detection criteria: probability sources not cited → response: mark analysis as speculative. Strip probabilities without evidence basis.
- **Failure: Outcomes valued inconsistently**: One outcome in dollars, another in users → response: convert all outcomes to common unit. Flag if conversion requires significant assumptions.
- **When to escalate**: EV difference between top two paths is <15% — close call. Catastrophic outcome has >5% probability on any path.

## 8. Gold Standard Checklist

- [ ] All chance node probabilities sum to 1.0
- [ ] Probability sources cited (even if estimates, source is documented)
- [ ] Outcome values use consistent units
- [ ] Expected values calculated correctly (manually verifiable)
- [ ] Sensitivity: which probability has the most impact on the recommendation?

- [ ] Framework alignment: validates against Decision tree analysis (Raiffa, Decision Analysis), expected value framework, Bayesian decision theory
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: trade_off_analysis, sensitivity_analysis, evidence_extraction
- **Downstream skills**: premortem_analysis, roadmap_scenario_generation, investment/allocation decisions
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
- **Test file**: `tests/test_v10_decision_tree_construction.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
