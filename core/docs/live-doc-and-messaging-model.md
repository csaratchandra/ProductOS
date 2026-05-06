# Live Doc And Messaging Model

Purpose: Define how ProductOS should keep product documentation and market-facing messaging live, governed, and traceable.

## Problem

ProductOS has readable operating docs, but it is still weak on the documents that explain the product itself to a human reader.

That gap creates three risks:

- the product truth lives in scattered internal artifacts
- marketing copy drifts ahead of what the product can actually defend
- every new update requires manual PM reconstruction instead of governed refresh

## Decision

Treat live product docs and messaging docs as part of the same governed document system as PRDs, roadmaps, and research reviews.

Do not treat marketing as a side channel that can bypass source artifacts, validation, or Ralph review.

## Standard Surface

Every ProductOS workspace should maintain a live bundle with at least these docs:

- `docs/product/product-overview.md`
- `docs/product/getting-started.md`
- `docs/marketing/positioning.md`
- `docs/marketing/messaging-house.md`

Optional follow-on docs once the bundle is stable:

- release notes or launch summary
- website or homepage copy pack
- one-pager for buyer or partner conversations
- demo narrative or live walkthrough script

## Source Of Truth

The source of truth for live docs and messaging is still the structured artifact layer.

Typical source artifacts:

- `problem_brief`
- `concept_brief`
- `prd`
- `increment_plan`
- `pm_superpower_benchmark`
- `research_feature_recommendation_brief`
- `presentation_brief`
- release metadata and improvement records where relevant

## Governance Rule

Market-facing messaging is a governed rendering of product truth, not an independent storytelling system.

That means:

- messaging may simplify
- messaging may prioritize
- messaging may choose audience fit
- messaging may not invent unsupported capability, proof, or certainty

## Refresh Cadence

Minimum cadence:

- refresh after every stable release
- refresh after every accepted bounded improvement that changes positioning or workflow scope
- refresh after material market-intelligence findings change differentiation or claim boundaries

## Validation Tier

Default validation tier for the live-doc and messaging bundle:

- `tier_2` inside the repo

Escalate to `tier_3` when:

- a leadership presentation is derived from the messaging bundle
- external publication or broad distribution is imminent
- the claims materially change ProductOS category, autonomy, or benchmark posture

## Ralph Expectations

The live-doc and messaging bundle should pass a Ralph loop before promotion:

1. inspect current docs, product truth, market evidence, and stale claims
2. review the plan and name likely drift risks
3. implement the updated docs and sync state
4. validate traceability, consistency, and required metadata
5. fix unsupported claims, weak phrasing, or ambiguous boundaries
6. revalidate and emit one explicit next action

## Claim Boundaries

The following claims should remain blocked unless new evidence exists:

- ProductOS is a fully autonomous PM replacement
- ProductOS already provides unattended safe market refresh
- ProductOS already guarantees buyer-ready outputs without PM review

## Success Standard

The slice is successful when:

- a new reader can understand what ProductOS is without reading raw JSON
- messaging matches the product reality visible in the workspace
- the PM can update product and marketing docs through one governed loop instead of ad hoc rewriting
