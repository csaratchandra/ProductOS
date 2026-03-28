# Loop Clustering Workflow

Purpose: Turn repeated feedback and gap signals into bounded recurring-pain clusters that can drive governed V4 improvement decisions.

## Inputs

- `productos_feedback_log`
- `feedback_cluster_state`
- `gap_cluster_state`
- `memory_retrieval_state`
- rejected-path and outcome-review memory where relevant

## Outputs

- updated `feedback_cluster_state`
- updated `gap_cluster_state`
- repeated-pain summary for the next improvement gate

## Operating Sequence

1. Gather recent open or repeated pain signals from feedback, issue, and outcome-review sources.
2. Group signals by recurring pain, not by superficial wording similarity alone.
3. Merge prior rejected-path and outcome-review memory so the loop does not rediscover a dead end as a new idea.
4. Record cluster impact, recurrence, and confidence in `feedback_cluster_state` or `gap_cluster_state`.
5. Route only high-signal clusters into the bounded-improvement workflow.

## Rules

- do not create a new cluster when an existing one already explains the pain
- if the evidence is thin, keep the cluster provisional instead of forcing a product change
- clustering quality matters more than cluster count
