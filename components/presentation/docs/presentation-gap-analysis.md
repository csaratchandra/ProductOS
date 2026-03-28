# ProductOS Presentation Gap Analysis And Remediation Plan

Purpose: Close the gap between the current presentation pipeline and the ProductOS promise of giving PMs a world-class presentation capability.

## 1. Executive Diagnosis

The current presentation capability is structurally incomplete.

ProductOS says presentation quality should be a competitive advantage and a PM leverage multiplier. The current implementation is a schema-valid rendering pipeline, not a presentation intelligence system.

Today the stack can:

- accept a `presentation_brief`
- derive a thin `evidence_pack`
- derive a thin `presentation_story`
- emit a normalized `render_spec`
- render responsive HTML
- emit a basic PPTX via a simple adapter

That is useful infrastructure, but it falls materially short of the intended system behavior.

The primary failure mode is not styling alone.

The system currently compresses the problem too early:

- the blueprint does not define a sufficiently concrete presentation grammar
- the schemas do not capture the information needed for high-quality deck generation
- the runtime does not perform real narrative planning
- the render layer collapses distinct slide types into near-identical outputs
- the quality gates verify artifact validity, not presentation excellence

## 2. Gap Summary

The gap can be described in one line:

ProductOS has a presentation transport layer, but not a presentation operating system.

### 2.1 What exists

- a clean artifact chain from brief to render payload
- a basic theme system
- basic source trace visibility
- minimal HTML output
- minimal native PPT export
- basic publish checks

### 2.2 What is missing

- explicit narrative planning logic
- typed evidence packaging
- audience-aware content transformation
- composition-specific rendering logic
- multi-format behavior that actually changes output shape
- native PPT fidelity as a first-class concern
- measurable visual and narrative quality gates
- exemplar-driven regression testing

## 3. Blueprint Gaps

The current blueprint expresses the right aspiration but under-specifies execution.

## 3.1 Missing presentation grammar

The blueprint says decks should be story-led, evidence-backed, and business-ready.
It does not define:

- narrative archetypes such as recommendation, status, strategy, roadmap, investment ask, incident, portfolio review
- slide sequencing rules by archetype
- how SCQ, answer-first, or recommendation-first patterns are selected
- when a point belongs in body slides versus appendix
- how a storyline should change for live versus async versus memo versus customer-safe contexts

Without this grammar, the implementation has no basis for making strong narrative decisions.

## 3.2 Missing evidence model

The blueprint requires supporting evidence, but it does not specify evidence as structured presentation material.

Missing evidence concepts:

- claims
- proof objects
- metric snapshots
- deltas and trends
- benchmark comparisons
- risks and mitigations
- dependencies and owners
- contradictions
- unknowns
- confidence rationale
- source provenance at claim level

Without this, the runtime can only pass through bullets.

## 3.3 Missing audience policy

The blueprint names several output forms, but it does not specify transformation rules for:

- leadership audiences
- PM and working-team audiences
- cross-functional operating reviews
- customer-safe narratives
- self-contained async decks
- presenter-led live decks

Missing policy dimensions:

- permissible detail density
- redaction rules
- terminology simplification
- recommendation directness
- evidence visibility threshold
- appendix depth
- call-to-action style

## 3.4 Missing visual operating grammar

The blueprint says visual quality should be consultant-grade and occasionally awe-inspiring.
It does not define the actual visual primitives and selection rules needed to achieve that bar consistently.

Missing:

- canonical composition library
- rules for choosing chart, table, matrix, timeline, comparison, narrative, or evidence forms
- layout density rules
- annotation rules
- hierarchy rules by slide type
- mobile and desktop adaptation rules
- how HTML and PPT should preserve the same composition semantics

## 3.5 Missing measurable quality bar

The blueprint includes qualitative guidance and a rubric, but there is no operational definition for automatic enforcement.

Missing measurable checks:

- does the first slide answer the audience question early
- does each slide have one primary message
- does each claim have sufficient proof
- does the deck show risk rather than hide it
- is the recommendation distinguishable from evidence
- is the deck audience-safe
- does the chosen visual form match the message
- does PPT preserve the intended reading path

## 4. Implementation Gaps

## 4.1 Brief schema is too thin

`presentation_brief` captures basic metadata, but not enough for high-quality deck generation.

Current missing fields:

- narrative archetype
- meeting type
- presenter presence
- audience sophistication
- decision stakes
- timebox
- appendix policy
- evidence threshold
- redaction policy
- tone profile
- desired outcome after presentation
- required objections to address
- optional alternative recommendations

