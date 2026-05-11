# V8 Thread Review Upgrade Plan

Status: proposed
Audience: PM, design, engineering, AI implementation
Owner: ProductOS PM
Updated At: 2026-04-09
Depends On: [v8-workspace-adoption-prd.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/v8-workspace-adoption-prd.md)
Mapping Reference: [v8-thread-review-mapping-inventory.md](/Users/sarat/Documents/code/ProductOS/tests/fixtures/workspaces/productos-sample/docs/planning/v8-thread-review-mapping-inventory.md)

## Purpose

This plan upgrades the current V8 thread-review slice from a working generated HTML review page into a stronger ProductOS review surface that remains repo-first, lifecycle-backed, and honest about proof boundaries.

The current baseline already exists:

- `adopt-workspace` emits a `thread_review_bundle`
- `adopt-workspace --emit-thread-page` writes a lightweight HTML page
- `thread-review --item-id ... --output-path ...` can render a page for a V7.3 workspace item

The next job is not to widen scope into a broad PM app. The job is to improve fidelity, trust, review speed, and lifecycle coverage without creating a second system of record.

## Ralph Loop Summary

This upgrade plan is intentionally structured as seven Ralph loops:

1. inspect the current thread-review truth model and prove coverage gaps
2. tighten artifact mapping and lifecycle fidelity
3. improve information hierarchy and visual review speed
4. add actionable review controls and state transitions
5. unify thread review with readable docs and presentation/export surfaces
6. scale from one item to large-product and portfolio review
7. validate release readiness and define the bounded V8 promotion claim

Each loop follows the same discipline:

- inspect
- implement the smallest coherent upgrade
- validate
- fix
- revalidate

## Current Baseline

What is already working:

- one canonical item can be rendered from lifecycle state into a thread page
- adopted workspaces can persist the bundle and page
- V7.3 reference workspace items can be rendered without going through adoption
- the review surface keeps later-stage gaps explicit instead of inventing completeness

Current gaps:

- artifact mapping is still heuristic and concentrated in one runtime file
- the page is readable, but not yet optimized for dense PM review
- the surface is mostly read-only; it does not help drive review closure
- there is no first-class "what changed" or diff-oriented review mode
- there is no portfolio or multi-item index for large products
- readable docs, presentation outputs, and thread review are still adjacent surfaces rather than one governed family

## Loop 1: Truth Model Audit

### Goal

Prove exactly which lifecycle stages and artifact types the thread review surface can and cannot render today.

### Inspect

- audit the current builder against the reference V7.3 workspace and starter workspace
- list every stage and its expected canonical artifact types
- record where the current page falls back to generic stage summaries rather than artifact-backed summaries

### Implement

- create a mapping inventory document for:
  - stage -> expected artifact types
  - artifact type -> panel fields
  - fallback policy when an artifact is missing
- separate "observed coverage" from "planned coverage"

### Validate

- run thread review against:
  - `tests/fixtures/workspaces/productos-sample`
  - an initialized starter workspace
  - an adopted `CodeSync` workspace
- confirm every section declares whether it is:
  - artifact-backed
  - lifecycle-summary-backed
  - intentionally deferred

### Exit Condition

No thread-review section is ambiguous about whether it is real artifact truth or a lifecycle fallback.

## Loop 2: Artifact Mapping Hardening

### Goal

Replace loose runtime heuristics with a more explicit, testable mapping layer.

### Inspect

- identify all places where thread review searches for artifacts by prefix only
- review whether mission-first V7.3 traces and adoption traces are handled with the same confidence
- identify fields that should be normalized before rendering

### Implement

- introduce a dedicated thread-review mapping module or helper layer
- define canonical selectors for:
  - research context
  - problem framing
  - concept
  - prototype
  - PRD
  - story pack
  - acceptance criteria
  - release readiness
  - release note
  - outcome review
- standardize field extraction and fallback ordering

### Validate

- add tests for:
  - reference lifecycle item
  - mission-rebased starter item
  - adoption-generated item
  - missing-artifact fallback behavior

### Exit Condition

Thread review uses an explicit mapping contract instead of ad hoc runtime inference for core sections.

## Loop 3: PM Review Experience Upgrade

### Goal

Make the surface materially faster to review for a PM handling dense product state.

### Inspect

- time-box a realistic PM review using the current page
- identify where the eye has to hunt for:
  - current stage
  - proof strength
  - what changed
  - what is blocked
  - what decision is required now

### Implement

- redesign the page around review velocity:
  - stronger hero summary
  - pinned "needs decision now" strip
  - better stage-rail emphasis
  - explicit confidence and proof badges
  - collapsed low-priority details by default
  - a "current path" mode that highlights only the stages needed for the next decision
- add section-level density modes for:
  - summary
  - standard
  - detailed

### Validate

- run manual PM review against one dense reference item
- confirm the PM can answer in under a few minutes:
  - what this item is
  - where it is
  - what passed
  - what is missing
  - what must happen next

### Exit Condition

The thread page is not only accurate; it is faster to use than opening the underlying artifacts one by one.

## Loop 4: Review Actions And Closure

### Goal

Turn the thread page from a passive reader into an execution-oriented review surface without turning it into a full app.

