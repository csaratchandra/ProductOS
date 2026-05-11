# ProductOS Design And Architecture Review

This review should happen step by step.

That is the right level for ProductOS because most of the current complexity is in workflow boundaries, handoffs, and control-state claims rather than in any one isolated artifact.

## Review Method

For each workflow step, capture:

- purpose
- inputs
- transformation
- outputs
- downstream consumer
- review or validation gate
- failure modes
- notes for next version

The main question for each step is not only "does it exist?" but also:

- is the input real or seeded?
- is the output freshly produced or reused from example artifacts?
- is the handoff explicit?
- can the step fail honestly?
- does the control surface surface real problems, or does it default to success?

## Repo Control Workflow

### 1. `doctor`

Purpose:
Validate that the next-version bundle is structurally healthy.

Inputs:

- workspace artifacts
- next-version bundle builder
- artifact schemas

Outputs:

- validation result
- selected adapter status
- intake item count
- top priority feature id

Outcome:
Fast health check for the repo-native control surface.

Review notes:

- current check is useful for schema validity, but it is not a truthfulness check
- a healthy result does not prove that the workflow is actually producing fresh or trustworthy outputs

### 2. `ingest`

Purpose:
Route inbox content into the right bounded workflows.

Inputs:

- `inbox/raw-notes`
- `inbox/transcripts`
- `inbox/documents`
- `inbox/support-exports`

Outputs:

- `intake_routing_state`

Outcome:
A normalized list of intake items with recommended workflow ids and derived artifact targets.

Review notes:

- routing is currently static by folder type
- this looks more like a declared routing map than an evidence-driven intake system

### 3. `run discover`

Purpose:
Turn messy inputs into a decision-ready package.

Inputs:

- live inbox files
- current workspace problem and concept context
- current benchmark and runtime state

Outputs:

- `discover_problem_brief`
- `discover_concept_brief`
- `discover_prd`
- `discover_execution_session_state`
- `discover_feature_scorecard`

Outcome:
A same-day discover-to-PRD package that can be reviewed and scored.

Review notes:

- the current implementation depends on exact file names in the inbox
- the discover slice is generated in memory by the bundle builder instead of being persisted as first-class workspace artifacts
- this makes the runtime look stronger than the actual repo state

### 4. `run align`

Purpose:
Package current product truth into readable docs and deck artifacts.

Inputs:

- PRD
- readable-doc sync state
- presentation artifacts

Outputs:

- `align_document_sync_state`
- `align_execution_session_state`
- docs alignment scorecard
- presentation scorecard

Outcome:
A stakeholder-ready aligned package.

Review notes:

- this step appears to rely mostly on existing example and prior-release artifacts
- it is not yet clear which outputs are freshly regenerated versus inherited

### 5. `run operate`

Purpose:
Turn current queues and issue state into one supervised PM operating loop.

Inputs:

- decision queue
- follow-up queue
- status mail
- issue log

Outputs:

- `operate_execution_session_state`
- `operate_status_mail`
- `operate_issue_log`
- weekly operator scorecard

Outcome:
A weekly operator session with a review-ready status output.

Review notes:

- current outputs look reused from seeded artifacts, not produced by a live operating loop
- the step is architecture-valid but runtime-thin

### 6. `run improve`

Purpose:
Turn scorecards into explicit improvement work.

Inputs:

- feature portfolio review
- improvement loop state

Outputs:

- `improve_execution_session_state`
- self-improvement scorecard
- refreshed portfolio review

Outcome:
The next bounded improvement slice should be made visible.

Review notes:

- the current model claims this loop routes sub-5 work
- in practice the bundle currently declares all named slices as `5/5`, so the loop cannot expose much real tension

### 7. `review`

Purpose:
Show pending review points and unresolved sub-5 features.

Inputs:

- cockpit state
- feature portfolio review

Outputs:

- pending review points
- sub-5 feature list

Outcome:
A PM-readable summary of what needs attention next.

Review notes:

- if the scorecards are over-optimistic, this review step becomes untrustworthy
- current output can report "all clear" even when the underlying architecture still has important gaps

### 8. `trace`

Purpose:
Expose lifecycle progress by item or stage.

Inputs:

- `item_lifecycle_state`
- `lifecycle_stage_snapshot`

Outputs:

- item timeline view
- stage snapshot view

Outcome:
A traceable PM-facing explanation of where work is in the lifecycle.

Review notes:

- the current CLI advertises `discovery`, `delivery`, `launch`, `outcomes`, and `full_lifecycle`
- only `discovery` currently resolves in the workspace
- this is a concrete control-surface mismatch, not just a future enhancement

### 9. `export`

Purpose:
Write the current next-version bundle to a portable output folder.

Inputs:

- the generated next-version bundle

Outputs:

- exported JSON artifact set

Outcome:
A shareable package for review and external validation.

Review notes:

- export is useful
- but today it exports a bundle that mixes runtime truth, seeded examples, and computed claims

## Initial Architecture Problems

### 1. Runtime, fixture, and scoring are too tightly coupled

The next-version bundle builder is acting as:

- runtime orchestrator
- artifact generator
- scoring engine
- release narrator

That makes it hard to distinguish what is actually true in the workspace from what the bundle says should be true.

### 2. Success is too easy to declare

The current control surface reports a healthy bundle and all named superpower slices at `5/5`.

That makes the system weak at self-critique.

If we already believe there are several problems, the current review and scoring layer is not sensitive enough.

### 3. Fresh runtime production is unclear

Several steps appear to be composed from example artifacts or prior artifacts rather than from freshly persisted outputs of the current run.

That weakens trust in every downstream claim.

### 4. Workflow boundaries are explicit, but artifact ownership is blurry

The workflow stages are named well, but it is still hard to answer:

- which artifacts are canonical inputs
- which artifacts are derived outputs
- which outputs must be persisted
- which outputs are only bundle-local summaries

### 5. The trace model is incomplete at the stage-snapshot level

The item lifecycle model covers the full path from intake to outcome review.

The stage snapshot surface does not yet cover the same scope.

That leaves the PM with incomplete observability across delivery, launch, and outcomes.

## Next-Version Improvement Directions

- separate seeded examples from live runtime outputs
- persist live run outputs as first-class workspace artifacts
- score from evidence instead of assigning the final score inside the same builder that creates the evidence
- require review surfaces to show uncertainty, drift, and disagreement
- make every CLI step declare canonical inputs and persisted outputs
- close the mismatch between `trace` command options and available lifecycle stage snapshots

## Suggested Review Sequence

1. Review the repo control workflow step by step using the sections above.
2. For each step, mark `real`, `seeded`, or `mixed`.
3. For each step, mark whether the output is persisted, derived-in-memory, or only reported.
4. For each step, record one trust problem and one next-version fix.
5. After that, redesign scoring and review so the system can fail honestly.
