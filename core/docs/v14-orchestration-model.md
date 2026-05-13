# ProductOS V14 Orchestration Model

**Purpose:** Define the operating model for building and managing complex multi-persona products with ProductOS V14, including the 100x intent-driven architecture pipeline.  
**Audience:** PMs using ProductOS for products with 3+ personas, cross-persona handoffs, or regulated workflows.  
**Last Updated:** 2026-05-13

---

## The Core Insight

Most PM tools optimize for single-user journeys: one persona, one path, one set of screens. Real products — especially in regulated industries, enterprise software, and healthcare — have **multiple personas who must collaborate through handoffs**. The PM's job is not to optimize each persona's journey in isolation. It is to optimize the **orchestrated workflow** across all personas.

ProductOS V14 makes orchestration a first-class artifact.

---

## The Orchestration Stack

V14 organizes multi-persona product work into five interconnected layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: ZOOM NAVIGATION                                   │
│  Portfolio → Product → Feature → Component → Story           │
│  One surface. Infinite drill-down. Context preserved.        │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: HANDOFF SIMULATION                                │
│  Model → Predict → Optimize → Validate                       │
│  See bottlenecks before code exists.                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: PER-PERSONA PROTOTYPES                            │
│  Adaptive source + standalone exports                        │
│  Each persona sees their world. The PM sees all worlds.     │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: LAYERED PRD ARCHITECTURE                            │
│  Master PRD → Component PRDs                                 │
│  One initiative. Multiple sub-systems. Traceable.            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: WORKFLOW ORCHESTRATION                              │
│  Personas → Handoffs → Shared Artifacts → SLAs → Gates      │
│  The foundation. Everything else builds on this.             │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Workflow Orchestration

### When to Use
- Product has 3+ personas who must interact to complete a workflow
- Handoffs between personas have SLA requirements
- Compliance or regulatory gates exist at handoff points
- Workflow objects (cases, requests, submissions) mutate as they cross personas

### Key Artifact: `workflow_orchestration_map`

The orchestration map is not a journey map. A journey map shows what one persona experiences over time. An orchestration map shows **what happens to a workflow object as it moves between personas**, including:
- **Handoffs:** Who gives what to whom, triggered by what event
- **Wait states:** Where the workflow pauses, timeout rules, fallback actions
- **Shared artifacts:** Objects that cross personas with mutation tracking
- **SLA gates:** Time limits for each handoff
- **Compliance gates:** Audit, approval, or documentation requirements

### Operating Pattern

1. **Start with personas.** Ensure `persona_archetype_pack` identifies all personas involved in the workflow.
2. **Define the workflow object.** What object moves through the system? A case? A request? A submission? A claim?
3. **Map handoffs.** For each persona, define: what triggers them to hand off, what they hand off, who receives it, and what happens if the handoff fails.
4. **Add SLAs and gates.** Time limits, compliance requirements, escalation paths.
5. **Detect gaps.** Run `productos workflow orchestrate --detect-gaps` to find missing handoffs and orphan stages.
6. **Validate consistency.** Run `productos workflow orchestrate --validate-slas` to ensure SLAs are achievable given journey time estimates.

### Anti-Patterns
- **Journey map masquerading as orchestration map.** If your orchestration map only shows what each persona does in isolation, it's not an orchestration map.
- **Missing wait states.** Every handoff has a wait state on the receiving side. If you don't model it, you can't optimize it.
- **Ignoring mutation.** If a workflow object changes when Persona A hands it to Persona B, that mutation must be tracked.

---

## Layer 2: Layered PRD Architecture

### When to Use
- Initiative spans multiple sub-systems or components
- Different teams own different components
- Components have different release cadences
- Some components serve different persona subsets

### Key Artifacts: `master_prd`, `component_prd`, `prd_cascade_map`

**Master PRD** = The initiative-level specification. Problem, outcomes, strategic context, integration requirements, and which components are involved.

**Component PRD** = The sub-system specification. Detailed scope, user stories, acceptance criteria, API contracts, and which personas this component primarily serves.

**PRD Cascade Map** = The traceability and propagation rules. What happens when the master PRD changes? What happens when a component PRD changes?

### Operating Pattern

