# Thin Agent Adapter Model

Purpose: Define how ProductOS supports Codex, Claude-style agents, Windsurf, Antigravity, and similar tools without making any one of them the system.

## Core Rule

The repo owns the operating model.

Each tool adapter stays thin.

Thin means the adapter only explains:

- how to inspect the repo
- how to start a bounded run
- how to capture review findings
- how to run validation
- how to request approval where needed

It does not own:

- feature logic
- schema rules
- benchmark rules
- release rules
- hidden memory

## Capability Matrix Rule

Thin adapters should still be measurable.

Every adapter entry should declare:

- supported ProductOS mission stages
- whether mission routing is native or repo-managed
- whether task-boundary visibility is native or repo-managed
- whether research freshness, validation, delegation, approval gating, memory steering, and artifact export are native, repo-managed, limited, or unsupported

This keeps ProductOS portable without pretending every host supports the same operating mechanics equally well.

## Default Adapter Actions

Every thin adapter should expose the same basic actions:

- `inspect_repo`
- `run_superpower_loop`
- `capture_review_findings`
- `run_validation`
- `export_artifacts`

## Current Posture

Codex, Claude-style, Windsurf, and Antigravity now clear the same repo-contract parity proof in this repo.

That verification means ProductOS proved the same bounded actions, artifact surfaces, and validation expectations without rewriting ProductOS logic per host.

Direct host-native execution should still keep using those same bounded actions rather than adding host-specific product behavior.
