# V10.0.0 Release Note — ProductOS V10

Released: 2026-05-03

ProductOS V10 transforms PMs from manual compilers into strategic decision-makers. 37 new schemas, 36 skills at world-class depth, autonomous intelligence across the full PM lifecycle.

## What Ships

### Intelligence Layer

- **Autonomous PESTLE Analysis**: 6-factor environmental analysis with 3-horizon projections, factor interconnections, geographic variations, and scenario modeling. Validated against Aguilar's PESTLE framework and Shell scenario planning.
- **Competitive Intelligence Engine**: Continuous radar scanning 19+ surface types. Structured alerts with competitive impact scoring and recommended PM actions. Auto-updating competitive feature matrix with differentiation summary and gap analysis.
- **Weak Signal Detection**: Identifies emerging patterns from thin evidence before they become obvious trends. Ansoff methodology with noise suppression and escalation triggers.
- **Market Trend Extrapolation**: 3-scenario market projections with confidence bands, inflection point analysis, and product implications mapping.
- **Regulatory Change Tracker**: Multi-jurisdiction regulatory monitoring with compliance deadlines, product impact assessment, and action requirements.
- **Living System**: Freshness monitoring with per-artifact-type TTLs. Drift detection when source data changes. Auto-refresh triggers. Impact propagation mapping across downstream dependencies.

### Decision Layer

- **Decision Intelligence**: Trade-off analysis with weighted scoring matrix. Decision trees with probability-weighted expected values. Sensitivity analysis identifying critical assumptions. Premortems with failure scenarios, early warning indicators, and reversal triggers. Reversibility scoring.
- **Pricing Intelligence**: Competitor pricing matrix. Willingness-to-pay synthesis per segment. Price sensitivity analysis (Van Westendorp). Pricing model options (subscription, usage-based, hybrid) with pros/cons. Unit economics per segment (CAC, LTV, payback). ROI calculator specification.
- **Hypothesis Portfolio Management**: Tree decomposition (strategic → tactical → testable). Kill criteria per hypothesis. Risk prioritization (impact × uncertainty). Auto-routing to prototype generation for highest-risk hypotheses.

### Production Layer

- **Discovery Depth**: 37 schemas with exceptional detail — persona goes from 4 fields to 12+ dimensions with empathy maps, narrative cards, and voice samples. Customer journey maps all 11 stages from unaware through advocacy.
- **AI Prototype Generation**: 3 interactive HTML variants per concept, each differentiated on visual design, interaction model, and information architecture. Complete state coverage (loading, empty, normal, error, edge, onboarding). WCAG 2.1 AA accessibility. PM-editable overlays. Annotation layers. User test kits with task scenarios and moderator guides.
- **Developer Handoff Pack**: PRD + INVEST user stories + acceptance criteria + API contracts + non-functional requirements + story maps + dependency graphs. Handoff-ready gates with blockers surfaced.
- **Full Marketing Content**: Messaging house (April Dunford framework). Battle cards per competitor. SEO-researched blog post briefs. Email sequences for launch, nurture, and re-engagement. Investor pitch deck (12 slides) and memo.
- **Stakeholder Management**: Power/interest stakeholder maps. Objection handling playbooks. Structured feedback capture with downstream propagation tracing.

### System Capabilities

- **Product Health Dashboard**: Single-surface product universe with autonomous alerts and top-5 recommended actions.
- **Autonomous Review Gates**: Composite f(confidence, decision_impact, maturity_band). Auto-publish low-risk outputs. Flag high-risk for PM review. Block critical+low-confidence combos.
- **Vendor-Neutral Agent Support**: Codex, Claude, Windsurf, Antigravity, and OpenCode — all supported through thin adapter model.
- **12-Element Skill Standard**: Every V10 skill includes: purpose, trigger, prerequisites, input spec, execution steps, output spec, guardrails, gold standard checklist, excellent/poor examples, cross-references, maturity band variations, validation criteria.

## What Changed

- Baseline version promoted from 8.4.0 to 10.0.0
- Skill system upgraded from 7-element V9 format to 12-element V10 depth
- 37 new schemas added to core/schemas/artifacts/
- 36 skills at world-class 12-element depth
- CHANGELOG updated with full V10 entry
- Blueprint trace matrix extended with 13 new V10 claims

## Known Limitations

- 48 legacy V9 skills remain at 7-element format (upgrade deferred to V10.1)
- 16 deferred schemas (analytics, cohort analysis, funnel tracking — deferred to V10.1)
- Product Health Dashboard is schema-defined; full visual build deferred to Sprint 19
- Agent swarm hardening under real workload not yet complete
- Production hosting and customer-safe external publication not yet available

## Upgrade Actions

1. Run `./productos run discover` to generate V10-depth discovery artifacts
2. Configure competitive radar with competitor surfaces via `competitor_radar_state`
3. Use autonomous review gates: set maturity band profile for your product stage
4. Generate prototypes from concept briefs with `prototype_generation_plan`
5. Build developer handoff packs from PRD and stories
6. Review bounded claims in `core/docs/v10-bounded-claim.md` before external communication
