# Trade-Off Analysis

## 1. Purpose

Compare multiple options across weighted criteria to surface the highest-expected-value path forward, explicitly naming what is gained and what is lost.

## 2. Trigger / When To Use

PM faces a decision with >=2 mutually exclusive options. Prioritization requires comparing alternatives. Leadership or stakeholder alignment requires quantified rationale for a recommendation.

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

1. **Frame the decision**: Define the decision question precisely. What is being decided? Who is affected? What are the stakes and timeline pressure?
2. **Articulate options**: List 2-4 materially different options. Options must represent genuinely different approaches — not variations on the same theme. Each: description, expected outcome, cost, timeline, risk level.
3. **Define weighted criteria**: Identify 3-6 evaluation criteria. Each: name, weight (sum = 100), type (must_have, quantitative, qualitative). Must-haves are binary gates — if an option fails a must-have, it is eliminated regardless of score.
4. **Score each option**: Per criterion, assign score (1-10) for each option. Score based on evidence, not preference. Document rationale per score.
5. **Compute weighted totals**: Multiply scores by criterion weights. Sum per option. Rank options by total.
6. **Surface key trade-offs**: Identify the single most important trade-off: what does the recommended option sacrifice? What is lost by not choosing the runner-up?
7. **Generate recommendation**: Recommend the highest-scoring option. Document rationale, key trade-offs, and what is lost.
8. **Validate**: Check for confirmation bias — did the scoring conveniently produce the PM's pre-existing preference? If scoring difference is <10%, the options may be too similar — reconsider if this is a real trade-off.

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Scoring reflects preference, not evidence**: Detection criteria: PM's stated preferred option scores highest by a wide margin while evidence is thin → response: flag potential confirmation bias. Request independent evidence for each score.
- **Failure: Criteria are not MECE**: Two criteria measure the same thing (e.g., "speed" and "time to market") → response: merge overlapping criteria. Re-weight.
- **Failure: Options are not materially different**: Two options differ only on timeline (now vs later) with same outcome → response: this is a timing decision, not a trade-off. Route to timing analysis.
- **When to escalate**: All options score within 15% of each other — no clear winner. Must-have criterion eliminates all options. Top-scoring option has high risk level and moderate+ uncertainty.

## 8. Gold Standard Checklist

- [ ] Options are materially different — a stakeholder should be able to argue for any of them credibly
- [ ] Criteria weights sum to 100 and are justified
- [ ] Every score has a rationale grounded in evidence, not intuition
- [ ] Recommendation explicitly names what is LOST by choosing it — no option is perfect
- [ ] If scoring difference between top options is <10%, this is flagged as a close decision requiring PM judgment override

- [ ] Framework alignment: validates against Kepner-Tregoe decision analysis, Multi-Criteria Decision Analysis (MCDA), decision matrix methodology
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: evidence_extraction, decision_packet_synthesis, competitive_shift_analysis, sensitivity_analysis
- **Downstream skills**: decision_tree_construction, premortem_analysis, roadmap_scenario_generation, stakeholder communication
- **Schemas**: decision_analysis.schema.json, strategy_option_set.schema.json
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
- **Test file**: `tests/test_v10_trade_off_analysis.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
