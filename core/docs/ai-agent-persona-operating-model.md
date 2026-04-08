# AI Agent Persona Operating Model

Purpose: Define what ProductOS is still missing for the AI Agent persona and specify the loop structure required to make AI agents efficient at building ProductOS itself.

Date baseline: March 21, 2026

Dependencies:

- [runtime-state-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/runtime-state-model.md)
- [continuous-intake-and-memory-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/continuous-intake-and-memory-model.md)
- [internal-learning-loop-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/internal-learning-loop-model.md)
- [autonomous-pm-swarm-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/autonomous-pm-swarm-model.md)
- [v4-auto-improvement-loop.md](/Users/sarat/Documents/code/ProductOS/core/docs/archive/version-history/v4-auto-improvement-loop.md)
- [product-document-system.md](/Users/sarat/Documents/code/ProductOS/core/docs/product-document-system.md)
- [presentation-gap-analysis.md](/Users/sarat/Documents/code/ProductOS/components/presentation/docs/presentation-gap-analysis.md)

## Why This Document Exists

ProductOS currently has a stronger structure for the Product Manager persona than for the AI Agent persona.

That mismatch matters because ProductOS is currently being used to evolve ProductOS.

This creates a loop:

1. ProductOS is the workspace used to discover ProductOS gaps
2. AI agents help analyze those gaps and propose changes
3. ProductOS should make those AI agents more effective over time
4. improved ProductOS should then produce better future ProductOS changes

If the AI Agent persona is not explicitly designed, this loop becomes noisy, repetitive, and fragile.

The system then risks producing output without reliably improving leverage.

## Current Read

The repository already includes important runtime pieces:

- cockpit and orchestration state
- intake and memory state
- reviewer, critic, referee, and validation agent contracts
- internal learning-loop and improvement-loop state
- PM benchmark and superpower benchmark concepts
- a product-document direction
- a presentation remediation direction

These are strong foundations.

They are not yet a complete AI Agent operating model.

The newer [autonomous-pm-swarm-model.md](/Users/sarat/Documents/code/ProductOS/core/docs/autonomous-pm-swarm-model.md) turns that gap into an explicit internal-only hardening target instead of leaving broader swarm behavior as prompt lore.

## Core Gap

The missing layer is not "more agents."

The missing layer is a disciplined operating structure that answers:

- what superpowers the AI Agent should gain
- what loops the AI Agent is allowed to run
- what artifacts represent progress at each stage
- which reviewers and validators must approve each transition
- how ProductOS decides the loop is actually improving outcomes instead of just generating more work

## AI Agent Persona

### Primary job

The AI Agent persona exists to reduce the time and ambiguity required to move from raw signals to validated product change.

### Design note

`AI Agent` should be treated as a temporary umbrella label, not the final operating design.

The stable operating model should decompose this umbrella into specialist personas with explicit contracts such as:

- orchestrator
- discoverer
- researcher
- product shaper
- reviewer
- tester
- librarian
- presenter

Each specialist should have distinct authority, memory scope, handoff rules, and benchmark criteria.

### Primary superpowers

ProductOS should eventually give the AI Agent these superpowers:

- continuous collection of pain points, product signals, and evidence
- continuous clustering of repeated patterns instead of one-off issue logging
- fast retrieval of prior decisions, context, and similar past work
- structured conversion from signal to idea, concept, prototype, PRD, stories, release, and launch outputs
- explicit reviewer and validator routing at each gate
- bounded execution planning instead of open-ended autonomous wandering
- measurable outcome tracking after each change
- world-class presentation and communication packaging

### Success condition

The AI Agent persona is successful only if it helps ProductOS improve faster with less PM reconstruction work and better decision quality.

## What Is Missing Today

### 1. AI-agent-specific benchmark

The repository has PM benchmarks.

It does not yet have an explicit benchmark for whether ProductOS gives better leverage to AI agents building ProductOS.

Missing measures:

- time to convert raw signal into routed canonical artifact
- time to find relevant prior ProductOS context
- rate of duplicate idea or scope generation
- rate of reviewer rejection caused by weak evidence or weak framing
- loop completion rate from pain to accepted fix
- human intervention rate required to unblock agent work
- post-change outcome movement versus the targeted pain

### 2. AI-agent-specific persona definition

There is no explicit AI Agent persona definition alongside the PM persona.

Missing fields for this persona:

- authority boundaries
- allowed autonomous actions
- required approval points
- preferred evidence sources
- failure costs
- trust model
- expected collaboration pattern with PM and reviewers

### 3. Stage-gate model for the full loop

The repository has pieces of the loop, but not the full end-to-end gate model for the AI Agent persona.

Missing canonical gates:

- signal accepted for tracking
- pain pattern confirmed
- idea worth exploring
- concept worth prototyping
- prototype worth planning
- plan worth implementing
- implementation worth releasing
- release worth keeping after outcome review

### 4. Strong anti-loop controls

The current docs acknowledge bounded loops, but the AI Agent operating model still needs explicit anti-loop controls.

Missing controls:

- maximum retries per stage
- forced defer or reject after repeated failed review
- stale-loop detection
- duplicate-loop detection
- contradiction detection across active workstreams
- escalation rules when agents keep producing surface-level rewrites without improving the target metric

### 5. Memory hierarchy for agents

The repo has baseline retrieval state, but not a clear memory hierarchy optimized for AI-agent work.

Missing layers:

- raw signal memory
- normalized evidence memory
- decision memory
- failed-attempt memory
- benchmark memory
- reusable pattern memory
- presentation exemplar memory

Without failed-attempt and benchmark memory, agents will repeat already-rejected work.

### 6. Canonical reviewer stack by stage

Reviewer roles exist, but not yet as a stage-by-stage operating requirement.

The AI Agent persona needs a default review stack:

- critic for framing and assumptions
- validation for structure, traceability, and completeness
- referee for competing recommendations
- PM gate for scope, value, and final acceptance
- optional domain reviewers such as UX, compliance, trust, or delivery readiness

### 7. Outcome accounting after release

The current loop is stronger before release than after release.

Missing post-release discipline:

- did the change reduce the original pain
- did it create new friction elsewhere
- did the agent benchmark improve
- should the change be kept, iterated, rolled back, or re-scoped

### 8. Presentation intelligence with sample scouting

The repo already identifies a major presentation gap.

For the AI Agent persona, a missing capability is structured sample scouting and verification.

Missing workflow behavior:

- scout high-quality external exemplars for a requested presentation pattern
- record why each sample is relevant
- extract reusable structural patterns instead of copying surfaces
- flag provenance, copyright, and suitability constraints
- route shortlisted samples for human verification before adoption
- convert approved patterns into internal presentation grammar and regression fixtures

This should become a repeatable evidence loop, not an ad hoc design exercise.

### 9. Cross-loop coordination

The user journey described here is not one loop.

It is several linked loops:

- discovery loop
- prioritization loop
- prototyping loop
- delivery loop
- release loop
- post-release learning loop
- ProductOS self-improvement loop

What is missing is a canonical rule for how work moves between those loops without losing provenance or reopening already-closed questions.

### 10. Human-readable control surfaces for agents

ProductOS is moving toward readable PM documents.

The AI Agent persona also needs readable operating documents:

- active loop summary
- gate review summary
- benchmark movement summary
- rejected-path summary
- sample-scouting review summary
- next bounded slice recommendation

These should be first-class artifacts or generated docs, not buried in raw state.

## Proposed AI Agent Loop Model

### Loop 1: Continuous intake

Goal: convert raw signals into visible tracked inputs.

Sources:

- user feedback
- bug and issue logs
- turnaround-time failures
- internal agent friction
- competitor and market observations
- new technology shifts
- repeated user conversations
- presentation quality gaps

Required outputs:

- `intake_routing_state`
- normalized source notes
- provenance warnings

Exit gate:

- signal is accepted, deferred, or rejected for tracking

### Loop 2: Pain and opportunity clustering

Goal: identify repeated or high-impact patterns.

Required outputs:

- feedback clusters
- gap clusters
- confidence and frequency assessment
- affected persona and workflow mapping

Exit gate:

- cluster is strong enough to become a problem or opportunity candidate

### Loop 3: Problem framing

Goal: turn repeated pain into a precise problem worth solving.

Required outputs:

- `problem_brief`
- target workflow
- target metric
- why-now framing
- evidence and confidence summary

Reviewers:

- critic
- validation

Exit gate:

- PM agrees the problem is real and worth attention

### Loop 4: Idea and concept shaping

Goal: produce solution directions and select the strongest concept.

Required outputs:

- `idea_record`
- `concept_brief`
- alternatives considered
- expected leverage hypothesis
- risk and dependency view

Reviewers:

