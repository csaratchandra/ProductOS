# Product And Portfolio Tracking Operating Model

Purpose: Define how ProductOS tracks products, features, lifecycle stage, status, and dependencies when Aha/Jira are available and when they are not.

## 1. Rule

ProductOS must support two valid operating modes:

- integrated mode: Aha, Jira, or both provide part of the tracked state
- workspace-manual mode: the PM tracks the same operating state inside ProductOS artifacts without relying on external access

The PM should not lose operating capability just because a connector is unavailable.

## 2. Canonical tracking domains

Regardless of tool choice, ProductOS should track:

- product or workspace identity
- feature identity
- lifecycle stage
- execution status
- owner
- target increment or release
- dependencies
- risks and blockers
- approval state
- last updated timestamp
- linked artifacts and decisions

## 3. Recommended lifecycle stages

Use a stable, simple stage model:

- discovery
- validation
- delivery
- launch
- support

A feature may move forward, pause, or move backward if evidence changes.

## 4. Recommended status values

Use a small status set that works across products and portfolios:

- on_track
- at_risk
- blocked
- done
- parked

These statuses are intentionally operational rather than team-specific.

## 5. Integrated mode

When Aha or Jira are available:

- ProductOS may treat them as authoritative for selected domains
- authoritative domains must be declared in `source_of_truth_policy`
- connector health and freshness must be tracked in `connector_manifest`
- ProductOS should still maintain derived operating artifacts for status, risks, dependencies, and cross-product rollups

Recommended split:

- Aha: roadmap, initiative framing, release planning
- Jira: requirements, stories, delivery execution
- ProductOS: cross-artifact traceability, PM summaries, risk digestion, dependency visibility, leadership renderings, portfolio rollups

## 6. Workspace-manual mode

When the PM does not have Aha/Jira access, ProductOS must fall back to a workspace-managed operating model.

In this mode:

- `workspace_manual` becomes the authoritative connector for the selected domains
- the PM updates ProductOS artifacts directly
- workflows and renderings still operate from structured state rather than freeform notes

Minimum manual operating set per workspace:

- `workspace_manifest`
- `program_increment_state`
- `increment_plan`
- `issue_log`
- `decision_log`
- `status_mail`
- `meeting_record`
- `meeting_notes`
- `item_tracking_log`
- `change_event`
- `change_impact_assessment`

## 7. Manual source-of-truth policy

If no external tracker is available, the default policy should be:

- requirements: `workspace_manual`
- feature_status: `workspace_manual`
- release_planning: `workspace_manual`
- status_reporting: `workspace_manual`
- dependency_tracking: `workspace_manual`

Conflict handling should usually be:

- `prefer_authoritative` for stable workspace records
- `escalate` when notes, meetings, and current state disagree
- `pause_publish` when customer-facing commitments conflict with current approved state

## 8. Manual operating rhythm

The fallback process should stay light and repeatable.

### Daily

- update blockers, owner changes, and dependency shifts
- capture notable change events
- refresh issue log when a blocker or risk changes

### Weekly

- review feature stage and status
- update increment plan
- update program increment state
- refresh decision log
- generate status output

### Monthly

- refresh product health summary
- review portfolio conflicts and shared dependencies
- refresh leadership-facing portfolio output where needed

## 9. Multi-product support

For multi-product setups:

- each product gets its own workspace
- each workspace maintains its own manual or integrated source-of-truth policy
- suite-level rollups are generated above the workspaces
- cross-product dependencies should be represented explicitly rather than inferred from narrative updates

Minimum suite-level visibility:

- workspace status summary
- key initiative or feature status
- cross-product dependencies
- shared risks
- upcoming release or increment milestones

## 10. Practical guidance

Do not try to reproduce all of Jira or Aha inside ProductOS.

The fallback model should capture only the operating state the PM actually needs to:

- know what stage each feature is in
- know whether it is on track
- know what is blocked and why
- know what changed
- know what leadership or partner teams need to hear

## 11. First-class tracking records

ProductOS should use these canonical records for tracking:

- `feature_record`
- `product_record`
- `portfolio_state`

These records complement rather than replace the existing workflow, increment, issue, and decision artifacts.
