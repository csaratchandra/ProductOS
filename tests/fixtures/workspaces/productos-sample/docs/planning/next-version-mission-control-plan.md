# Next-Version Mission Control Plan

Status: active
Owner: ProductOS PM
Updated At: 2026-04-12

## Goal

Turn the system-prompt review into one real ProductOS next-version slice by hardening the repo-native control plane instead of copying vendor prompts.

## Scope

- add mission-boundary and task-boundary visibility to `cockpit_state`
- add mission-boundary, route-budget, route-stage, reviewer-lane, and next-action visibility to `orchestration_state`
- expand `runtime_adapter_registry` into a measurable adapter capability matrix
- add a named mission router and steering context that flow from `mission_brief` into `context_pack` and `memory_retrieval_state`
- expose the new mission-control fields through the `productos` CLI status surfaces
- persist refreshed reference outputs after generation

## Non-Goals

- broaden the external ProductOS claim boundary
- turn ProductOS into an open-ended autonomous PM mesh
- copy vendor-specific UX behavior into ProductOS core

## Verification

- `./productos status`
- `./productos review`
- `./productos run all --persist`
- `python3 scripts/validate_artifacts.py`
- `pytest`

## Why This Slice Matters

The review of external system prompts showed the same pattern repeatedly: the strongest products are not powered by one hidden prompt. They expose mode routing, task boundaries, reviewer gates, validation, and tool capabilities as part of their operating system.

ProductOS already had most of the underlying pieces. This slice makes those pieces more visible, more contractual, and easier to trust from the PM-facing control surface.
