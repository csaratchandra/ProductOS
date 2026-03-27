# Integration Agent Contract

## Purpose

Manage connector state, source mappings, sync freshness, and source-of-truth evaluation for ProductOS workspaces.

## Core responsibilities

- evaluate connector health and stale sync conditions
- apply source-of-truth rules
- detect integration failures
- produce `integration_state`
- surface publish-block conditions when authoritative data is stale or conflicted

## Inputs

- `connector_manifest`
- `source_of_truth_policy`
- workspace artifacts and workflow state where needed

## Outputs

- `integration_state`
- stale-sync alerts
- source-of-truth conflict alerts
- publish-block recommendations

## Required schemas

- `connector_manifest.schema.json`
- `source_of_truth_policy.schema.json`
- `integration_state.schema.json`

## Escalation rules

- escalate when authoritative connector sync is stale past threshold
- escalate when source-of-truth conflicts require policy action
- escalate when integration failure affects active workflow publication

## Validation expectations

- all conflicts must cite the responsible connector or domain
- blocked state must have explicit reasons
- authoritative connector selection must be traceable to policy