1. **Create master PRD.** Define the initiative problem, outcomes, and target personas.
2. **Decompose into components.** Use the orchestration map to identify natural component boundaries (often at handoff points).
3. **Create component PRDs.** Each component PRD links to the master. Define scope, personas, and integration points.
4. **Validate cascade.** Run `productos prd cascade --validate` to check for orphans, uncovered personas, and circular dependencies.
5. **Propagate changes.** When the master PRD scope changes, ProductOS queues component PRD regenerations. Review and approve in the living system.
6. **Notify upstream.** When a component PRD changes, ProductOS notifies the master PRD. The PM reviews before updating the master.

### Anti-Patterns
- **Flat PRD for multi-component initiatives.** A single PRD for a 6-component product becomes unreadable and unmanageable.
- **Components without persona assignments.** Every component must serve at least one persona. If it doesn't, it's either dead code or a missing persona.
- **Circular component dependencies.** Component A depends on Component B which depends on Component A. The cascade map detects and blocks this.

---

## Layer 3: Per-Persona Prototypes

### When to Use
- Different personas need different screens, navigation, and permissions
- Stakeholders need persona-specific demos for user testing or approval
- The PM needs to validate handoff continuity between persona views

### Key Artifacts: `persona_prototype_variant`, `prototype_handoff_config`

**Adaptive Prototype** = One HTML file with a persona role switcher. The PM uses this to validate continuity: "Watch what happens when Persona A submits, then switch to Persona B's view to see what they receive."

**Standalone Exports** = One HTML file per persona, generated from the same source. Used for stakeholder sharing and user testing with specific roles.

### Operating Pattern

1. **Generate variants.** `productos prototype persona-variants --prototype <id> --personas p1,p2,p3,p4`
2. **Validate adaptive prototype.** Switch between personas. Verify that handoff triggers are visible and actionable.
3. **Export per persona.** Generate standalone HTML for user testing with each persona group.
4. **Never edit exports directly.** If a change is needed, update the source artifacts and regenerate. Exports are outputs, not sources.

### Anti-Patterns
- **One prototype for all personas.** Every persona sees the same screens, but with different permissions. This obscures the true workflow and creates false assumptions.
- **Divergent exports.** Edits made to standalone exports that aren't reflected in the source. Always regenerate from source.
- **Missing handoff triggers.** A persona can take an action that hands off to another persona, but the trigger isn't visible in their prototype view.

---

## Layer 4: Handoff Simulation

### When to Use
- Workflow has SLA requirements that must be validated before implementation
- Resource constraints (reviewer capacity, system throughput) create bottlenecks
- "What-if" analysis is needed: "What if we add a parallel reviewer?" "What if we automate step 3?"
- Stakeholders need quantitative proof that the workflow will meet targets

### Key Artifact: `handoff_simulation_state`

The simulation engine models workflow execution as a probabilistic process:
- **Paths:** The workflow object can take multiple paths through the orchestration map
- **Bottlenecks:** Wait states where the object spends more time than the SLA allows
- **Optimization:** Suggested changes to reduce bottlenecks (parallelization, automation, SLA adjustment)

### Operating Pattern

1. **Build orchestration map first.** Simulation requires a valid orchestration map with SLAs and wait states.
2. **Configure simulation.** Define path probabilities, iteration count, and duration.
3. **Run baseline simulation.** `productos simulate handoffs --workflow-id <id> --duration 30d`
4. **Identify bottlenecks.** Review the bottleneck report for SLA violations and queue depth issues.
5. **Run "what-if" scenarios.** Adjust parameters: "Add parallel reviewer," "Reduce SLA by 50%," "Automate handoff 3."
6. **Compare scenarios.** Generate comparison tables showing time saved, cost impact, and risk change.
7. **Present animated output.** Use the interactive HTML simulation to show stakeholders how the workflow will behave.

### Anti-Patterns
- **Simulating without SLAs.** If your orchestration map has no SLA targets, the simulation has nothing to evaluate.
- **Ignoring confidence intervals.** Bottleneck predictions include confidence intervals. A 95% CI that includes zero means the bottleneck might not be real.
- **Optimizing without constraints.** "Automate everything" is not an optimization. The simulation engine suggests specific, constrained improvements.

