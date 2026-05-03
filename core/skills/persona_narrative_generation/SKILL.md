# Persona Narrative Generation

## 1. Purpose

Generate rich narrative persona profiles with AI-crafted day-in-the-life stories, authentic voice samples, behavioral profiles, decision journey mapping, relationship analysis, use case inventory, satisfaction driver identification, and one-page visual card rendering specs — transforming archetype packs into vivid, stakeholder-ready persona artifacts.

## 2. Trigger / When To Use

- `persona_archetype_pack` created or updated with priority personas
- PM requests deeper persona for stakeholder presentation or workshop
- Prototype generation plan needs persona context for realistic scenarios
- Marketing content generation requires buyer persona depth
- Persona evidence refreshed (new interview data, survey results)

## 3. Prerequisites

- `persona_archetype_pack` with archetypes fully specified (goals, pains, triggers, blockers, workflow_traits)
- Source note cards from customer interviews, user observation, or domain expert input (minimum 3 per persona)
- Segment context from `segment_map`
- (Optional) `empathy_map` for think/feel dimension enrichment

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `persona_archetype_pack` | `object` | `persona_archetype_pack.schema.json` | Yes | Full archetype pack | Contains archetypes to narrativize |
| `source_evidence` | `array[object]` | `source_note_card.schema.json` | Yes | Interview transcripts, observation notes | Min 3 sources per persona |
| `target_archetype_refs` | `array[string]` | `persona_archetype_pack.archetypes[].persona_ref` | Yes | `["pers_sarah_enterprise_pm"]` | Which personas to generate cards for |

## 5. Execution Steps

1. **Select priority archetypes**: From archetype_pack, identify must_now and next priority personas for narrative card generation.
2. **Build identity profile**: From evidence, construct demographic and professional identity: age range, location, role, experience, team context, career stage. Generate AI photo description for visual mockup.
3. **Craft day-in-the-life narrative**: Compose 5-part narrative (morning, core workday, afternoon, evening, weekly rhythm). Ground every detail in evidence — describe tools they actually use, frustrations they actually expressed, behaviors actually observed. Do not invent aspirational workflows.
4. **Extract voice samples**: From interview transcripts, identify authentic quotes that reveal persona's mindset. If exact quotes unavailable, generate voice samples in persona's language style based on observed communication patterns. Each sample: context, quote, tone. Minimum 3 samples.
5. **Profile behavior**: Classify technology comfort, learning style, communication preference. List actual daily tools from evidence. Assess switching cost with rationale.
6. **Map decision journey**: Build structured evaluation process: discovery channel, ranked evaluation criteria (with weights), decision authority level, budget signoff requirements, timeline, influencers, and deal-killers. All derived from buying behavior evidence.
7. **Analyze relationships**: Map who they influence, who influences them, reporting chain, primary collaborators, and potential conflicts with other personas.
8. **Catalog use cases**: Primary, secondary, edge, and anti-use cases. Per case: detailed scenario, frequency, criticality, and outcome if solved. Anti-use case is critical — defines what the persona will NOT use the product for.
9. **Identify satisfaction drivers**: Must-haves (table-stakes), delighters (differentiation), detractors (deal-breakers), indifference zone (don't invest here). Ground in evidence of what actually drives satisfaction for this persona.
10. **Define maturity band variation**: How does this persona's behavior evolve as the product matures? Same persona at 0→1 behaves differently than at 10→100.
11. **Design visual card**: Specify one-page visual layout: sections, layout type, color palette, key quote pullout. This feeds into automated visual rendering.
12. **Assemble and validate**: Build `persona_narrative_card` artifact. Link evidence refs. Validate against gold standard (Alan Cooper persona framework, NN/g methodology).

## 6. Output Specification

- `persona_narrative_card` → `core/schemas/artifacts/persona_narrative_card.schema.json`

## 7. Guardrails

- **Failure condition: Invention without evidence**: Narrative includes details not supported by source data → detection criteria: every claim must trace to a source_ref → response: strip unsupported details. Mark affected sections as low-confidence.
- **Failure condition: Stereotyping**: Persona attributes based on demographic assumptions, not observed behavior → response: force re-derivation from behavioral evidence only. Flag for review.
- **When to stop and escalate**: Conflicts between archetype_pack goals/pains and interview evidence. Decision journey evidence is thin but persona has high buying influence — PM should fill gaps before stakeholder presentation.

## 8. Gold Standard Checklist

- [ ] Day-in-the-life narrative is specific ("spends 2hrs compiling research from 6 tools") not generic ("is a busy person")
- [ ] Voice samples capture distinct personality — reading them, you can "hear" the persona
- [ ] Decision journey criteria are ranked and weighted from evidence, not assumed
- [ ] Anti-use case exists and is specific — defines persona boundaries clearly
- [ ] Satisfaction drivers distinguish must-haves from delighters — not everything is "critical"
- [ ] Photo description is detailed enough for AI image generation
- [ ] External framework: Alan Cooper goal-directed design, NN/g persona methodology, Jobs-to-be-Done interview analysis

## 9. Examples

### Excellent: See `core/examples/artifacts/persona_narrative_card.example.json` (Sarah Chen)

### Poor: Generic persona with "wants to be more productive" goals, no voice samples, no anti-use case, no decision journey.

## 10. Cross-References

- **Upstream**: `persona_evidence_synthesis`, `empathy_map_generation`, `customer_signal_clustering`
- **Downstream**: `prototype_html_generation`, `messaging_house_construction`, `battle_card_generation`, `story_decomposition_and_ambiguity_detection`
- **Schemas**: `persona_narrative_card.schema.json`, `persona_archetype_pack.schema.json`, `empathy_map.schema.json`

## 11. Maturity Band Variations

| Band | Depth |
|---|---|
| 0→1 | Exhaustive: full narrative for all priority personas. Deep day-in-the-life. Photo description for image generation. |
| 1→10 | Deep: full narrative for must_now personas. Voice samples for top 3 only. |
| 10→100 | Standard: abridged narrative. Behavioral + decision data focus. Day-in-the-life condensed. |
| 100→10K+ | Focused: decision journey + satisfaction drivers only. Narrative depth deprioritized for quantitative behavioral data. |

## 12. Validation Criteria

- **Schema**: `persona_narrative_card.schema.json`
- **Test**: `tests/test_v10_persona_narrative.py`
- **Example**: `core/examples/artifacts/persona_narrative_card.example.json`