# Persona Evidence Synthesis

## 1. Purpose

Turn scattered persona observations into a canonical archetype packet that downstream artifacts can reuse without reinterpretation.

## 2. Trigger / When To Use

Use when persona notes, interviews, or source artifacts exist but the persona truth is too loose for problem, concept, PRD, or story work. Specific triggers:
- New customer interview transcripts are available in inbox
- Segment map has been created or updated, requiring persona alignment
- PM invokes discovery phase persona generation
- Existing persona_archetype_pack freshness score drops below threshold

## 3. Prerequisites

- `segment_map` artifact with defined segments and qualifying traits
- At least 3 source note cards from customer interviews, user observation, or domain expert input
- `research_brief` or `research_notebook` with target persona context
- (Optional) `customer_pulse` for sentiment context

## 4. Input Specification

| Field | Type | Source Artifact/Schema | Required | Example Value | Notes |
|---|---|---|---|---|---|
| `persona_notes` | `array[string]` | Source note cards from `inbox/` | Yes | `["PM spends 3hrs/day in meetings..."]` | Min 5 notes per persona |
| `source_evidence` | `array[object]` | `source_note_card.schema.json` | Yes | `[{entity_type: "interview", ...}]` | Must include entity_type, timestamp |
| `segment_map` | `object` | `segment_map.schema.json` | Yes | Full segment_map artifact | Must have qualifying_traits per segment |
| `target_segment_ids` | `array[string]` | `segment_map.segments[].segment_id` | Yes | `["seg_enterprise_pm"]` | Min 1 segment |
| `research_context` | `object` | `research_brief.schema.json` | No | Full research_brief | Provides framing context |

## 5. Execution Steps

