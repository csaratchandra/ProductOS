# Empathy Map Generation

## 1. Purpose

Generate structured empathy map canvas for priority personas showing Think & Feel, See, Say & Do, Hear, Pains, and Gains — all evidence-backed from source note cards, not assumptions — with visual canvas rendering spec for workshop and presentation use.

## 2. Trigger / When To Use

- `persona_archetype_pack` created with priority personas
- PM requests empathy map for stakeholder workshop or alignment session
- Persona evidence refreshed with new interview data
- Before user journey mapping — empathy map informs emotional and cognitive context

## 3. Prerequisites

- `persona_archetype_pack` with archetype profiles
- Source note cards from interviews, observation, or surveys (minimum 3 per persona)
- (Optional) `persona_narrative_card` for enriched context

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `persona_archetype_pack` | `object` | `persona_archetype_pack.schema.json` | Yes | Goals, pains, triggers, workflow_traits |
| `source_evidence` | `array[object]` | `source_note_card.schema.json` | Yes | Interview transcripts, observation data |

## 5. Execution Steps

1. **Extract emotional and perceptual data**: From source note cards, isolate quotes and observations revealing how the persona thinks, feels, perceives, and hears.
2. **Build Think & Feel quadrant**: Major preoccupations, worries, aspirations, overall emotional state. Derive from internal monologue captured in interviews.
3. **Build See quadrant**: What they observe in their environment, market, colleagues, and competitors. Ground in specific observations they shared.
4. **Build Say & Do quadrant**: Public attitude vs private behavior. What they say in meetings. How they actually behave with team and tools.
5. **Build Hear quadrant**: What they hear from boss, peers, directs, and industry. Influences on their thinking.
6. **Build Pains**: Fears, frustrations, obstacles, failure risks. More emotionally deep than archetype_pack pains.
7. **Build Gains**: Wants, needs, success measures, dream state. What they aspire to, not just what they need today.
8. **Score evidence confidence**: Per quadrant: confidence level, source count, identified evidence gaps.
9. **Design visual canvas**: Layout spec for rendering: quadrants, center label, layout type.
10. **Assemble empathy_map artifact**: Link to persona_refs and evidence_refs. Validate completeness.

## 6. Output Specification

- `empathy_map` → `core/schemas/artifacts/empathy_map.schema.json`

## 7. Guardrails

- **Fabricated emotions**: Emotional content not traceable to interview or observation evidence → mark as low confidence. Strip unsupported emotional claims.
- **Empty quadrant**: A quadrant has no evidence-supported content → flag gap. Do not invent content to fill it. PM should decide: gather more data or accept gap.
- **When to escalate**: Empathy map reveals emotional state that contradicts archetype_pack goals (persona says one thing, feels another) — surface contradiction for PM.

## 8. Gold Standard Checklist

- [ ] Every quadrant entry has behavioral specificity ("worries about being blamed for product failures" not "worried")
- [ ] Gains and Pains are distinct — no item appears in both
- [ ] Say & Do distinguishes between public statements and actual behavior (Say/Do gap)
- [ ] Dream state is aspirational and specific — it's what the persona wishes for, not what they expect
- [ ] Framework: XPLANE empathy map methodology, Dave Gray Gamestorming

## 9. Examples

See `core/examples/artifacts/empathy_map.example.json`

## 10. Cross-References

- **Upstream**: `persona_evidence_synthesis`, `persona_narrative_generation`
- **Downstream**: `customer_journey_synthesis`, `user_journey_screen_flow`, `prototype_html_generation`
- **Schemas**: `empathy_map.schema.json`, `persona_archetype_pack.schema.json`, `persona_narrative_card.schema.json`

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full empathy map for all priority personas. Deep emotional exploration. |
| 1→10 | Deep: full empathy map for must_now personas only. |
| 10→100 | Standard: abbreviated empathy map. Pains + Gains depth prioritized over Think & Feel narrative. |
| 100→10K+ | Focused: Pains + Gains only. Quantitative satisfaction data replaces qualitative empathy depth. |

## 12. Validation Criteria

- **Schema**: `empathy_map.schema.json`
- **Test**: `tests/test_v10_empathy_map.py`
- **Example**: `core/examples/artifacts/empathy_map.example.json`