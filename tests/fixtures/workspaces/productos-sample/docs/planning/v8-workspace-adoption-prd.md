# Workspace Adoption And Thread Review PRD

Status: proposed
Audience: PM, design, engineering, AI implementation
Owner: ProductOS PM
Updated At: 2026-04-09
Source Artifact: `prd_workspace_adoption_superpower`

## Project Specifics

- Working name: `Workspace Adoption And Thread Review`
- Candidate release: V8 bounded slice candidate
- Benchmark workspace: [workspaces/CodeSync](/Users/sarat/Documents/code/ProductOS/workspaces/CodeSync)
- Primary CLI surface: `./productos adopt-workspace`
- Primary review surface: lightweight generated thread page over one canonical lifecycle item

## Goals And Business Objectives

- let a PM point ProductOS at an existing notes-first workspace and get usable ProductOS state on the first pass
- reduce the setup burden that currently prevents messy real work from becoming ProductOS artifacts
- convert research, strategy, and customer-context material into governed artifacts instead of leaving them as disconnected markdown packs
- let a PM review one canonical thread from problem through launch and outcome without reopening raw notes end to end
- make ProductOS adoption credible for products that did not start from `./productos init-workspace`

## Background And Strategic Fit

`workspaces/CodeSync` is strong as a manual research pack, but it is not a ProductOS workspace. It lacks `inbox/`, `artifacts/`, `handoffs/`, `workspace_manifest.yaml`, and the first-class artifacts that ProductOS expects when running `ingest`, `discover`, `align`, and lifecycle trace flows.

That failure mode is product-significant. ProductOS currently works best after a user has already accepted the ProductOS workspace model. It is weaker when the user starts with a real product folder containing notes, research, presentation drafts, screenshots, and mixed evidence. If ProductOS cannot absorb that reality and propose the right artifact set itself, the user will keep doing research and planning outside the system.

The V8 slice should close that gap by making ProductOS convert an existing workspace into governed ProductOS state with explicit provenance and inference boundaries, then render that same state as one lightweight review surface for PM inspection.

## Problem Statement

ProductOS does not yet provide a reliable workspace-adoption path from arbitrary product folders into first-class ProductOS artifacts and lifecycle state, and it does not yet expose the resulting item trace as one lightweight PM review surface.

Today the user must already know how to:

- restructure files into ProductOS directories
- decide which workflows should run
- infer which artifacts should exist
- create those artifacts manually or through indirect runtime paths

That is too much hidden setup work. In a workspace such as `CodeSync`, the result is that high-value product thinking remains trapped in notes and slide material instead of becoming durable ProductOS operating state.

Even after adoption, PM review is still too fragmented. The canonical lifecycle trace exists, but the PM still has to jump between artifacts, docs, and generated outputs instead of inspecting one item thread from problem through release communication and outcome review.

## Assumptions

- many real product workspaces begin as markdown notes, exported docs, screenshots, and ad hoc research packs
- the first useful adoption step is not perfect automation, but high-confidence bootstrap plus explicit review of uncertain inferences
- ProductOS must preserve provenance and distinguish `observed`, `inferred`, and `hypothesis` content rather than flattening them
- persisted workspace artifacts matter more than runtime-only bundle output for adoption credibility
- ProductOS should reuse the existing lifecycle traceability model as the canonical backbone for review instead of inventing a second UI-only workflow model

## User Stories

- as a PM, I want to point ProductOS at an existing product folder and get a suggested ProductOS workspace rather than rebuilding structure by hand
- as a PM, I want ProductOS to infer an initial artifact set from my notes and research so I do not have to translate everything manually
- as a PM, I want deep research outputs to refresh or create ProductOS artifacts, not only produce markdown reports
- as a PM, I want ProductOS to show what was observed, what was inferred, and what still needs confirmation
- as a PM, I want one canonical lifecycle item and initial stage placement so the work can move through the ProductOS model immediately
- as a PM, I want a review queue for low-confidence inferences before ProductOS treats them as product truth
- as a PM, I want one thread page that lets me move from problem to concept to prototype to PRD to story to release communication without losing artifact lineage

## Capability Definition

The V8 capability is `workspace adoption, artifact inference, and thread review`.

It should let ProductOS:

1. detect that a source folder is not yet a ProductOS workspace
2. classify existing files into notes, research, customer context, workflow notes, visuals, drafts, and raw evidence
3. normalize those inputs into an `inbox` plus structured evidence summaries
4. propose `recommended_workflow_ids` and `derived_artifact_ids`
5. generate the first-pass artifact set for discovery and early product definition
6. persist those artifacts into a destination ProductOS workspace
7. create one canonical lifecycle item with an explicit current stage
8. emit a confidence report and unresolved-review queue
9. generate one lightweight thread review surface over the same canonical lifecycle item

The review surface must leverage the existing lifecycle traceability capability already proven through V7. It is a rendering and navigation layer over canonical ProductOS artifacts, not a new lifecycle model.

## Functional Requirements

### 1. Workspace Detection

- detect whether the source path is already a ProductOS workspace
- detect missing ProductOS primitives such as `inbox/`, `artifacts/`, `handoffs/`, and `workspace_manifest.yaml`
- summarize the current source shape before any conversion begins

### 2. Evidence-Driven Intake

- ingest arbitrary source folders instead of relying only on fixed inbox folder names
- classify files by evidence type and likely downstream use
- preserve source file path, capture time when known, and importer metadata
- build a persisted `intake_routing_state` with non-empty `recommended_workflow_ids`

### 3. Ask-To-Artifact Bootstrapping

- infer and create a minimum artifact set from the source material
- minimum first-pass set:
  - `idea_record`
  - `research_brief`
  - `problem_brief`
  - `concept_brief`
  - `segment_map`
  - `persona_pack`
  - `prd`
  - `item_lifecycle_state`