### Inspect

- find the current gaps between "I can inspect this item" and "I can actually move review forward"
- identify review-driving artifacts:
  - review queue
  - pending questions
  - blocked reasons
  - validation artifacts
  - release checks

### Implement

- add review-action panels that expose:
  - unresolved questions
  - blocked reasons
  - highest-priority review items
  - suggested next command or artifact to update
- add "review status summary" logic:
  - ready for PM review
  - blocked on proof
  - blocked on prototype
  - blocked on delivery definition
  - release-ready but communication incomplete

### Validate

- confirm the page tells the PM what to do next without opening code or JSON first
- add tests proving review queue and pending-question content reaches the rendered page consistently

### Exit Condition

The page helps close review loops rather than only showing lifecycle history.

## Loop 5: Surface Unification

### Goal

Make thread review part of the ProductOS communication system, not a separate rendering island.

### Inspect

- compare overlap across:
  - thread review page
  - readable docs
  - presentation outputs
  - release communication
- identify duplicated summarization logic and drift risks

### Implement

- define a shared summarization layer so docs, thread review, and presentation consume the same normalized panel data where possible
- connect thread review into:
  - readable doc generation
  - presentation/export generation
  - future publication adapters
- decide whether `thread_review_bundle` should become a first-class input for `align`

### Validate

- confirm one canonical item can produce:
  - a thread review page
  - a readable review doc
  - a presentation-ready summary
  without contradictory claims

### Exit Condition

Thread review, readable docs, and presentation surfaces behave like one governed family over the same truth model.

## Loop 6: Scale To Large Products

### Goal

Make the feature usable when a product has many items, long histories, and large artifact sets.

### Inspect

- test with many-item workspace scenarios
- identify scale failure modes:
  - too much content on one page
  - too many artifacts per stage
  - poor navigation between related items
  - no portfolio entry point

### Implement

- add an index or portfolio review surface:
  - item list
  - current stage
  - confidence
  - review status
  - changed recently
- add per-thread navigation improvements:
  - stage anchors
  - compact mode
  - section filters
  - related-item links
- add explicit "thread scope" controls:
  - one item
  - one feature family
  - one release lane

### Validate

- prove a PM can start at a portfolio/index view and reach the right thread quickly
- confirm thread pages remain readable even when artifacts are exhaustive

### Exit Condition

The feature works for both one bounded item and a big product with many threads.

## Loop 7: V8 Release Boundaries

### Goal

Define the truthful bounded claim for V8 and the proof required to promote it.

### Inspect

- compare the implemented slice against the V8 PRD
- review what is still missing for truthful release positioning
- identify what must remain explicitly deferred

### Implement

- write the V8 candidate note, release gate inputs, and validation checklist for thread review
- define the V8 claim boundary precisely:
  - ProductOS can adopt a notes-first workspace into governed lifecycle state
  - ProductOS can render one canonical thread review surface over that state
  - ProductOS does not yet ship a broad collaborative PM web app
- keep external publication adapters and broad portfolio publication deferred unless separately proven

### Validate

- run full validation:
  - targeted pytest coverage
  - schema validation
  - reference review proof
  - adoption benchmark proof
  - manual PM review for one dense item

### Exit Condition

There is one evidence-backed V8 promotion claim with no inflated autonomy or UI scope.

## Proposed Build Sequence

Build in this order:

1. Loop 1 and Loop 2 together
2. Loop 3
3. Loop 4
4. Loop 5
5. Loop 6
6. Loop 7

Reason:

- truth-model clarity must come before UX polish
- UX must come before workflow/action design
- surface unification should happen after the thread page shape stabilizes
- scale work should not precede a strong single-thread experience
- release planning should happen after the above is concretely proven

## Acceptance Upgrades

The feature should be considered strong only when all of the following are true:

- one PM can inspect a dense item thread end to end in minutes
- every major panel is artifact-backed or explicitly marked as lifecycle fallback
- review actions are visible and prioritized
- the same item can power docs, thread review, and presentation without drift
- the feature remains readable for large-product and multi-item contexts
- the V8 claim stays bounded to repo-first governed review, not a broad autonomous PM portal

## Validation Commands

Use these commands as the standing validation baseline:

- `python3 -m pytest tests/test_productos_cli.py tests/test_workspace_adoption.py tests/test_artifact_schemas.py -q`
- `python3 scripts/validate_artifacts.py`
- `python3 scripts/productos.py --workspace-dir tests/fixtures/workspaces/productos-sample thread-review --item-id opp_pm_lifecycle_traceability --output-path /tmp/thread-review.html`
- `python3 scripts/productos.py adopt-workspace --source workspaces/CodeSync --dest /tmp/codesync-review --workspace-id ws_codesync --name "CodeSync" --mode research --emit-thread-page`

## Non-Goals For This Upgrade Plan

- building a live multi-user web app in this loop
- replacing explicit PM review with autonomous decisions
- adding external publication adapters in the same bounded upgrade track
- broadening ProductOS claims past what the repo can prove

## Recommendation

The correct next implementation target is Loop 1 plus Loop 2 together.

That will make the feature more reliable on top of V7.3 before we spend more time on presentation polish or larger-product navigation.