---

## Layer 5: Zoom Navigation

### When to Use
- Product has grown beyond a single overview
- Stakeholders need different levels of detail (executives need portfolio, engineers need stories)
- The PM needs to trace a business outcome down to a specific acceptance criterion
- Context (filters, persona selection, time range) must persist across views

### Key Artifact: `zoom_navigation_map`

The atlas provides 4 levels of drill-down:
- **Product:** Summary cards, health indicators, linked PRDs
- **Feature:** Component breakdown, status, dependencies
- **Component:** Story map, acceptance criteria, API contracts
- **Story:** Full user story narrative, AC detail, test methods

### Operating Pattern

1. **Start at Product level.** See the full initiative overview.
2. **Drill to Feature level.** Click a feature to see its components and PRD links.
3. **Drill to Component level.** Click a component to see its story map and acceptance criteria.
4. **Drill to Story level.** Click a story to see its full narrative, acceptance criteria, and test methods.
5. **Preserve context.** Filters, selected persona, and time range persist across all levels.
6. **Use breadcrumbs.** The breadcrumb trail shows your full path: ProductOS V14 > Workflow Orchestration > Handoff Simulation > Story: "As a reviewer, I want to receive handoff notifications..."

### Anti-Patterns
- **Missing levels.** If the atlas jumps from Product to Story without Component, engineers lose the context they need.
- **Broken traceability.** Clicking a component should show its linked stories. If the link is broken, the zoom navigation is misleading.
- **Lost context.** If filters reset when zooming, the PM must reconfigure the view at every level.

---

## Cross-Layer Integration

The five layers are not independent. They are connected by traceability:

```
Master PRD scope change
    → triggers orchestration map regeneration (Layer 1)
    → triggers persona prototype variant updates (Layer 3)
    → queues zoom navigation re-render (Layer 5)

Orchestration map SLA change
    → triggers handoff simulation re-run (Layer 4)
    → suggests prototype handoff config updates (Layer 3)

Persona prototype user test feedback
    → feeds back into component PRD (Layer 2)
    → may trigger orchestration map gap detection (Layer 1)

Handoff simulation bottleneck
    → suggests orchestration map optimization (Layer 1)
    → may trigger master PRD scope discussion (Layer 2)
```

All changes flow through the **living system**: `impact_propagation_map` registers artifacts, `regeneration_queue` processes changes, and `queue review` requires PM approval for content-deep updates.

---

## Domain Extension Pack Integration

When domain extension packs are activated (V14.1+), the orchestration model gains domain-specific depth:

- **Compliance gates** in the orchestration map are populated from the regional overlay (e.g., HIPAA checkpoints for US healthcare)
- **Shared artifacts** reference domain data models (e.g., FHIR Patient, Coverage, Claim resources)
- **SLA targets** may be constrained by regulatory requirements (e.g., CMS turnaround time requirements)
- **Handoff simulation** includes domain-specific path probabilities and bottleneck thresholds

The core orchestration model remains domain-agnostic. Domain packs are overlays that add specificity without changing the core model.

---

## Success Metrics for PMs Using V14

A PM using ProductOS V14 should be able to:

1. Map a 6-persona workflow with handoffs, wait states, and SLAs in <30 minutes
2. Generate per-persona prototypes for all 6 personas in <5 minutes
3. Identify ≥2 missing handoffs or SLA inconsistencies before the first engineering discussion
4. Simulate the workflow and predict ≥1 bottleneck before implementation
5. Present an animated workflow simulation to stakeholders that demonstrates handoff continuity
6. Drill from portfolio summary to individual acceptance criterion in <10 seconds
7. Maintain a master PRD + 3 component PRDs with auto-propagation and no circular dependencies

If these metrics are not achievable, the orchestration model is not yet operational.

---

## Failure Modes

| Failure | Detection | Response |
|---|---|---|
| Orchestration map has <3 handoffs for a 4-persona workflow | `detect_handoff_gaps()` flags | Add explicit handoff for every persona transition |
| Master PRD scope change queued 0 component regenerations | `prd_cascade_map` validation | Check component coverage map — personas may be uncovered |
| Prototype variant has 0 handoff triggers | Variant schema validation | Ensure orchestration map handoffs are linked to prototype actions |
| Simulation shows 100% SLA compliance with no bottlenecks | Sanity check | If SLAs are too loose, the simulation is not useful. Tighten SLAs. |
| Zoom navigation drill-down loses filter context | `context_preservation` check | Verify `zoom_navigation_map` context rules |

