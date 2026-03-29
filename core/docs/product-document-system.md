# Product Document System

Purpose: Define the standard human-readable document surface that ProductOS should maintain alongside structured artifacts.

## Why This Exists

Structured JSON artifacts are strong system-of-record inputs for validation, routing, and automation.

They are not sufficient for the PM's real job.

PMs need readable documents that can be reviewed, shared, presented, published, and kept current without forcing every stakeholder to inspect raw JSON.

If ProductOS is itself a product for PMs, the document system must also cover live product communication and market-facing messaging, not only internal operating docs.

## External Reference Basis

This document uses public Atlassian and Microsoft guidance as the baseline for practical product-document and publication behavior:

- Atlassian PRD guidance emphasizes a consistent template, project specifics, goals, strategic fit, assumptions, user stories, design links, open questions, and explicit out-of-scope sections.
- Atlassian Product Vision Board guidance emphasizes vision, target audience, problem space, solution, business goals, and next steps.
- Atlassian product roadmap guidance emphasizes team mission, project information, quarterly planning, high-level roadmap overviews, and frequent updates for stakeholders.
- Microsoft SharePoint guidance emphasizes content types, managed metadata, document sets, metadata navigation, and version history for reusable document management.

Reference URLs:

- https://www.atlassian.com/agile/product-management/requirements
- https://www.atlassian.com/software/confluence/templates/product-vision-board
- https://www.atlassian.com/software/confluence/templates/product-roadmap
- https://support.microsoft.com/en-us/office/create-and-edit-content-types-3d5d45af-608d-4183-8d51-073095fe0312
- https://support.microsoft.com/en-us/office/create-a-managed-metadata-column-8fad9e35-a618-4400-b3c7-46f02785d27f
- https://support.microsoft.com/en-us/office/create-and-manage-document-sets-c71d5796-d559-48de-b1b3-42383bdd13ea
- https://support.microsoft.com/en-us/office/how-versioning-works-in-lists-and-libraries-0f6cd105-974f-44a4-aadb-43ac5bdfd247

## ProductOS Standard

ProductOS should use a dual-representation model:

- structured artifact: canonical machine-readable state in JSON
- readable document: human-facing markdown document generated from, linked to, or synchronized with the structured artifact

The two forms should share the same logical identity, version lineage, and review status.

## Document Lanes

ProductOS should treat readable documents as three connected lanes rather than one flat set.

### 1. Operating docs

These are the internal product-operating documents used to move from discovery through release.

Required docs:

- discovery summary
- problem brief
- concept brief
- prototype review
- product strategy or vision
- roadmap
- PRD

### 2. Live product docs

These are the always-current documents that explain the product itself.

Required docs:

- product overview
- getting started
- release notes or current release summary
- capability map or workflow overview when the product has become broad enough that a single overview is no longer sufficient

### 3. Messaging docs

These are the market-facing narrative documents that convert product truth into clear positioning.

Required docs:

- positioning brief
- messaging house
- leadership-ready one-pager or presentation brief for major communication moments

## Required Human-Readable Documents

### 1. Discovery Summary

Audience:

- PM
- leadership
- design
- engineering

Minimum sections:

- context and trigger
- evidence summary
- user or customer pain
- opportunity framing
- risks and unknowns
- recommended next step

Primary source artifacts:

- `current_state_assessment`
- `source_note_card`
- `research_notebook`
- `research_brief`
- `customer_pulse`

### 2. Problem Brief

Audience:

- PM
- design
- engineering leads
- leadership

Minimum sections:

- problem statement
- who is affected
- why this matters now
- evidence and confidence
- current workaround costs
- constraints
- recommendation

Primary source artifact:

- `problem_brief`

### 3. Concept Brief

Audience:

- PM
- design
- research
- leadership

Minimum sections:

- concept summary
- hypothesis
- target audience
- why now
- why us
- success signal
- open questions

Primary source artifact:

- `concept_brief`

### 4. Prototype Review

Audience:

- PM
- design
- engineering
- leadership

Minimum sections:

- prototype objective
- prototype format
- audience and scenario
- what was tested
- what was learned
- decision
- next step

Primary source artifact:

- `prototype_record`

### 5. Product Strategy / Vision

Audience:

- leadership
- cross-functional stakeholders

Minimum sections:

