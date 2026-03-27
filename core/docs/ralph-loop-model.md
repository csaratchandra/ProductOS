# Ralph Loop Model

Purpose: Define the named umbrella loop that governs inspect, implement, refine, validate, fix, and revalidate work before ProductOS promotes a slice as stable.

Preferred practical shorthand for day-to-day execution is: inspect, implement, refine, validate, fix, and revalidate.

In that shorthand, `refine` is the hardening pass that covers review-driven cleanup, readability improvement, and architecture alignment before formal validation is treated as complete.

## Sequence

### 1. Inspect

- inspect current repo reality
- inspect upstream evidence and freshness
- inspect what is missing before implementation starts

### 2. Implement

- add the bounded code, docs, artifacts, and tests required for the slice
- keep the scope explicit

### 3. Review / Refine

- run logic and traceability review
- separate blocking findings from non-blocking findings
- surface missing assumptions and weak inference
- refine the implementation until the slice is legible, bounded, and aligned with repository rules

### 4. Validate

- run schema, fixture, workflow, and regression checks
- confirm the chosen validation tier
- route disagreement into referee instead of hiding it

### 5. Fix

- address blocking findings from review, validation, and manual review
- record rejected paths and loopholes rather than repeating them silently

### 6. Revalidate

- rerun the same validation surface after fixes
- require one explicit next action: proceed, revise, defer, or block

## Rules

- Ralph does not replace existing V4 validation lanes
- Ralph orchestrates them into one visible loop
- no stable release promotion should skip the fix and revalidate stages
- manual review must name at least one real weakness when weaknesses exist instead of forcing a success-only narrative