---

## Immediate Next Action for PMs

If you are managing a multi-persona product with ProductOS V14:

1. Ensure your `persona_archetype_pack` is complete with ≥3 personas
2. Run `productos workflow orchestrate --prd <id> --personas p1,p2,p3 --detect-gaps`
3. Review the orchestration map for missing handoffs and orphan stages
4. If gaps exist, update your PRD or persona pack and re-run
5. Once the orchestration map is clean, run `productos prototype persona-variants` to generate per-persona views
6. Run `productos simulate handoffs --workflow-id <id> --duration 30d` to predict bottlenecks
7. Iterate on SLAs, handoffs, and parallel paths until the simulation shows acceptable performance
8. Only then proceed to component PRD creation and engineering handoff

---

---

## V14 100x Intent-Driven Architecture Pipeline

ProductOS V14 extends the orchestration model with an **intent-driven architecture pipeline** that generates the full stack from a single natural language statement.

### The 100x Pipeline

```
PM Intent (1-3 sentences)
    → Intent Decomposition (structured problem, personas, outcomes, domain)
    → Master PRD Generation
    → Parallel Architecture Synthesis (6 engines)
    → Cross-Layer Consistency Validation
    → Gap Intelligence (narrative gap detection + fix suggestions)
    → Predictive Simulation (Monte Carlo + bottleneck ranking + what-if)
    → Domain Intelligence (auto-activation + compliance validation)
    → Output Bundle (12 formats + PM Briefing)
```

### Key Differences from Manual Orchestration

| Aspect | Manual V14 | 100x Pipeline |
|---|---|---|
| PM input → First architecture | 2-3 hours of manual commands | <30 seconds from intent |
| Artifact generation | Per-command, sequential | 6 parallel engines |
| Gap detection | On-demand, 1 layer at a time | Cross-layer, proactive with narratives |
| Simulation | Single scenario | 5 auto-generated what-if scenarios |
| Output | Per-command, 1 format | 12 formats in one bundle |
| PM Briefing | None | Auto-generated with confidence levels |

### Using the Pipeline

```bash
# Full pipeline (auto mode)
./productos architect --intent "A HIPAA-compliant prior authorization platform for US providers and payers with AI-assisted review"

# Decomposition only (no artifact generation)
./productos architect --intent "..." --dry-run

# Wizard mode (step-by-step with confirmations)
./productos architect --intent "..." --wizard
```

### Pipeline Components

1. **Intent Engine** (`intent_engine.py`): NLP parsing with domain keyword matching, persona archetype detection, ambiguity flagging, confidence scoring
2. **Architecture Synthesis** (`architecture_synthesis.py`): 6 parallel artifact generators with UUID cross-linking
3. **Gap Intelligence** (`gap_intelligence.py`): 9 gap types with impact narratives, suggestions, auto-fix payloads
4. **Predictive Simulation** (`predictive_simulation.py`): Monte Carlo (10K runs), bottleneck ranking, 5 what-if scenarios
5. **Domain Intelligence** (`domain_intelligence.py`): Auto-activation, compliance gate injection, coverage validation
6. **Architecture Exporter** (`architecture_exporter.py`): 12 output formats including JSON, Markdown, HTML, Mermaid

## Reference

- Execution Plan: `internal/plans/version-history/v14-100x-rich-execution-plan.md`
- Execution Plan (Legacy): `internal/plans/version-history/v14-orchestration-superpowers-execution-plan.md`
- V14.0 Bounded Claim: `core/docs/v14-0-bounded-claim.md`
- V14 Master Bounded Claim: `core/docs/v14-master-bounded-claim.md`
- Domain Extension Pack Architecture: `core/docs/domain-extension-pack-architecture.md`
- Workflow Orchestration Skill: `core/skills/workflow_orchestration_synthesis/SKILL.md`
- PRD Cascade Management Skill: `core/skills/prd_cascade_management/SKILL.md`
