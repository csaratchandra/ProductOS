# Customer Journey Synthesis

## 1. Purpose

Synthesize end-to-end customer journey across all 11 stages from unaware through advocacy — with per-stage emotion scores, touchpoints, channels, pain points, moments of truth, drop-off risk indicators, competitive journey comparison, gap analysis, and auto-generated opportunity briefs — producing a visual-ready journey map artifact.

## 2. Trigger / When To Use

- Discovery phase persona and segment work complete
- PM requests journey mapping for specific segment/persona
- Before prototype generation — journey identifies where prototypes are most needed
- Competitive shift detected that may change customer journey expectations
- New customer research reveals journey friction points

## 3. Prerequisites

- `segment_map` with target segment defined
- `persona_archetype_pack` with target personas
- Source note cards from customer research covering multiple journey stages
- (Recommended) `persona_narrative_card` and `empathy_map` for persona context
- (Recommended) `competitive_feature_matrix` for competitive journey comparison

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `target_segment` | `object` | `segment_map.schema.json` | Yes | Segment journey is for |
| `target_personas` | `array[object]` | `persona_archetype_pack.schema.json` | Yes | Personas experiencing the journey |
| `source_evidence` | `array[object]` | `source_note_card.schema.json` | Yes | Research across journey stages |

## 5. Execution Steps

1. **Define journey scope**: Confirm target segment and personas. Frame the journey from customer perspective — what end-to-end experience are we mapping?
2. **Map all 11 stages**: For each stage (unaware through renewal/churn), describe what the customer experiences, what they do, what they think. Ensure stage transitions are logical.
3. **Score emotions per stage**: Assign emotion_score (1-10) and emotion_label per stage. Base on evidence of customer sentiment at each stage. Do not assume — use interview and support data.
4. **List touchpoints and channels**: Per stage, what does the customer interact with? What channel do they use? Be exhaustive — surface touchpoints the team may not realize exist.
5. **Identify pain points**: Per stage, what causes friction, confusion, or frustration? Prioritize by impact on customer retention and satisfaction.
6. **Map moments of truth**: Identify 3-5 points in the journey where the customer's relationship with the product is decided — they either deepen commitment or begin disengaging. Score current performance and improvement need.
7. **Analyze drop-off risk**: Per stage, assess likelihood of customer abandoning the journey. High risk stages are priorities for improvement.
8. **Build emotion curve**: Overall trend shape (improving, stable, declining, u_shaped, rollercoaster). Peak and valley stages identified.
9. **Conduct gap analysis**: Compare current customer experience against ideal. Identify critical gaps. Define unmet expectations.
10. **Generate opportunities**: From gaps and pain points, auto-generate improvement opportunities. Each opportunity: title, description, potential impact, effort estimate, linked feature concept.
11. **Compare against competitors** (optional): How does our journey compare to a named competitor's? Which stages do we lead? Which do we lag?
12. **Design visual map spec**: Configure rendering: stages visible, emotion curve overlay, touchpoint overlay, rendering mode.
13. **Assemble customer_journey_map artifact**: Link all evidence refs. Validate completeness.

## 6. Output Specification

- `customer_journey_map` → `core/schemas/artifacts/customer_journey_map.schema.json`

## 7. Guardrails

- **Incomplete stage coverage**: Fewer than 8 stages mapped → flag. Missing stages create blind spots in the journey.
- **Assumed emotions without evidence**: Emotion scores based on team assumptions, not customer data → mark all emotion scores as low confidence. Flag for PM review.
- **When to escalate**: Moment of truth has current_performance=weak with high importance — critical risk. Multiple stages have high drop_off_risk. Competitive comparison shows disadvantage at multiple key stages.

## 8. Gold Standard Checklist

- [ ] All 11 stages are mapped with specific content — not "TBD" or empty
- [ ] Emotion scores are evidence-backed (cited to interview snippets, survey data, support sentiment)
- [ ] At least 3 moments of truth identified with performance assessment
- [ ] Gap analysis identifies specific customer experience gaps with impact description
- [ ] Generated opportunities have effort/impact assessment and are actionable
- [ ] Framework: Forrester CX Index, McKinsey customer decision journey, Service Design (service blueprint alignment)

## 9. Examples

See `core/examples/artifacts/customer_journey_map.example.json`

## 10. Cross-References

- **Upstream**: `persona_evidence_synthesis`, `persona_narrative_generation`, `empathy_map_generation`, `competitive_shift_analysis`
- **Downstream**: `user_journey_screen_flow`, `prototype_html_generation`, `roadmap_scenario_generation`, `marketing_content_generation`
- **Schemas**: `customer_journey_map.schema.json`, `persona_archetype_pack.schema.json`, `segment_map.schema.json`

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: all 11 stages fully mapped. Deep qualitative research. Emotions from interview data. |
| 1→10 | Deep: all 11 stages. Mix of research + analytics data. Focus on purchase-to-adoption stages. |
| 10→100 | Standard: 8 core stages (skip unaware/aware for established product). Analytics-heavy. |
| 100→10K+ | Focused: 6 stages (research through renewal). Quantitative data only. Portfolio-level journey view. |

## 12. Validation Criteria

- **Schema**: `customer_journey_map.schema.json`
- **Test**: `tests/test_v10_customer_journey.py`
- **Example**: `core/examples/artifacts/customer_journey_map.example.json`