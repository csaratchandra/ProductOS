# V10.1 PM Startup Simplification Note

Status: draft candidate  
Audience: PM, engineering, design, leadership  
Owner: ProductOS PM  
Updated At: 2026-05-05

## Summary

This slice simplifies the ProductOS Day-1 experience for a new PM.

The main change is that `./productos start` is now the public beginner surface. Instead of requiring a dense set of flags, it can guide a PM through:

1. starting a new workspace
2. bringing existing work into ProductOS

The flow keeps setup vocabulary simple, asks for `Startup` or `Enterprise`, and frames the first success target as the first deliverable ProductOS should help create.

## What Changed

- `./productos start` now supports a guided interactive path
- `./productos start --non-interactive` preserves the scripted advanced path
- `start --kind import` routes through the existing workspace adoption logic
- guided startup derives `workspace_id` automatically from the workspace name
- guided startup derives `maturity_band` from workspace mode:
  - `startup -> zero_to_one`
  - `enterprise -> one_to_ten`
- guided startup maps first-win choices to internal mission defaults:
  - strategy brief
  - problem brief
  - PRD
  - research pack
  - roadmap / plan

## Why This Matters

The previous startup path was technically correct but too dense for a first-time PM.

It exposed repo and schema concepts too early:

- `workspace-id`
- `success-metric`
- `maturity-band`
- `operating-mode`

This slice reduces Day-1 setup friction and aligns the user-facing promise more closely with the actual product idea:

- help a PM get started on a product much faster
- let ProductOS generate the first coherent working surface
- keep advanced control available without making it mandatory

## Proof In Repo

Implementation:

- `scripts/productos.py`
- `README.md`
- `core/docs/product-workspace-starter-guide.md`
- `templates/README.md`
- `tests/test_productos_cli.py`

Verification run:

- `python3 scripts/productos.py start --help`
- `pytest tests/test_productos_cli.py`

Observed result:

- `51 passed, 3 skipped`

## Non-Goals

- no GUI onboarding
- no change to the underlying mission schema contract
- no release-version bump or stable-line promotion in this slice alone
- no claim expansion beyond the proof now present in the repo
