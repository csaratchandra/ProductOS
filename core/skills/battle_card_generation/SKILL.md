# Battle Card Generation

## 1. Purpose

Generate per-competitor battle cards with feature comparison, pricing comparison, win/loss themes, objection handling scripts, ideal customer profile comparison, recent competitive moves, and sales conversation guide.

## 2. Trigger / When To Use

Competitor dossier updated. New competitive intelligence alert. Sales team requests competitive enablement. Before launch.

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

1. Load competitor data: From competitor_dossier, competitive_feature_matrix, competitive_intelligence_alerts, win_loss_analysis.
2. Write overview: One-liner describing competitor. Our positioning vs theirs. Primary advantage and disadvantage.
3. Build feature comparison: 5-8 key features covering all differentiation categories. Per feature: our capability, their capability, advantage (us/them/tie), detail explaining difference.
4. Summarize pricing: Comparison matrix with tier mapping. Identify where we are cheaper/better value and where competitor undercuts us.
5. Define ideal customer profiles: When does competitor win? When do we win? Help sales qualify out early.
6. Surface win themes: 2-3 systematic reasons we beat this competitor. Each with description.
7. Surface loss themes: 1-3 reasons we lose to this competitor. Which are addressable?
8. Build objection handling: 2-4 common objections with scripted responses and supporting evidence. Train sales to handle competitive conversations.
9. Write sales conversation guide: A paragraph the sales rep can use verbatim when a prospect mentions this competitor. 'If prospect says [competitor name], say: ...'
10. Note recent moves: What has this competitor done in the last 90 days that the sales team should know about?

## 6. Output Specification

Primary output: `battle_card, competitive_feature_matrix` artifact

## 7. Guardrails

- Battle card too negative: Dismisses competitor without acknowledging their strengths → fix. Sales hears this from prospects. Honest assessment builds credibility.
- Objection responses are defensive: "No, we're actually better because..." → fix. Acknowledge the concern, then pivot to evidence.
- When to escalate: Competitor has launched a capability that nullifies our primary differentiator. Battle card may be temporarily inaccurate — flag urgency.

## 8. Gold Standard Checklist

- [ ] Overview acknowledges competitor strengths (not just weaknesses)
- [ ] Feature comparison covers the capabilities PROSPECTS most frequently ask about
- [ ] Objection handling includes scripted responses for sales reps
- [ ] Sales conversation guide is ready-to-use (verbatim)
- [ ] Framework: Pragmatic Institute competitive enablement, Crayon competitive intelligence methodology
- [ ] Framework alignment: Pragmatic Institute, Crayon competitive intelligence, MEDDIC sales qualification
- [ ] All outputs have explicit evidence traceability

## 9. Examples

See `core/examples/artifacts/` for canonical example artifacts.

## 10. Cross-References

- **Upstream skills**: competitive_feature_matrix, win_loss_analysis, competitive_shift_analysis, pricing_analysis
- **Downstream skills**: sales enablement, one_pager, launch communication
- **Schemas**: battle_card.schema.json, competitive_feature_matrix.schema.json

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