- vision
- target audience
- problem space
- solution direction
- business goals
- strategic fit
- next bets

Primary source artifacts:

- `concept_brief`
- `research_brief`
- `market_strategy_brief`
- `decision_log`
- `strategy_option_set`

### 6. Roadmap

Audience:

- leadership
- cross-functional stakeholders
- delivery teams

Minimum sections:

- team mission
- planning horizon
- now / next / later or quarter-by-quarter view
- item owner
- status
- dependencies
- linked evidence and PRDs

Primary source artifacts:

- `increment_plan`
- `program_increment_state`
- `decision_queue`

### 7. PRD

Audience:

- PM
- design
- engineering
- data / AI implementation

Minimum sections:

- project specifics
- goals and business objectives
- background and strategic fit
- assumptions
- user stories or workflow expectations
- interaction and design references
- open questions
- out of scope

Primary source artifact:

- `prd`

### 8. Product Overview

Audience:

- leadership
- go-to-market
- design
- engineering
- external evaluators

Minimum sections:

- product definition
- target PM user
- problem solved
- operating model
- primary workflows
- differentiators
- current release status

Primary source artifacts:

- `problem_brief`
- `concept_brief`
- `pm_superpower_benchmark`
- relevant release metadata

### 9. Getting Started

Audience:

- PM
- operators
- internal adopters
- early design partners

Minimum sections:

- when to use ProductOS
- workspace structure
- first-run loop
- expected outputs
- validation and review rules
- next recommended action

Primary source artifacts:

- `prd`
- `increment_plan`
- `workspace_manifest`
- relevant workflow definitions

### 10. Positioning Brief

Audience:

- leadership
- product marketing
- design
- sales or partnerships

Minimum sections:

- category statement
- ideal customer profile
- acute problem
- why existing tools are not enough
- ProductOS differentiation
- proof points
- claim boundaries

Primary source artifacts:

- `problem_brief`
- `research_feature_recommendation_brief`
- `pm_superpower_benchmark`
- `presentation_brief`

### 11. Messaging House

Audience:

- leadership
- go-to-market
- founder or PM communicator

Minimum sections:

- master narrative
- audience segments
- value pillars
- proof for each pillar
- objection handling
- claims to avoid

Primary source artifacts:

- `concept_brief`
- `research_feature_recommendation_brief`
- `presentation_brief`

## Repository Layout Standard

Every workspace should support this layout:

```text
workspaces/<workspace>/
  artifacts/                  structured system-of-record json
  docs/
    discovery/
    strategy/
    prototype/
    planning/
    product/
    marketing/
    research/
  handoffs/                   execution-facing markdown context
  feedback/                   product feedback notes
```

Rules:

- `artifacts/` remains canonical for validation and automation
- `docs/` is canonical for stakeholder-readable publication inside the repo
- every readable document should name the source artifact ids it was derived from
- every readable document should carry status, owner, audience, and updated-at metadata near the top
- every market-facing claim should trace back to a source artifact, benchmark, release record, or named rejected-path boundary
- live product docs and messaging docs should participate in `document_sync_state`; they are not exempt from drift review because they are "marketing"

## External Publishing Model

### SharePoint

Recommended mapping:

- one document library for product docs per workspace
- content types for operating docs, live product docs, and messaging docs
- managed metadata for product, audience, stage, release, owner, and status
- document sets for grouped work products such as one initiative, release, or communication bundle
- versioning enabled for all published docs

### Confluence

Recommended mapping:

- one page tree per workspace
- one page per readable document
- shared labels for product, audience, stage, release, and status
- backlinks to structured artifact ids and repository paths
- rendered roadmap, PRD, product overview, and positioning pages kept synchronized with repository source

## Upgrade Recommendation

This should be treated as a product capability, not optional polish.

Reason:

- PM influence and update work is core product work
- without live docs, ProductOS remains too internal and too system-facing
- without governed messaging docs, marketing drift will outrun the product truth
- repository-backed readable docs are the foundation for later presentation, publishing, and app integrations

Recommended sequencing:

1. add the standard operating-doc set and repository structure
2. add live product docs and messaging docs with explicit source-artifact linkage
3. add generation or synchronization from structured artifacts
4. add publication adapters for SharePoint, Confluence, or site surfaces
5. add stronger visual and presentation quality with UI/UX design support
