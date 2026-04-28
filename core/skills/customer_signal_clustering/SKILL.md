# Customer Signal Clustering

## Purpose

Cluster customer and support signals into reusable patterns that can drive priority and outcome decisions.

## Trigger / When To Use

Use when `customer_pulse` or `outcome_review` has many raw signals and the PM needs usable patterns.

## Inputs

- customer evidence
- operator evidence
- support or adoption notes

## Outputs

- support signal clusters
- adoption signal clusters
- priority implications

## Guardrails

- do not mix positive adoption pull with support pain in one cluster
- keep evidence refs on every cluster
- preserve uncertainty when the cluster is weak

## Execution Pattern

1. separate pain from pull
2. group repeated signals into bounded clusters
3. label cluster strength and implications
4. connect the clusters to the next PM decision

## Validation Expectations

- clusters should feel distinct
- each cluster should have evidence refs
- the resulting priority implication should be readable
