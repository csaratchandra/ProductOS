# ProductOS V10 Superpower Plan

Purpose: Canonical source of truth for the V10 build — defining every schema, skill, visual type, and capability needed to transform ProductOS from a structured artifact engine into a world-class, living, decision-driving PM superpower platform.

Status: **Complete** — 84 skills at 12-element depth. 201 schemas. 199 examples. 14 feature scorecards. Blueprint trace matrix updated. Bounded claims, release note published. 7/7 validation tests passing.

---

## Architecture: Three Layers That Compound

```
LAYER 1: INTELLIGENCE (continuously runs)
  ↓
LAYER 2: DECISIONS (helps PM choose)
  ↓
LAYER 3: PRODUCTION (generates world-class outputs)
  ↓
PRODUCT HEALTH DASHBOARD
```

---

## Build Progress

### Completed (Sprints 1-10): 21 schemas, 23 skills at 12-element depth

| Sprint | Phase | Schemas | Skills |
|---|---|---|---|
| 1-2 | Foundation | `maturity_band_profile`, `artifact_freshness_state` | `persona_evidence_synthesis` (upgraded to 12-element) |
| 3-4 | Intelligence | `competitor_radar_state`, `competitive_intelligence_alert`, `competitive_feature_matrix`, `regulatory_change_tracker` | `competitive_radar_scan`, `competitive_shift_analysis`, `weak_signal_detection`, `market_trend_extrapolation` |
| 5-6 | Discovery | `pestle_analysis`, `gold_standard_checklist`, `persona_narrative_card`, `empathy_map`, `customer_journey_map`, `user_journey_map` | `pestle_synthesis`, `persona_narrative_generation`, `empathy_map_generation`, `customer_journey_synthesis`, `user_journey_screen_flow` |
| 7-8 | Decision | `decision_analysis`, `pricing_analysis`, `hypothesis_portfolio` | `trade_off_analysis`, `decision_tree_construction`, `sensitivity_analysis`, `premortem_analysis`, `pricing_analysis_synthesis`, `pricing_model_design`, `hypothesis_portfolio_management` |
| 9-10 | Roadmap + Tech Bridge | `roadmap_scenario`, `capacity_model`, `win_loss_analysis`, `experiment_design`, `api_contract`, `developer_handoff_pack` | `roadmap_scenario_generation`, `capacity_vs_scope_modeling`, `win_loss_pattern_detection`, `experiment_design`, `api_contract_generation`, `non_functional_requirement_extraction` |

### Remaining (Sprints 11-20): ~24 schemas, 22 skills

| Sprint | Phase | Schemas Needed | Skills Needed |
|---|---|---|---|
| 11-13 | Prototype Generation | `design_token_set`, `prototype_generation_plan`, `prototype_comparison_matrix`, `prototype_quality_report`, `prototype_user_test_kit`, `prototype_annotation` | `prototype_html_generation`, `prototype_quality_evaluation` + 2 more |
| 14-15 | Developer + Support | `story_map`, `data_model_impact`, `rollout_strategy`, `help_manual_pack` | `story_map_generation`, `help_manual_generation` + 2 more |
| 16-17 | Marketing + Investor | `messaging_house`, `battle_card`, `blog_post_brief`, `email_sequence`, `social_media_pack`, `investor_pitch_deck`, `investor_memo`, `demo_video_script`, `one_pager` | `messaging_house_construction`, `battle_card_generation`, `investor_content_generation` + 3 more |
| 18 | Stakeholder + Living System | `stakeholder_map`, `meeting_brief`, `objection_playbook`, `alignment_dashboard_state`, `feedback_capture`, `drift_detection_alert`, `impact_propagation_map` | `stakeholder_management`, `freshness_and_staleness_scan`, `drift_and_impact_propagation` |
| 19 | Dashboard + Analytics | `cohort_analysis`, `funnel_analysis`, `feature_adoption_report`, `churn_prediction`, health dashboard panels | `health_dashboard_build` + analytics skills |
| 20 | Validation + Release | Blueprint trace matrix, feature scorecards, dogfood in an explicit workspace, release note | Feature scorecards for all capabilities |

---

## Skill Contract Standard (12 Elements)

Every V10 skill must include:
1. Purpose — one sentence of what this skill accomplishes
2. Trigger — specific conditions for invocation
3. Prerequisites — what must exist before execution
4. Input Specification — table with field/type/source/required/example
5. Execution Steps — numbered, actionable steps (5-13 per skill)
6. Output Specification — exact schema references
7. Guardrails — failure conditions with detection criteria and responses
8. Gold Standard Checklist — verifiable quality criteria + external framework alignment
9. Examples — excellent (5/5) and poor (2/5) with explanation
10. Cross-References — upstream/downstream skills + schemas
11. Maturity Band Variations — how behavior changes across 0→1, 1→10, 10→100, 100→10K+
12. Validation Criteria — schema conformance, test file, example fixture

---

## Guardrails

- Every schema requires a valid example in `core/examples/artifacts/`
- Every schema + example must pass schema validation tests
- Every skill must pass 12-element contract consistency test
- No stable release promotion without Ralph loop (inspect, implement, refine, validate, fix, revalidate)
- OpenCode adapter parity maintained throughout (added Sprint 1)
- Marketing claims must not exceed bounded claim rules

---

## Success Metrics

| Dimension | V9 Baseline | V10 Target |
|---|---|---|
| Artifact schemas | 148 | 172+ |
| Skills at world-class depth | 49 (V9 format) | 77 (V10 12-element format) |
| Visual types | 10 | 24 |
| Intelligence subsystems | 0 | 4 |
| Decision subsystems | 0 | 5 |
| Feature score average | ~3 | 4.5+ |
| PM rewrite rate | ~40% | <10% |
