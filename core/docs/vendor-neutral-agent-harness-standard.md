# Vendor-Neutral Agent Harness Standard

Purpose: Define a tool-agnostic operating standard for running ProductOS with Codex, Claude, Windsurf, OpenCode, Antigravity, or other approved coding agents without making any single tool the system of record.

## Core Rule

The harness and repository are canonical.

The agent is a driver of the system, not the system itself.

That means:

- standards live in versioned docs, schemas, scripts, tests, and CI
- product and architecture knowledge lives in the repository
- tool-specific prompts and adapters stay thin and replaceable
- no critical workflow should depend on one vendor's UI or proprietary memory

## Design Goals

- remain portable across multiple agent tools
- preserve one operating model even when teams switch drivers
- keep human effort focused on intent, acceptance criteria, and judgment
- make runtime behavior legible enough that agents can inspect and fix their own work

## Required Repository Contracts

Every agent-capable ProductOS repository should define these contracts in-repo:

1. `AGENTS.md`
2. architecture and workflow docs in `core/docs/` or workspace docs
3. execution-plan conventions for non-trivial work
4. validation commands that any tool can run locally
5. artifact schemas and examples
6. CI gates that enforce the same rules regardless of which tool authored the change

`AGENTS.md` should stay short and act as a map, not a giant manual.

Detailed knowledge should live in durable documents close to the code and workflows they govern.

## Tool-Agnostic Operating Model

Humans steer. Agents execute.

Humans are responsible for:

- choosing priorities
- defining acceptance criteria
- deciding release and risk posture
- raising taste and architecture rules into mechanical checks
- reviewing ambiguous or high-judgment decisions

Agents are responsible for:

- inspecting current repo and runtime reality
- implementing bounded changes
- updating docs and artifacts required by the change
- running validation
- responding to review feedback
- proposing the next bounded fix when validation fails

## Supported Tool Classes

The standard is intentionally compatible with:

- Codex
- Claude Code and Claude-style coding agents
- Windsurf
- OpenCode
- Antigravity
- future approved agent runners

Differences between tools are expected in:

- context window behavior
- built-in review loops
- tool and browser integration
- approval and sandbox models
- prompt syntax

Those differences should be isolated behind adapter guidance, not embedded into the core operating model.

## Adapter Rule

Each tool may have a thin adapter layer that explains:

- how to start work
- how to load repository context
- how to run the standard validation commands
- how to capture review findings
- how to open or update a pull request

Adapters may vary.

The following may not vary by tool:

- architecture constraints
- schema requirements
- release gates
- evidence freshness rules
- benchmark thresholds
- Ralph loop completion requirements

## Repository-As-System-Of-Record

If an agent cannot discover something from the repo or approved runtime surfaces, it should be treated as missing.

Do not rely on:

- Slack-only decisions
- hidden prompt lore
- one-off human memory
- vendor-hosted project state that is not mirrored in-repo

Push durable decisions into:

- markdown docs
- structured artifacts
- examples and fixtures
- executable plans
- validation scripts

## Ralph Overlay

ProductOS should run major changes through a Ralph loop on top of the vendor-neutral harness.

The practical sequence is:

1. inspect
2. implement
3. refine
4. validate
5. fix
6. revalidate

Interpretation:

- inspect: gather repo state, requirements, evidence freshness, and missing context
- implement: make the smallest bounded change that can satisfy the task
- refine: improve traceability, readability, architecture fit, and edge-case handling before claiming completion
- validate: run schemas, fixtures, tests, workflow checks, and benchmark-sensitive checks
- fix: address failures and blocking findings, then capture rejected paths or loopholes when useful
- revalidate: rerun the relevant surface and emit one explicit outcome: proceed, revise, defer, or block

This sequence complements the existing Ralph review model.

`refine` is the practical hardening pass between initial implementation and formal validation.

## Standard Change Flow

For any non-trivial task:

1. start from a short prompt plus repo-local context
2. inspect current reality before editing
3. create or update an execution plan when the task is multi-step or long-running
4. implement one bounded slice
5. refine the slice until the output is legible and aligned with repository rules
6. validate locally
7. fix failures and record meaningful rejected paths
8. revalidate
9. promote only when the outcome is explicit

## Guardrails

Encode standards as checks whenever possible.

Preferred mechanical guardrails:

- schema validation
- example fixture validation
- dependency-boundary checks
- naming and logging conventions
- file-size or complexity limits where useful
- doc freshness checks for high-value system-of-record docs
- benchmark or rubric-based regression checks for important workflows

Human review should focus on judgment and product quality, not rediscovering missing mechanical rules.

## Efficiency Rule

Efficiency does not come from asking agents to try harder.

It comes from improving the harness:

- clearer repository maps
- better execution plans
- stronger validation
- more legible runtime feedback
- thinner tool adapters
- faster fix and revalidate loops

## Adoption Standard

A team may prefer one agent tool operationally while still remaining tool-agnostic structurally.

That is the recommended posture:

- preferred tool for default throughput
- portable repo contracts for resilience
- common Ralph loop for quality
- common validation surface for every agent

## Decision

ProductOS should be built so the repository can be driven by multiple approved agent tools.

Codex may be the reference driver for some workflows, but it must not be the only environment capable of satisfying the repository's operating rules.
