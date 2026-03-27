# ProductOS Feedback Log Triage Workflow

Purpose: Convert ProductOS-specific PM feedback into structured improvement records, backlog candidates, and release proposals without losing the original pain point.

## Inputs

- `productos_feedback_log`
- optional scenario-validation findings
- optional PM benchmark review
- optional improvement registry history

## Outputs

- updated `productos_feedback_log`
- `feedback_cluster_state`
- routed improvement recommendations
- backlog candidate summary
- `release_scope_recommendation` where scope justifies it

## Rules

- preserve the original PM wording of the pain point before compressing it into a recommendation
- distinguish between lifecycle-breaking V2 gaps and runtime-leverage V3 opportunities
- route repeat reliability or usability issues into improvement records instead of leaving them as isolated notes
- if a feedback entry changes release significance materially, emit a release proposal recommendation
- close an entry only when its output path is explicit
