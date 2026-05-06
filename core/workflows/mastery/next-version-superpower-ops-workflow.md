# Next Version Superpower Ops Workflow

Purpose: Run the next-version ProductOS build from one repo control surface while dogfooding every major loop inside the current workspace under review.

## Inputs

- the current workspace under review
- inbox notes, transcripts, documents, and support exports
- current decision artifacts such as `problem_brief`, `concept_brief`, and `prd`
- current runtime state such as `cockpit_state`, `orchestration_state`, and `runtime_adapter_registry`
- current `feature_scorecard`, `feature_portfolio_review`, and `improvement_loop_state`

## Outputs

- refreshed runtime state for the next-version control surface
- bounded execution sessions for `discover`, `align`, `operate`, and `improve`
- refreshed feature scorecards and portfolio review
- exportable repo bundle for review, validation, and follow-up work

## Operating Sequence

1. Run `productos doctor` to confirm the repo-backed next-version bundle validates.
2. Run `productos ingest` to route the live inbox into the correct bounded loops.
3. Run `productos run discover` to push the messy-input-to-PRD slice forward first.
4. Run `productos run align`, `productos run operate`, and `productos run improve` to keep downstream alignment, weekly operation, and self-improvement active behind the same control surface.
5. Run `productos review` to inspect pending review points and every sub-`5/5` gap.
6. Run `productos export` when a bounded slice needs to be shared or validated outside the live workspace.

## Rules

- the current ProductOS workspace is the canonical dogfood environment for the next version
- every major loop must stay explainable through repo-visible artifacts rather than hidden tool state
- thin adapters may change the driver tool, but they must not change ProductOS logic or scoring rules
- every feature below `5/5` must route feedback into the existing improvement loop
- do not claim a superpower until the loop is repeatable, low-rewrite, and benchmark-backed in live workspace use
