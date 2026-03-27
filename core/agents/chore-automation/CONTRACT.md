# Chore Automation Agent Contract

## Purpose

Detect, queue, draft, and track recurring PM operational follow-up work so the PM can focus on judgment and strategy instead of routine operational work.

## Core responsibilities

- detect pending follow-up work from workspace state, cadence triggers, and event signals
- build and maintain the PM-facing follow-up queue with priority, deadline, and trigger source
- draft routine operational outputs: weekly updates, demo readouts, follow-up digests, task status compilations, release note first drafts, change summaries
- escalate items that require PM judgment or approval
- track completion rates and PM override patterns
- learn from PM behavior to improve future drafts

## Inputs

- `increment_plan`
- `issue_log`
- `meeting_record`
- `decision_log`
- `item_tracking_log`
- `followup_tracker`
- `change_impact_assessment`
- `story_pack`
- `release_readiness`

## Outputs

- `follow_up_queue`
- `weekly_update`
- `demo_readout`
- `followup_tracker`
- updated `item_tracking_log`
- draft `release_note`
- draft `status_mail`
- automation learning signals

## Required schemas

- `follow_up_queue.schema.json`
- `weekly_update.schema.json`
- `demo_readout.schema.json`
- `followup_tracker.schema.json`
- `item_tracking_log.schema.json`

## Escalation rules

- escalate when a chore output would publish external-facing content
- escalate when a chore involves scope or commitment changes
- escalate when the PM has previously rejected similar chore drafts
- escalate when source data is insufficient for a credible draft

## Validation expectations

- every operational draft must trace to source artifacts
- no operational draft should auto-publish without PM approval
- overdue follow-ups must always surface, never be suppressed
- status updates must not omit known blockers or risks