Impact:

- the runtime cannot determine how to shape the deck beyond simple intent labels

## 4.2 Evidence pack is not real evidence packaging

The current runtime builds `evidence_pack` by copying outline bullets and assigning confidence from slide intent.

That means:

- confidence is not evidence-derived
- contradictions are never discovered
- source artifacts are not distilled into proof units
- no prioritization exists
- no evidence compression logic exists

Impact:

- presentations can look sourced without actually being evidence-driven

## 4.3 Story generation is mostly pass-through

The current `presentation_story` layer does not truly plan a story.

It currently lacks:

- audience-question mapping
- recommendation-versus-context distinction beyond labels
- narrative transitions
- explicit tension and resolution handling
- objection handling
- appendix extraction strategy
- proof allocation across slides

Impact:

- the deck is structurally flat and predictable

## 4.4 Render spec is not expressive enough

The current `render_spec` can name a composition type, but it does not carry the structured payload needed to render each composition well.

Missing typed render content:

- hero metrics
- comparison series
- timeline events with dependencies
- risk objects with likelihood, impact, owner, mitigation
- decision options with pros, cons, recommendation, consequences
- evidence blocks with proof type and annotation
- chart configuration
- appendix traces
- audience-specific visibility rules

Impact:

- every composition degrades into the same bullet-oriented shape

## 4.5 HTML renderer ignores composition semantics

The HTML runtime currently renders nearly every slide with the same structure:

- headline
- core message
- evidence cards
- footer blocks

Impact:

- composition names exist, but not composition behavior
- decks feel repetitive
- evidence-heavy and decision-heavy slides are visually indistinguishable
- the system cannot create true strategy, portfolio, or operating visuals

## 4.6 PPT export is below the required bar

The native PPT export is effectively a text layout fallback.

Missing:

- composition-specific placement
- grid system
- consistent typography mapping
- card and panel primitives
- table rendering
- matrix rendering
- timelines
- annotations
- appendix behavior
- speaker note integration
- fidelity scoring

Impact:

- PPT is not yet a publishable executive format

## 4.7 Publish check is too shallow

Current checks focus on source presence and a simple confidence rule.

Missing:

- unsupported claim detection
- density limit checks
- decision clarity checks
- audience-fit checks
- risk visibility coverage checks
- appendix sufficiency checks
- redaction checks
- HTML and PPT parity checks

## 4.8 Tests certify mechanics, not quality

Current tests prove:

- schema validity
- expected field presence
- file generation
- basic output writing

Current tests do not prove:

- story quality
- visual differentiation
- audience adaptation
- correctness of evidence packaging
- fidelity of PPT output
- regression against known-good exemplars

## 5. Required Blueprint Upgrades

The presentation blueprint should be upgraded from principles to an executable system contract.

## 5.1 Add presentation archetypes

Define at least these archetypes:

- decision recommendation deck
- executive status update
- roadmap and dependency review
- portfolio review
- launch readiness review
- incident or risk escalation deck
- customer narrative
- one-page operating summary

For each archetype define:

- opening pattern
- mandatory sections
- optional sections
- evidence standards
- appendix expectations
- prohibited shortcuts

## 5.2 Add narrative rules

Define:

- answer-first rule
- audience-question rule
- one-message-per-slide rule
- proof-before-assertion rule
- objection surfacing rule
- risk visibility rule
- appendix extraction rule

## 5.3 Add evidence contract

Define evidence objects with:

- `claim`
- `proof_type`
- `proof_payload`
- `source_ref`
- `confidence_state`
- `confidence_reason`
- `freshness`
- `counterevidence`
- `materiality`

## 5.4 Add audience policies

Define a transformation table for each audience and output mode.

Each policy should control:

- allowed detail
- tone
- jargon level
- risk exposure
- recommendation directness
- appendix depth
- customer-safe filtering

## 5.5 Add composition library

Define canonical slide compositions such as:

- hero statement
- decision frame
- metric strip
- proof panel
- evidence table
- comparison matrix
- risk heatmap
- roadmap timeline
- dependency chain
- tradeoff table
- recommendation with options
- appendix trace view

Each composition should specify:

- best use case
- required data shape
- reading path
- HTML rendering rules
- PPT rendering rules
- fallback rules

## 6. Required Schema Changes

## 6.1 `presentation_brief` changes

Add fields:

- `presentation_archetype`
- `meeting_type`
- `presenter_mode`
- `audience_type`
- `audience_familiarity`
- `decision_stakes`
- `time_limit_minutes`
- `deck_length_target`
- `appendix_mode`
- `redaction_policy`
- `tone_profile`
- `success_outcome`
- `required_objections`
- `non_negotiables`
- `comparison_baseline`
- `customer_safe`

Upgrade `slide_outlines` to carry:

- `audience_question`
- `claim`
- `proof_requirements`
- `must_show_risk`
- `must_show_owner`
- `cta`
- `appendix_link`

## 6.2 `evidence_pack` changes

Replace plain findings with structured evidence units:

- `evidence_units`
- `contradictions`
- `gaps`
- `priority_evidence`
- `deferred_evidence`
- `metrics`
- `risk_items`
- `timeline_events`
- `decision_options`

## 6.3 `presentation_story` changes

Add:

- `narrative_pattern`
- `audience_key_question`
- `opening_answer`
- `main_recommendation`
- `objections_addressed`
- `appendix_strategy`
- `story_transitions`

For each slide add:

- `audience_question_answered`
- `claim`
- `why_now`
- `proof_strategy`
- `transition_from_previous`
- `cta`
- `appendix_reference`

## 6.4 `render_spec` changes

Replace generic `supporting_evidence` arrays with typed composition payloads.

Each slide should include:

- `composition_type`
- `composition_payload`
- `layout_variant`
- `density_mode`
- `visual_tokens`
- `visibility_rules`
- `annotation_rules`
- `html_render_hints`
- `ppt_render_hints`

`composition_payload` should vary by composition type.

Examples:

- decision frame: recommendation, options, tradeoffs, ask
- risk matrix: risks with impact, likelihood, owner, mitigation
- timeline: milestones, dependencies, confidence, slippage
- comparison table: entities, dimensions, highlighted deltas
- proof panel: claim plus proof blocks

## 6.5 `publish_check` changes

Add:

- `narrative_quality_score`
- `evidence_quality_score`
- `audience_fit_score`
- `visual_clarity_score`
- `html_fidelity_status`
- `ppt_fidelity_status`
- `redaction_status`
- `claim_support_exceptions`
- `density_exceptions`
- `missing_objections`

## 7. Required Runtime Architecture

The implementation should be refactored into explicit planning and rendering stages.

## 7.1 Proposed runtime stages

1. Source normalization
2. Evidence extraction
3. Narrative planning
4. Slide planning
5. Composition planning
6. Format-specific rendering
7. Publish validation

## 7.2 Source normalization layer

Input:

- `portfolio_update`
- `leadership_review`
- `status_update`
- `portfolio_state`
- other source artifacts

Responsibilities:

- convert source artifacts into typed source facts
- identify freshness and provenance
- mark contradictions and unknowns
- classify proof types

## 7.3 Evidence extraction layer

Responsibilities:

- derive claims from normalized facts
- package proof objects
- rank evidence by materiality
- identify weak or unsupported claims
- prepare appendix-grade trace content

## 7.4 Narrative planner

Responsibilities:

- select archetype-specific storyline
- answer the primary audience question early
- choose opening move
- place recommendations, risks, and evidence deliberately
- decide what belongs in appendix
- tailor the arc to live, async, memo, one-page, and customer-safe forms

## 7.5 Slide planner

Responsibilities:

- map story beats to slides
- assign one claim per slide
- allocate proof to slide or appendix
- enforce slide-count and density targets
- add transitions and calls to action

## 7.6 Composition planner

Responsibilities:

- choose the right composition for each slide
- convert evidence objects into typed composition payloads
- choose layout variant and density mode
- emit both HTML and PPT render hints

## 7.7 Renderer layer

Implement composition-specific renderers for:

- HTML
- PPT
- memo and one-page variants

These renderers should share the same composition semantics and differ only in channel-specific layout behavior.

## 7.8 Publish validator

Responsibilities:

- check support for each claim
- check that recommendation and evidence remain distinguishable
- verify audience safety
- verify risk visibility
- verify density limits
- verify HTML and PPT fidelity expectations

## 8. Rendering System Requirements

## 8.1 HTML renderer

Needed upgrades:

- composition-specific templates
- a real grid and spacing system
- annotations and callouts
- evidence table rendering
- matrix and timeline rendering
- appendix rendering
- density-aware variants
- better presenter and async variants

## 8.2 PPT renderer

Needed upgrades:

- native slide masters and theme mapping
- composition-specific layouts
- consistent geometry system
- table and matrix primitives
- notes support
- appendix support
- fallback rules by composition
- fidelity status reporting

