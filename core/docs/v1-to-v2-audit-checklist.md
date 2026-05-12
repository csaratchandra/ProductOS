# ProductOS V1 to V2 Audit Checklist

Purpose: Verify that ProductOS V2.0 is materially better than V1.0 on the important PM operating dimensions and does not regress on core capabilities.

## How To Use This Audit

- compare V1 and V2 side by side
- score each dimension as:
  - `regressed`
  - `same`
  - `improved`
  - `materially improved`
- require evidence, not intuition
- do not mark a dimension as improved if V2 only added more structure without reducing PM work or increasing quality

## Audit Dimensions

### 1. PM lifecycle coverage

Check whether V2 covers the full PM lifecycle more clearly than V1:

- current-state assessment
- discovery
- prioritization and planning
- delivery execution
- launch readiness and release communication
- post-launch learning
- ProductOS improvement loop

Evidence to inspect:

- [README.md](../../README.md)
- [current-state-assessment-workflow.md](../workflows/discovery/current-state-assessment-workflow.md)
- one explicit workspace manifest, if available outside the public repo boundary

### 2. PM terminology and usability

Check whether V2 uses familiar PM language more consistently than V1.

Audit:

- user-facing artifact names
- workflow names
- queue names
- workspace documentation

Look for drift into internal system language or AI-agent jargon.

### 3. Reference workspace capability

Check whether V2 can operate ProductOS itself as a product more cleanly than V1.

Audit:

- dedicated reference workspace
- lifecycle artifacts in the workspace
- release and adoption records
- improvement records feeding back into core

Evidence to inspect:

- one private explicit workspace, if available outside the public repo boundary
- [registry/releases](../../registry/releases)
- [registry/improvements](../../registry/improvements)

### 4. Note capture and raw-input intake

Check whether V2 captures notes and raw product inputs well enough to start product work.

Audit:

- idea capture
- meeting notes and meeting records
- source note cards
- research notebook
- workspace inbox support

Important:

- V2 now includes note-oriented artifacts plus a scaffolded workspace `inbox/` in the reference workspace
- the inbox is wired to the inbox normalization workflow so raw material can convert into structured evidence

### 5. ProductOS feedback logging

Check whether ProductOS has a separate, first-class mechanism to collect feedback about ProductOS itself.

Audit:

- structured improvement registry entries
- PM pain-point logging
- rejected output logging
- repeated workflow-friction logging
- dedicated ProductOS feedback artifact or workflow

Important:

- V2 has improvement records
- V2 now also has a dedicated ProductOS feedback-log artifact and triage workflow

### 6. Discovery quality

Check whether V2 improves discovery over V1 in practical PM terms.

Audit:

- better current-state framing
- better research routing
- better evidence structure
- better customer feedback synthesis
- stronger problem framing

Evidence to inspect:

- discovery workflows
- research workflows
- customer pulse
- research notebook and note-card paths

### 7. Prioritization and decision quality

Check whether V2 improves PM decision making over V1.

Audit:

- decision queue support
- strategy option generation
- decision premortem support
- uncertainty framing
- explicit tradeoff handling

Evidence to inspect:

- [decision_queue.schema.json](../schemas/artifacts/decision_queue.schema.json)
- decision-intelligence workflows

### 8. Delivery handoff quality

Check whether V2 improves the path from approved product thinking into build-ready execution.

Audit:

- PRD quality
- story and acceptance criteria support
- handoff contracts
- traceability from problem to execution
- change-impact support

### 9. Launch and communication support

Check whether V2 is stronger than V1 on the PM work around launches and updates.

Audit:

- release readiness
- release notes
- weekly and biweekly updates
- meeting-to-follow-up support
- leadership-ready renderings

### 10. Reliability and governance

Check whether V2 is safer and more trustworthy than V1.

Audit:

- validation presence
- publish-block concepts
- reliability workflows
- integration/compliance review support
- standalone validation and tests

Evidence to inspect:

- [testing-strategy.md](testing-strategy.md)
- [reliability-and-uncertainty-workflow.md](../workflows/reliability/reliability-and-uncertainty-workflow.md)

### 11. Cockpit and orchestration maturity

Check whether V2 is closer than V1 to the Jarvis model.

Audit:

- cockpit contract
- orchestrator contract
- specialist agent coverage
- workflow routing
- visible decision and follow-up queue concepts

Important:

- V2 has the architecture
- V2 does not yet have a full live Jarvis runtime with observable agent swarm behavior

This should score as `improved`, not `complete`.

### 12. Measurable PM leverage

Check whether V2 proves better PM leverage, not just more assets.

Audit:

- time-to-first-draft improvements
- lower rewrite rates
- better traceability
- fewer missing-context loops
- lower PM coordination overhead

Important:

- V2 has benchmarking docs, scenario validation, and a V1-to-V2 benchmark report

## Minimum Outcome To Call V2 Better Than V1

V2 should only be called clearly better than V1 if:

- no critical dimension is marked `regressed`
- at least half of the major dimensions are marked `improved` or `materially improved`
- the known gaps are explicitly recorded and not hidden

## Remaining Non-V2 Items

- no full live Jarvis runtime or agent swarm execution layer yet

This remaining item is intentionally deferred to V3 rather than treated as an unfinished V2 gap.
