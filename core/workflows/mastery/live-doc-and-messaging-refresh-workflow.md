# Live Doc And Messaging Refresh Workflow

Purpose: Refresh ProductOS product docs and messaging docs from current source artifacts without letting claims drift ahead of the product.

## Inputs

- current product truth in `artifacts/`
- current readable docs under `workspaces/<workspace>/docs/`
- `document_sync_state` for the live-doc bundle
- benchmark, release, and market-intelligence artifacts where relevant
- current rejected-path and Ralph-loop records

## Outputs

- updated product and messaging markdown docs
- updated `document_sync_state`
- validation and manual-review records
- explicit proceed / revise / defer guidance for the next promotion step

## Operating Sequence

1. Inspect which product facts, workflow claims, and differentiators changed since the last refresh.
2. Update product docs first so the reader can understand what ProductOS is, who it serves, and how to start.
3. Update messaging docs second so positioning and proof are derived from the refreshed product truth.
4. Run AI review against unsupported claims, vague language, and benchmark drift.
5. Run AI test checks for metadata, source linkage, required sections, and sync-state completeness.
6. Route the bundle through targeted PM Leader manual validation before broader publication or presentation reuse.
7. Record any blocked claims or overreach in a rejected-path record instead of leaving them implicit.

## Rules

- product docs and marketing docs must share the same approved source-artifact base
- do not let the messaging bundle promise autonomy, freshness, or coverage beyond the current evidence
- if a new claim cannot be defended with source artifacts or explicit benchmark proof, remove it or defer it
- if the docs become materially stale, mark the bundle as drifted rather than pretending it is current