## 8.3 Cross-render consistency

The same `render_spec` should preserve:

- primary message
- reading order
- relative emphasis
- evidence visibility intent
- risk and confidence treatment

## 9. Test Plan

The test strategy must shift from payload validity to outcome quality.

## 9.1 Schema tests

Continue validating:

- schema compliance
- required field presence
- invalid payload rejection

Add:

- invalid archetype rejection
- invalid composition payload rejection
- audience-policy validation
- publish-check scoring validation

## 9.2 Unit tests for planners

Add tests for:

- evidence extraction from source artifacts
- contradiction detection
- claim support mapping
- narrative pattern selection
- appendix extraction
- audience-mode transformation
- composition selection

## 9.3 Golden artifact tests

Create curated presentation fixtures for:

- executive recommendation deck
- status update deck
- roadmap review
- customer-safe story
- one-page summary

For each fixture validate:

- selected story arc
- selected compositions
- claim support completeness
- appendix behavior
- publish-check output

## 9.4 HTML snapshot tests

Add snapshot or DOM-structure tests to verify:

- composition differentiation
- risk treatments
- annotations
- evidence trace visibility
- mode-specific rendering differences

## 9.5 PPT verification tests

Add tests for:

- slide count and layout selection
- expected text placement groups
- note insertion
- composition-specific native objects
- fallback behavior for unsupported layouts

## 9.6 Rubric-based quality tests

Operationalize the visual rubric into testable checks:

- first slide answers the central question
- each slide has one primary message
- low-confidence claims are visibly treated
- decision slides show options and recommendation
- timeline slides show dependency logic
- risk slides show owner and mitigation

## 9.7 Regression review process

Add a manual review lane for exemplar decks:

- leadership review
- PM operating review
- customer-safe update

These should be reviewed against the rubric whenever composition logic changes.

## 10. Recommended Implementation Sequence

The work should be phased to reduce churn.

## Phase 1. Blueprint And Schema Foundation

Deliver:

- upgraded presentation blueprint section
- richer schema set for brief, evidence pack, story, render spec, publish check
- updated examples for all schemas

Success criteria:

- schemas can express all required deck behaviors without overloading free-text fields

## Phase 2. Typed Evidence And Story Planning

Deliver:

- source normalization layer
- typed evidence extraction
- narrative planner
- richer story artifacts

Success criteria:

- the system can produce materially different stories from the same source set based on audience and mode

## Phase 3. Composition Planning And HTML Rendering

Deliver:

- composition payload builders
- composition-specific HTML renderer
- appendix support
- density-aware output variants

Success criteria:

- HTML output shows visibly distinct slide forms and better narrative flow

## Phase 4. Native PPT Upgrade

Deliver:

- composition-specific PPT renderer
- notes support
- fallback fidelity rules
- PPT publish checks

Success criteria:

- PPT output is presentation-ready for internal leadership use

## Phase 5. Quality Gates And Regression Harness

Deliver:

- scoring-based publish checks
- golden deck fixtures
- snapshot and PPT verification tests
- rubric-based review workflow

Success criteria:

- quality regressions are caught automatically before claiming capability completion

## 11. Definition Of Done For Presentation Superpower

The presentation capability should only be considered complete when all of the following are true:

- the same source material can be rendered credibly as live, async, memo, one-page, meeting brief, and customer-safe outputs
- the system chooses narrative structure intentionally rather than passing through author-provided bullets
- evidence is packaged as proof, not decorative sourcing
- HTML and PPT outputs preserve composition semantics
- publish checks can block weak or misleading decks
- regression tests protect deck quality, not just payload validity
- exemplar outputs feel materially closer to consultant-grade work than to templated slide automation

## 12. Immediate Next Actions

The next implementation session should do the following in order:

1. Upgrade schemas to support archetypes, audience policies, typed evidence, and typed composition payloads.
2. Refactor the runtime so `evidence_pack` is derived from normalized source facts rather than slide bullets.
3. Replace pass-through `presentation_story` generation with an archetype-aware narrative planner.
4. Replace the generic HTML renderer with composition-specific templates.
5. Rebuild PPT export around native compositions rather than stacked bullet text.
6. Expand tests so narrative quality and render fidelity become release criteria.

## 13. Bottom Line

The current presentation system is not failing because the visual theme is weak.

It is failing because the system does not yet know how to think like a world-class PM storyteller, package evidence like a strategy analyst, and render like a serious presentation engine.

That is the gap ProductOS must close to claim presentation creation as a real PM superpower.