1. **Group evidence by persona cluster**: Read all source note cards and interview transcripts. Cluster observations by common role, behavior pattern, and workflow context. Identify distinct persona candidates — minimum 3, maximum 7 per segment.
2. **Extract goals, pains, triggers, blockers**: Per cluster, identify explicit goals (what they're trying to achieve), pains (frustrations, inefficiencies), triggers (what starts their workflow), and blockers (what stops them from achieving goals). Only include items with direct evidence support.
3. **Classify archetype roles**: Assign each persona cluster one archetype type: buyer, user, champion, blocker, operator, executive, or influencer. Each persona can only have ONE archetype type — split into separate personas if needed.
4. **Synthesize workflow traits**: Describe how each persona operates day-to-day: tools they use, communication patterns, decision-making style, collaboration habits. Derive from observation data, not assumptions.
5. **Score buying influence**: Per persona, assign buying influence level (high/medium/low) based on evidence of their role in purchasing decisions. Do not invent — if no evidence, mark as unknown and flag for PM review.
6. **Generate evidence-backed archetype profiles**: Compose the full archetype object per persona with all required and optional fields. Link evidence_refs to specific source note cards.
7. **Prioritize archetypes**: Score each archetype (1-100) based on: segment strategic importance × archetype role leverage × evidence confidence. Rank. Assign priority lanes (must_now/next/later/park).
8. **Record handoff preferences**: Per persona, define downstream requirements: what format do they prefer for communication? What detail level do they need in PM artifacts? What are their deal-breaker concerns?
9. **Assemble persona_archetype_pack**: Combine all archetypes, prioritization_basis, and handoff_preferences into a single canonical artifact.
10. **Validate and emit**: Run against gold standard checklist. If any criterion fails, mark ralph_status as blocked. If all pass, emit with ralph_status=decision_ready.

## 6. Output Specification

| Field | Type | Schema Reference | Required | Description |
|---|---|---|---|---|
| `persona_archetype_pack_id` | `string` | schema required field | Yes | Unique identifier |
| `workspace_id` | `string` | schema required field | Yes | Owning workspace |
| `title` | `string` | schema required field | Yes | Human-readable pack title |
| `segment_refs` | `array[entityRef]` | `#/$defs/entityRef` | Yes | Linked segments (min 1) |
| `archetype_mode` | `enum` | schema required field | Yes | buyer/user/champion/blocker/operator/executive/influencer |
| `canonical_truth` | `boolean` (const: true) | schema required field | Yes | Always true |
| `prioritization_basis` | `object` | `#/$defs/prioritizationBasis` | Yes | Must_now/next/later/park with rationale |
| `archetypes` | `array[archetype]` | `#/$defs/archetype` | Yes | Min 1 archetype, each fully specified |
| `source_artifact_ids` | `array[string]` | schema optional field | No | Source artifacts that informed this pack |

Primary output artifact: `persona_archetype_pack` → maps to `core/schemas/artifacts/persona_archetype_pack.schema.json`

## 7. Guardrails

- **Failure condition: Insufficient evidence**: Less than 3 source note cards per persona cluster → detection criteria: source count check before synthesis → response: stop and flag for PM. Do not synthesize from thin evidence.
- **Failure condition: Contradictory evidence**: Two sources describe conflicting goals/pains for the same persona cluster → detection criteria: contradiction_detection skill flag → response: surface conflict in output with confidence marked low. Do not silently resolve.
- **Failure condition: Persona overlap**: Two persona clusters share >70% traits → detection criteria: similarity threshold check → response: merge clusters or differentiate with explicit rationale. Flag for PM if ambiguous.
- **When to stop and escalate to PM**: Evidence for a critical persona (must_now priority) is thin or contradictory. Archetype classification is ambiguous between buyer and user roles. Buying influence evidence is missing for a high-priority persona.
- **When output should be marked low-confidence**: Single source per persona. Contradictory evidence unresolved. Evidence older than fresh_ttl (90 days for persona evidence). Inferred traits without direct observation.
- **When skill should refuse to generate**: No source note cards available. No segment_map exists. PM has not approved the target segment scope. Governance review blocks persona data collection.

## 8. Gold Standard Checklist

- [ ] Every archetype has at least 3 evidence refs to specific source note cards or interview transcripts
- [ ] Goals and pains are specific and behavioral, not generic ("wants to save time" → "spends 2hrs/week manually compiling status reports from 5 tools")
- [ ] Buying influence classification is evidence-backed, not assumed
- [ ] Workflow traits describe actual observed behavior, not idealized workflow
- [ ] Prioritization differences between archetypes are explainable from evidence
- [ ] Handoff preferences are concrete enough for downstream artifacts to action
- [ ] External framework alignment: validates against Alan Cooper's persona framework (goal-directed design) and NN/g persona methodology
- [ ] No archetype has empty goals, pains, triggers, or blockers arrays
- [ ] Archetype types are mutually exclusive per persona (one persona = one archetype type)
- [ ] Segment refs are valid and map to existing segment_map entries

## 9. Examples

### Excellent Output (5/5)

```json
{
  "persona_archetype_pack_id": "pap_enterprise_pm_2026",
  "workspace_id": "ws_productos_v2",
  "title": "Enterprise PM Persona Pack",
  "segment_refs": [
    {"entity_type": "segment", "entity_id": "seg_enterprise_pm"}
  ],
  "archetype_mode": "user",
  "canonical_truth": true,
  "prioritization_basis": {
    "lane": "must_now",
    "selection_rationale": "Enterprise PMs represent our highest-value beachhead segment. They report the strongest pain signal across all interviews.",
    "decision_owner": "PM Lead"
  },
  "archetypes": [
    {
      "persona_ref": {"entity_type": "persona", "entity_id": "pers_sarah_enterprise_pm"},
      "archetype_type": "user",
      "role_summary": "Senior PM at 500+ person org. Manages 2-product portfolio with 3 direct reports. Primary tool: Jira + Confluence + Google Docs. Decision authority: recommends, does not approve budget.",
      "goals": [
        "Reduce time spent on manual discovery research from 15hrs/week to 5hrs/week",
        "Produce stakeholder-ready strategy decks without designer dependency",
        "Keep 3 engineering teams aligned on quarterly roadmap without daily status meetings"
      ],
      "pains": [
        "Spends 4hrs/week manually compiling competitive research from 6 different sources",
        "PRD takes 2 weeks to write because evidence is scattered across Slack, Notion, and interview notes",
        "Engineering team reports story ambiguity causes 30% sprint carry-over"
      ],
      "triggers": [
        "Quarterly planning cycle begins → needs discovery pack within 3 days",
        "Competitor launches feature → needs competitive analysis within 24hrs",
        "Leadership requests strategy review → needs deck within 48hrs"
      ],
      "blockers": [
        "Current tools don't integrate — switching between 5 apps breaks flow",
        "No budget for additional headcount — must do more with current team",
        "Security review adds 4-week delay to any new tool adoption"
      ],
      "buying_influence": "medium",
      "workflow_traits": [
        "Starts day checking dashboards at 8am",
        "Spends 60% of week in meetings — prefers async updates",
        "Uses keyboard shortcuts extensively — power user of existing tools",
        "Reviews artifacts on mobile during commute — needs responsive layouts"
      ],
      "priority_score": 92,
      "priority_rationale": "Highest pain signal across all segments. Most interview mentions. Strongest alignment with ProductOS value prop.",
      "handoff_preferences": [
        "Executive summary first — will read detail only if summary hooks",
        "Visual first — decision decks matter more than raw data",
        "Exportable to Google Slides — need to customize for internal presentations"
      ],
      "evidence_confidence": "high",
      "evidence_refs": [
        "source_note_card_sarah_interview_001",
        "source_note_card_sarah_interview_002",
        "source_note_card_sarah_observation_003",
        "source_note_card_enterprise_pm_survey_004"
      ]
    }
  ],
  "source_artifact_ids": [
    "research_brief_enterprise_pm_q2",
    "segment_map_productos_v2"
  ],
  "created_at": "2026-05-03T08:00:00Z"
}
```

### Poor Output (2/5) — What to Avoid

```json
{
  "archetypes": [
    {
      "persona_ref": {"entity_type": "persona", "entity_id": "pers_sarah_enterprise_pm"},
      "archetype_type": "user",
      "role_summary": "PM at a company",
      "goals": ["Save time", "Be more productive"],
      "pains": ["Too much work"],
      "triggers": ["Needs to do work"],
      "blockers": ["Not enough time"],
      "buying_influence": "high",
      "workflow_traits": ["Works hard"],
      "priority_score": 100,
      "priority_rationale": "Important",
      "handoff_preferences": ["Good output"],
      "evidence_refs": ["some_source"]
    }
  ]
}
```

**Why this fails:**
- Goals and pains are generic platitudes ("save time" → not actionable). Real goals must be measurable and behavior-specific.
- Buying influence marked "high" without evidence — appears invented.
- Workflow traits contain one vague entry — real traits must describe specific observed behavior.
- Priority score of 100 with "Important" rationale — needs quantified reasoning.
- Single evidence reference — minimum 3 required.
- Handoff preferences are meaningless ("Good output") — must specify format, channel, detail level.

## 10. Cross-References

- **Upstream skills**: `segment_enrichment`, `customer_signal_clustering`, `evidence_extraction`, `source_normalization`
- **Downstream skills**: `persona_priority_scoring`, `concept_risk_surfacing`, `story_decomposition_and_ambiguity_detection`, `prd_scope_boundary_check`
- **Related entity schemas**: `core/schemas/entities/persona.schema.json`, `core/schemas/entities/segment.schema.json`, `core/schemas/entities/customer.schema.json`
- **Related artifact schemas**: `core/schemas/artifacts/persona_archetype_pack.schema.json`, `core/schemas/artifacts/empathy_map.schema.json`, `core/schemas/artifacts/persona_narrative_card.schema.json`
- **Related workflows**: `core/workflows/discovery/idea-to-concept-workflow.md`, `core/workflows/discovery/persona-to-user-story-workflow.md`

## 11. Maturity Band Variations

| Band | Depth Adjustment | Evidence Requirements | Output Expectations |
|---|---|---|---|
| 0→1 | Exhaustive: synthesize all 7 archetype types. Include empathy maps and narrative personas for all must_now archetypes | Min 5 source note cards per archetype. Multi-source corroboration required. Max 30-day evidence freshness | All archetypes fully specified. Empathy maps required for top 3 archetypes. Persona narrative cards auto-generated. |
| 1→10 | Deep: synthesize 4-5 archetype types for priority segments | Min 3 source note cards per archetype. Single source allowed for later-priority personas | Priority archetypes fully specified. Empathy maps for must_now archetypes only. |
| 10→100 | Standard: synthesize 3-4 archetype types. Focus on user + buyer + champion | Min 2 source note cards per archetype. Quantitative data (analytics, surveys) preferred over interviews | Core fields required. Empathy maps optional. Prioritize data-backed over narrative depth. |
| 100→10K+ | Focused: synthesize 2-3 archetype types. User + buyer only. Heavy on quantitative behavioral data | Min 2 source note cards. Analytics data primary source — interview secondary. | Lean archetypes. Focus on behavioral data patterns. Narrative depth deprioritized for data precision. |

## 12. Validation Criteria

- **Schema conformance**: validates against `core/schemas/artifacts/persona_archetype_pack.schema.json`
- **Test file**: `tests/test_v10_persona_synthesis.py`
- **Example fixture**: `core/examples/artifacts/persona_archetype_pack.example.json`
- **Skill consistency test**: included in `tests/test_skill_consistency.py` — all 12 elements present and non-empty