- critic
- optional referee if alternatives conflict

Exit gate:

- concept is strong enough to justify prototype or bounded implementation planning

### Loop 5: Prototype and proof

Goal: test whether the proposed direction improves the target workflow before broad commitment.

Required outputs:

- `prototype_record`
- scenario tests
- usability or workflow critique
- benchmark hypothesis

Reviewers:

- UX or workflow reviewer where relevant
- validation
- PM gate

Exit gate:

- prototype evidence supports planning, revision, or rejection

### Loop 6: Planning and implementation

Goal: turn the approved direction into a bounded slice that can be executed safely.

Required outputs:

- roadmap or increment impact
- PRD or execution package
- acceptance criteria
- execution session plan
- required validation path

Reviewers:

- delivery readiness
- validation
- PM gate for commitments

Exit gate:

- slice is approved for implementation

### Loop 7: Release and launch

Goal: verify that the slice is fit to release and explainable to humans.

Required outputs:

- release readiness
- release gate decision
- stakeholder-facing docs
- presentation or communication package when needed

Reviewers:

- validation
- readiness reviewer
- PM gate

Exit gate:

- release is accepted, deferred, or blocked

### Loop 8: Outcome review

Goal: determine whether the change actually delivered the intended superpower.

Required outputs:

- benchmark delta
- targeted pain movement
- unintended side effects
- keep / iterate / rollback / defer recommendation

Reviewers:

- critic
- validation
- PM gate

Exit gate:

- loop is explicitly closed with accept, iterate, defer, or reject

## Required New Capability Areas

### A. AI agent benchmark model

Add an AI-agent-specific benchmark artifact parallel to `pm_benchmark`.

Minimum sections:

- workflow scenario
- baseline time and quality
- current time and quality
- reviewer rejection rate
- duplicate-work rate
- context retrieval quality
- post-release outcome movement

### B. Agent authority and approval policy

ProductOS should define what an AI agent may do without PM approval versus what always requires a human gate.

Minimum policy dimensions:

- read
- route
- draft
- modify structured artifacts
- modify readable docs
- trigger implementation
- trigger publish or release
- adopt external exemplars

### C. Reviewer policy by artifact type

Each artifact type should name default required reviewers and optional reviewers.

This prevents shallow outputs from flowing downstream just because they are schema-valid.

### D. Failed-attempt memory

Rejected concepts, failed prototypes, weak presentation samples, and blocked implementation slices should remain retrievable.

Otherwise the AI Agent will keep rediscovering dead ends.

### E. Sample-scouting system for presentation excellence

ProductOS should support a presentation-sample loop:

1. scout strong exemplars
2. capture structured notes on why they work
3. classify the pattern by archetype, audience, and composition
4. verify with human review before adoption
5. convert approved patterns into internal templates, grammar rules, and regression tests

The acceptance rule should be:

- inspiration may be gathered broadly
- adoption into ProductOS requires human review and internal abstraction
- ProductOS should store extracted principles, not copied external decks

### F. Cross-loop traceability

Every accepted change should trace:

- source signal
- clustered pain
- problem
- idea
- concept
- prototype
- plan
- release
- measured outcome

If this chain is broken, the system will not know which loops are actually paying off.

## Superpower Evaluation For The AI Agent Persona

The question should not be "did the agent produce more artifacts?"

The question should be "did ProductOS give the agent better leverage?"

Core measures:

- less time spent reconstructing context
- less duplicate analysis
- faster routing from signal to decision-ready state
- fewer weak concepts reaching PM review
- stronger release and post-release learning discipline
- better explanation and presentation quality
- more visible reasons for why a change should or should not proceed

## Priority Recommendation

For the AI Agent persona, the next structural moves should be:

1. define the AI Agent persona explicitly
2. define an AI-agent benchmark artifact
3. define stage-gate reviewer policy across the full loop
4. add failed-attempt memory and duplicate-loop controls
5. add presentation sample-scouting and human verification as a formal capability
6. generate readable loop summaries so humans can supervise the swarm without reading raw state

## Decision Rule

ProductOS should treat the AI Agent persona as a first-class internal operating persona now.

Reason:

- ProductOS is already being built through an AI-assisted self-hosting loop
- the PM persona alone is not enough to structure that loop
- without an explicit AI Agent operating model, self-improvement will remain partially accidental

The AI Agent persona should remain internal-first until benchmark evidence shows the loop is genuinely improving ProductOS outcomes.
