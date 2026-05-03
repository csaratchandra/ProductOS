# Hypothesis Portfolio Management

## 1. Purpose

Structure a portfolio of linked hypotheses with tree decomposition (strategic → tactical → testable), interdependency mapping, kill criteria definition, risk prioritization (impact × uncertainty), and auto-routing into prototype generation for highest-risk hypotheses.

## 2. Trigger / When To Use

Discovery phase producing multiple hypothesis candidates. Strategy review requires uncertainty mapping. Before prototype or experiment planning. After PESTLE and persona synthesis surface assumptions that need validation.

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

1. **Decompose into tree**: Start from strategic hypotheses (product-level, existential). Break each into tactical hypotheses (specific capability or segment bets). Further decompose into testable hypotheses (concrete, falsifiable, small-scope).
2. **Write falsifiable statements**: Each hypothesis: clear statement that can be proven wrong. "We believe [X] will result in [Y] for [persona]. We will know this is true when [measurable condition]." Vague hypotheses ("PMs want better tools") are rejected.
3. **Define kill criteria**: Per hypothesis: what evidence would kill this hypothesis? Kill criteria must be specific and measurable. Example: "Kill if <60% of PMs rank this feature in top-5 needs in survey of N>=20."
4. **Map interdependencies**: Which hypotheses depend on others? If H1 is invalidated, H2-H5 (which depend on H1) become irrelevant — flag for cascading impact. Mutually exclusive hypotheses: both cannot be true — validation outcome determines which path.
5. **Score risk priority**: Per hypothesis: impact_if_true × uncertainty. Risk priority score = f(impact, uncertainty, interdependency criticality). Highest scores are hypotheses where: the impact of being wrong is high AND our uncertainty is high — these need validation first.
6. **Route to prototypes/experiments**: Hypotheses with risk priority >=80 → auto-route to prototype generation plan. Hypotheses with risk priority 60-79 → auto-route to experiment design. Rationale provided per route.
7. **Build portfolio summary**: Total hypotheses, by status (draft/planned/in_test/validated/invalidated), by level (strategic/tactical/testable), risk distribution assessment.

## 6. Output Specification

Primary output artifact: `decision_analysis` → maps to `core/schemas/artifacts/decision_analysis.schema.json`

## 7. Guardrails

- **Failure: Hypotheses are not falsifiable**: "AI will help PMs" cannot be proven wrong with specific evidence → response: reject. Demand falsifiable formulation. "PMs using AI-generated PRDs will report <30% rewrite rate" is falsifiable.
- **Failure: Untestable hypotheses**: Hypothesis requires data we cannot get or experiment we cannot run within budget/timeline → response: flag as "unvalidatable." Decompose into smaller testable hypotheses or mark as strategic assumption (PM judgment required).
- **Failure: No kill criteria**: Hypothesis has no defined conditions for invalidation → response: cannot proceed. Kill criteria prevent indefinite belief in invalidated hypotheses.
- **When to escalate**: Top risk hypothesis (score >=90) has transformative impact and high uncertainty — this is the single biggest bet the product is making. PM must decide: invest in validation OR accept this as a leap of faith. Multiple strategic hypotheses have been invalidated — core product thesis may be wrong.

## 8. Gold Standard Checklist

- [ ] Every hypothesis has a falsifiable statement and specific kill criteria
- [ ] Hypothesis tree has at least 2 levels (strategic + tactical) with clear parent-child links
- [ ] Interdependencies are mapped — if H1 fails, affected downstream hypotheses are identified
- [ ] Risk prioritization uses explicit scoring, not implicit ranking
- [ ] Highest-risk hypotheses are auto-routed to prototype generation with rationale
- [ ] Framework: Lean Startup (Eric Ries), discovery-driven planning (McGrath & MacMillan), hypothesis-driven development

- [ ] Framework alignment: validates against Lean Startup (Ries), discovery-driven planning (McGrath/MacMillan), hypothesis-driven development, scientific method in product
- [ ] Every recommendation includes explicit confidence level and assumptions
- [ ] Trade-offs are explicitly named — "what is lost" is as clear as "what is gained"
- [ ] PM has clear next action — not just "consider this" but "do X by Y date"

## 9. Examples

See `core/examples/artifacts/decision_analysis.example.json` for the canonical format.

## 10. Cross-References

- **Upstream skills**: pestle_synthesis, persona_evidence_synthesis, customer_journey_synthesis, weak_signal_detection
- **Downstream skills**: prototype_html_generation, experiment_design, sensitivity_analysis, roadmap_scenario_generation
- **Schemas**: hypothesis_portfolio.schema.json, hypothesis.schema.json (entity), prototype_record.schema.json
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
- **Test file**: `tests/test_v10_hypothesis_portfolio_management.py`
- **Example fixture**: `core/examples/artifacts/decision_analysis.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py`
