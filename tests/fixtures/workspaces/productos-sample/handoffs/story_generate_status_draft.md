# Story Handoff: Generate Status Draft From Workspace State

## Goal

Generate a PM-ready status draft from trusted workspace artifacts so the PM is not rebuilding progress manually.

## Required Inputs

- current decision log
- current issue log
- current increment plan
- latest follow-up queue

## Output Expectation

- draft status summary
- visible blockers and risks
- explicit next steps
- no invented accomplishments or dates

## Edge Cases

- if source artifacts disagree materially, route to review instead of merging them silently
- if no current progress evidence exists, draft a low-confidence update rather than fabricated momentum
- if issue severity increased since the last draft, surface that change explicitly

## Non-Goals

- do not rewrite the source artifacts
- do not create new delivery scope
- do not publish without PM review
