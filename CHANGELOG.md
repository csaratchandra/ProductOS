# Changelog

## Unreleased

### Added

- internal-only `autonomous_pm_swarm_plan` schema and example
- governed autonomous PM swarm model and hardening workflow docs
- next-version runtime surfacing for internal swarm readiness
- invalid fixture coverage for swarm anti-loop controls

## V7.0.0 - 2026-04-08

ProductOS V7.0.0 promotes lifecycle traceability through `outcome_review`.

### Added

- `./productos v7` for the promoted V7 lifecycle bundle
- public V7 cutover planning support
- starter-template `release_note` and `outcome_review` artifacts
- starter-template launch and outcome review documentation
- public V7 lifecycle bundle tests

### Changed

- the stable ProductOS line is now `V7.0.0`
- the promoted lifecycle claim now extends from `release_readiness` through `launch_preparation` and `outcome_review`
- public examples and runtime evidence refs now use generic workspace-relative paths instead of assuming a tracked `internal/ProductOS-Next/` checkout
- self-hosting-only CLI commands now require `--workspace-dir` when no private default workspace is present

### Validation

- `python3 scripts/validate_artifacts.py`
- `pytest -q`

### Upgrade Notes

- use `templates/` as the supported public adoption surface
- keep private self-hosting work outside product workspaces and promote only reusable repo surfaces
- pass `--workspace-dir` explicitly when running self-hosting-only CLI commands from a checkout without a private internal workspace
