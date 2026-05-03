# Experiment Design

## 1. Purpose

Design rigorous experiments with hypothesis, control + treatment variants, primary/secondary metrics, sample size requirements, guardrail metrics, and statistical decision criteria — with auto-trigger to decision upon conclusion.

## 2. Trigger / When To Use

High-uncertainty hypothesis needs validation (risk priority >=60). PM requests experiment to resolve a decision. A/B test needed for feature launch.

## 3. Prerequisites

- Current feature prioritization data (feature_prioritization_brief, prioritization_decision_record)
- Engineering team structure and velocity data (from capacity_model or PM input)
- OKR or strategic objectives defined for the planning period
- (Recommended) PESTLE analysis and market context
- (Recommended) Previous roadmap scenario for comparison

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `feature_backlog` | `array[object]` | feature_prioritization_brief, prioritization_decision_record | Yes | Prioritized features with story points |
| `team_data` | `array[object]` | PM input or capacity_model | Yes | Team velocity, headcount, allocation |
| `time_horizon_months` | `integer` | PM input | Yes | Planning horizon (3-24 months) |

## 5. Execution Steps

1. Frame from hypothesis: Convert hypothesis from portfolio into testable experiment. "We believe [change] will improve [metric] by [MDE] for [population]."
2. Design variants: Control (current state, no change). Treatment(s): the change being tested. Assign allocation % (equal split preferred unless ethical constraints).
3. Select metrics: Primary (what decides success), secondary (contextual understanding), guardrails (must not degrade — if violated, pause experiment).
4. Calculate sample size: Using baseline metric rate, MDE, significance level (default 0.05), power (default 0.80). Output: sample size required per variant.
5. Estimate duration: Sample size / daily eligible users. Add ramp-up period (data quality check).
6. Define decision criteria: Ship if: primary metric shows >=MDE with p<significance AND no guardrails violated. Hold if: directionally positive but not significant — gather more data. Abandon if: flat or negative.
7. Specify implementation: How are variants served? How is data collected? What instrumentation is needed?
8. Schedule review: Set interim check (50% sample) and final review date.

## 6. Output Specification

Primary output artifact: specified in schema reference below.

## 7. Guardrails

- Insufficient sample size: Daily eligible users × duration < required sample → cannot run. Propose: broaden eligibility OR extend duration OR accept lower power.
- Unethical variant: Treatment degrades user experience below acceptable threshold → reject. Experiment must not harm users.
- When to escalate: Primary metric is a business-critical KPI and experiment could materially affect quarterly numbers. Requires leadership approval.

## 8. Gold Standard Checklist

- [ ] Hypothesis is specific and falsifiable — not "we think this might help"
- [ ] Sample size calculation is shown with explicit inputs
- [ ] Guardrail metrics prevent quality degradation during experiment
- [ ] Decision criteria are defined BEFORE experiment starts
- [ ] Conclusion auto-routes to decision analysis artifact
- [ ] Framework alignment: validates against A/B testing (Kohavi, Trustworthy Online Controlled Experiments), statistical hypothesis testing, experimentation culture (Booking.com model)
- [ ] Every recommendation includes explicit evidence basis
- [ ] PM has clear next action with owner and timeline

## 9. Examples

See example artifacts in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: hypothesis_portfolio_management, prototype_html_generation
- **Downstream skills**: decision_analysis (auto-trigger on conclusion), feature_scorecard, improvement_loop
- **Schemas**: experiment_design.schema.json, hypothesis_portfolio.schema.json

## 11. Maturity Band Variations

| Band | Depth Adjustment |
|---|---|
| 0→1 | Exhaustive: multiple scenario modeling with qualitative depth. Capacity model lean — early team is small. |
| 1→10 | Deep: 3-scenario model. Capacity modeling important — team scaling. |
| 10→100 | Standard: 2-scenario model. Capacity modeling data-driven. Resource allocation focus. |
| 100→10K+ | Focused: portfolio-level scenarios. Capacity modeling across multiple teams. |

## 12. Validation Criteria

- **Schema conformance**: validates against associated schemas
- **Test file**: TBD in target sprint
- **Example fixture**: see associated `.example.json` files