- artifact generation must include provenance references back to the source inputs used

### 4. Inference Discipline

- every generated statement that is not direct evidence must be marked as `inferred` or `hypothesis`
- confidence should be attached at the artifact or section level where practical
- conflicting notes should create review items instead of being silently merged

### 5. Persisted Adoption Output

- ProductOS must write the adopted artifacts into the destination workspace
- runtime summaries alone are insufficient
- the destination workspace should be valid enough to run `./productos ingest`, `./productos run discover`, and lifecycle trace commands

### 6. Review And Gap Surfacing

- produce an adoption report that explains:
  - what was adopted with high confidence
  - what was inferred
  - what artifacts could not be generated safely
  - what human review is required next
- create a review queue for missing proof, contradictory evidence, and low-confidence mappings

### 7. Thread Review Surface

- generate a lightweight PM review page for one canonical lifecycle item after adoption completes
- the page must reuse existing ProductOS lifecycle stages, not introduce a parallel stage model
- the page must let the PM inspect, at minimum:
  - problem framing
  - segments and personas
  - market and competitor context
  - concept
  - prototype
  - PRD
  - story pack and acceptance criteria
  - release readiness
  - release note or launch communication
  - outcome review when present
- the page must keep source refs, open questions, risks, and confidence visible without forcing the PM to open each backing artifact first
- the page may start as generated HTML and repo-local assets before any richer app shell exists

## CLI And API Shape

### CLI

```text
./productos adopt-workspace \
  --source /path/to/existing-workspace \
  --dest /path/to/adopted-workspace \
  --workspace-id ws_codesync \
  --name "CodeSync" \
  --mode research
```

Optional flags:

- `--in-place` to adopt into an existing destination workspace after safety checks
- `--review-threshold medium|high` to control how aggressively uncertain inferences are routed to review
- `--emit-report` to write an adoption summary markdown document
- `--emit-thread-page` to write the generated thread review page for the canonical lifecycle item
- `--dry-run` to preview the inferred artifact set without writing files

### API

```python
adopt_workspace(
    source_dir: Path,
    dest_dir: Path,
    workspace_id: str,
    name: str,
    mode: str = "startup",
    review_threshold: str = "medium",
    generated_at: str | None = None,
) -> dict[str, dict]
```

Required output payload keys:

- `workspace_adoption_report`
- `intake_routing_state`
- `idea_record`
- `research_brief`
- `problem_brief`
- `concept_brief`
- `segment_map`
- `persona_pack`
- `prd`
- `item_lifecycle_state`
- `lifecycle_stage_snapshot_discovery`
- `adoption_review_queue`
- `thread_review_bundle`

## Artifact Contracts

The V8 slice should add or promote the following contracts:

- `workspace_adoption_report`
  - source summary
  - destination summary
  - detected workspace mode
  - generated artifact ids
  - confidence summary
  - unresolved questions
- `adoption_review_queue`
  - review item id
  - source refs
  - uncertainty type
  - recommended reviewer action
- `thread_review_bundle`
  - canonical item ref
  - ordered stage sections
  - panel summaries
  - pinned risks, questions, and decisions
  - source artifact refs
- upgraded `intake_routing_state`
  - real source classification
  - explicit `derived_artifact_ids`
  - confidence-aware workflow recommendations

## Interaction And Design References

The adoption flow should feel like a conversion wizard for PM reality, not a developer-only import utility.

The PM should be able to inspect:

- what ProductOS found
- what it decided
- what it refused to assume
- what artifact set it created
- what the resulting canonical thread looks like end to end

The output should remain repo-first and diff-friendly. The first review surface should be a lightweight generated page over the repo state, not a detached system of record.

## Acceptance Criteria

### Benchmark Scenario: `CodeSync`

Given [workspaces/CodeSync](/Users/sarat/Documents/code/ProductOS/workspaces/CodeSync),
when ProductOS runs `adopt-workspace`,
then it should:

- detect that the source is not yet a ProductOS workspace
- classify the existing research pack and notes into reusable evidence inputs
- create a destination workspace with ProductOS starter structure
- generate at least the minimum first-pass artifact set listed above
- create one canonical lifecycle item for the CodeSync product thesis
- produce an adoption report that distinguishes `observed`, `inferred`, and `hypothesis`
- emit review items for unsupported commercial, security, or performance claims
- generate one canonical thread review page for the adopted item
- leave the destination workspace runnable through `ingest` and `run discover`

### Quality Bar

- no generated artifact may omit provenance for non-trivial claims
- no unsupported marketing claim may be silently promoted to fact
- contradictory source inputs must produce a review item
- `dry-run` and persisted runs must produce the same inferred artifact plan
- the PM must be able to review the adopted workspace without reading the original notes pack end to end
- the thread review page must be traceable back to canonical artifacts rather than storing product truth separately

## Non-Goals

- perfect autonomous product strategy generation from arbitrary files
- replacing targeted PM review for ambiguous or commercial claims
- external publication adapter coverage in the same bounded slice
- a broad multi-page PM application before the repo-native adoption path and thread page are stable

## Open Questions

- should adoption create one canonical item by default or allow multiple inferred items on the first pass
- what confidence threshold should block `prd` generation and route only to `problem_brief` plus `research_brief`
- should the first destination always be a new workspace, with in-place adoption deferred
- how much artifact overwrite behavior is safe when adopting into a partially existing workspace
- should the first thread review page be emitted only for the primary canonical item or for every inferred item above a confidence threshold

## Out Of Scope

- SharePoint and Confluence publication adapters
- broad packaging and collateral export flows
- automated pricing or commercial truth validation beyond explicit review flags
- deep multi-item portfolio migration from a very large legacy repo on the first bounded slice
