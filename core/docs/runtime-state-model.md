# ProductOS Runtime State Model

Purpose: Define the minimum control-plane artifacts that make the V3 runtime visible, explainable, and testable.

## Internal Boundary

These runtime-state artifacts are internal ProductOS operating records.

They exist so ProductOS can dogfood and verify live runtime behavior while building later versions.

They should not be treated as a PM-facing feature promise by themselves.

## Runtime-State Artifacts

### `cockpit_state`

PM-facing control-surface state.

Use it to show:

- current operating mode
- current focus
- active specialist visibility
- queue visibility
- queue-driven recommendations for what the PM should review or unblock next
- the next controlled step
- review and blocker context

### `orchestration_state`

Multi-agent coordination state.

Use it to show:

- routing plan
- route rationale
- current specialist path
- handoffs between agents
- retries
- escalations
- dependencies across routes
- queue impacts caused by blocked, review, or active routes

### `execution_session_state`

Bounded work-session state.

Use it to show:

- what session was created
- why it exists
- which adapter supports it
- whether review is required
- verification progress
- completion or failure outcome

### `runtime_adapter_registry`

Host-capability registry for live runtime behavior.

Use it to show:

- which runtime adapters exist
- whether each adapter is available, limited, planned, or unavailable
- which actions are supported
- what host constraints apply

### `intake_routing_state`

Continuous intake and routing state.

Use it to show:

- which inbox items were captured
- whether provenance is complete
- which downstream workflows should receive each item
- which items are blocked before normalization

### `memory_retrieval_state`

Baseline retrieval state for prior context reuse.

Use it to show:

- what prior context was requested
- which records were retrieved
- freshness and confidence of each retrieved record
- provenance warnings and unresolved gaps

### `feedback_cluster_state`

Internal learning-loop state.

Use it to show:

- repeated ProductOS pain clusters
- which clusters are strong enough to affect release scope
- whether the next route is backlog, improvement, or release-scope review

## Interaction Model

The intended relationship is:

1. `cockpit_state` frames the PM-visible situation
2. `orchestration_state` turns that framing into controlled routing and visible route rationale
3. `execution_session_state` tracks bounded subtask execution and review
4. `runtime_adapter_registry` explains which execution surfaces are actually available
5. `intake_routing_state` shows what new raw inputs entered the system and where they are being routed
6. `memory_retrieval_state` shows what prior context was reused to reduce reconstruction work
7. `feedback_cluster_state` shows when repeated ProductOS pain is strong enough to influence staged-release planning

This keeps the runtime explainable without overloading `workflow_state` with every control-plane concern.

## Relationship To Existing State Artifacts

- `workflow_state` remains the canonical state for an individual workflow run
- `reliability_state` remains the canonical state for confidence and publish blocking
- `integration_state` remains the canonical state for connector and source-of-truth health

The new runtime-state artifacts do not replace those records.

They add the missing control-plane layer needed for a live cockpit and specialist swarm.

## Visibility Rule

If the runtime is doing meaningful coordination work, the PM should be able to answer:

- what is active now
- which specialist is doing it
- what is blocked
- what needs PM review
- which queue item should be handled next
- which adapter or host capability is being relied on

If those answers are not visible in state, the runtime is still too implicit.

## Coordination Rule

Visible coordination should flow like this:

1. `orchestration_state` records the active, blocked, and review-needed routes plus the rationale for each route
2. `orchestration_state` emits queue impacts when a route requires PM review, approval, or escalation
3. `cockpit_state` surfaces those queue impacts as queue-driven recommendations in the PM control surface

This keeps queue behavior tied to real runtime state rather than leaving it as a detached artifact list.
