# Premortem Analysis

## 1. Purpose

Assume a decision has failed 6-12 months from now and work backward to identify the most likely failure causes — surfacing risks, early warning indicators, and reversal triggers before commitment.

## 2. Trigger / When To Use

Before any major bet (decision impact >=4). Before irreversible decisions. During strategy review or roadmap planning. After a recommended decision is identified but before PM commits.

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

1. **Assume failure**: Start with the premise: "It is 12 months from now. This decision was wrong. We are looking back at why." This mindset shifts from justifying the decision to stress-testing it.
2. **Generate failure scenarios**: Brainstorm 2-4 distinct ways the decision could fail. Scenarios should be: specific (names concrete events, not "things go wrong"), plausible (could realistically happen), varied (different failure modes, not variations on one theme). For each: probability, impact if occurs, leading indicators that would have warned us.
3. **Identify early warning indicators**: For each scenario, what signals would we have seen early? Specific metrics, market signals, team feedback, competitive moves. Indicators should be observable, not after-the-fact analysis.
4. **Define reversal triggers**: Based on warning indicators, define explicit conditions under which the decision should be reconsidered or reversed. "Pull the plug if: [specific condition]." Triggers must be binary (yes/no) or threshold-based — not subjective judgment calls.
5. **Assess reversibility**: If a reversal trigger fires, can we actually reverse? At what cost? By when? If the decision is irreversible after a certain milestone, that milestone becomes a hard deadline for the reversal decision.
6. **Recommend safeguards**: Based on failure scenarios, what preemptive actions reduce the probability or impact of each failure mode?

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Failure scenarios are vague**: "Things could go wrong" or "The market might not respond" → detection criteria: scenario has no specific events → response: reject. Demand concrete failure narratives.
- **Failure: Warning indicators are unobservable**: "Customer satisfaction drops" with no defined measurement → response: require specific metric and measurement method. "NPS drops below 30 for 2 consecutive quarters" is observable.
- **Failure: Reversal triggers are subjective**: "Revisit if it doesn't feel right" → response: require binary or threshold-based triggers. No judgment-call triggers.
- **When to escalate**: Catastrophic failure scenario has probability >=15% — PM must explicitly accept this risk. No reversal path exists for a likely failure scenario — PM must decide: accept irreversibility or choose a reversible option.

## 8. Gold Standard Checklist

- [ ] At least 2 materially different failure scenarios (not "bad market" and "worse market")
- [ ] Each scenario has specific leading indicators that are MEASURABLE before failure
- [ ] Reversal triggers are binary or threshold-based — no subjective triggers
- [ ] Reversibility is assessed honestly — if irreversible, this is stated explicitly
- [ ] Safeguards are actionable and costed — "add more testing" is not a safeguard without specifics
- [ ] Framework: premortem methodology (Gary Klein), prospective hindsight, red teaming

- [ ] Framework alignment: validates against Premortem (Gary Klein), prospective hindsight, risk management frameworks, decision reversibility analysis
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: trade_off_analysis, sensitivity_analysis, decision_tree_construction
- **Downstream skills**: decision communication, risk management planning, stakeholder brief generation
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
- **Test file**: `tests/test_v10_premortem_analysis.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
