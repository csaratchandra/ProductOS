# Win/Loss Pattern Detection

## 1. Purpose

Analyze win/loss records to detect systematic patterns explaining why deals are won or lost — by segment, competitor, feature gap, and pricing — generating actionable product and sales improvements.

## 2. Trigger / When To Use

New win/loss records available (>=5). >=10 records accumulated since last analysis. Quarterly review cycle. Before competitive strategy refresh.

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

1. Aggregate records: Collect all win/loss records from analysis period. Categorize: won, lost, no-decision.
2. Segment patterns: Break down win/loss by segment, persona, deal size, evaluation stage. Where does win rate deviate significantly from average?
3. Identify win themes: What consistently appears in wins? Time-to-value? Integration depth? Peer recommendation? Categorize with frequency.
4. Identify loss themes: What consistently appears in losses? Missing features? Pricing? Procurement friction? Competitor advantage?
5. Competitive loss breakdown: Per competitor, decompose losses by reason. Which reasons are addressable (we can fix) vs structural (competitor advantage we accept)?
6. Quantify feature gaps: For addressable losses, what features would flip the outcome? Estimate revenue impact of addressing each gap.
7. Surface pricing gaps: Are losses clustered at specific price points? In specific segments?
8. Generate recommendations: Per finding, recommend action with impact/effort/owner.

## 6. Output Specification

Primary output artifact: specified in schema reference below.

## 7. Guardrails

- Sample size too small: <5 records in analysis period → flag as directional only. Confidence low.
- All losses attributed to pricing or "brand": Overly simple attribution → require multi-factor analysis. Most losses have 3+ contributing factors.
- When to escalate: Win rate declining 10%+ over 2 consecutive periods. Single competitor capturing >50% of losses.

## 8. Gold Standard Checklist

- [ ] Every pattern has frequency and win_rate statistics — not just anecdotes
- [ ] Competitive losses are attributed with contribution % per reason
- [ ] Feature gaps include revenue impact estimate
- [ ] Every recommendation has an explicit owner — not "someone should fix this"
- [ ] Addressable vs non-addressable losses are distinguished
- [ ] Framework alignment: validates against Win/loss analysis (Pragmatic Institute), competitive intelligence, sales enablement
- [ ] Every recommendation includes explicit evidence basis
- [ ] PM has clear next action with owner and timeline

## 9. Examples

See example artifacts in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: competitive_radar_scan, competitive_shift_analysis, customer_signal_clustering
- **Downstream skills**: battle_card_generation, pricing_analysis_synthesis, roadmap_scenario_generation
- **Schemas**: win_loss_analysis.schema.json, win_loss_record.schema.json

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
