# ProductOS Testing Strategy

ProductOS should be implemented with a contract-first, test-driven approach where possible.

The goal is not only to write artifacts. The goal is to prove that the implementation behaves like the blueprint intends.

## 1. Testing layers

### Contract tests

Every schema should have:

- at least one valid example
- negative examples over time for known failure modes
- automated validation in CI or local test runs

### Workflow tests

Every workflow should eventually have fixture-driven tests that verify:

- required inputs are enforced
- missing-context prompts are targeted rather than broad
- downstream artifact creation happens correctly
- failure rules stop unsafe publication

### Agent contract tests

Each agent contract should be checked for:

- required inputs and outputs
- escalation behavior
- validation expectations
- schema coverage

### Blueprint trace tests

Important blueprint claims should map to:

- a schema
- a workflow
- an agent contract
- a template
- a test or validation check

## 2. Current test baseline

This workspace currently includes:

- JSON parse validation for all schemas and examples
- schema-to-example validation using `jsonschema`

This is only the first testing layer, not the full target state.

## 3. Immediate next testing additions

- negative fixtures for invalid payloads
- workflow fixture tests for transcript-to-notes and status mail generation
- blueprint-to-implementation trace matrix
- publish-block tests for low-confidence and contradictory states

## 4. Implemented trace additions

This workspace now includes:

- a blueprint-to-implementation trace matrix in [blueprint-trace-matrix.md](blueprint-trace-matrix.md)
- publish-block tests for low-confidence, contradiction, and missing-owner reliability conditions
- integration tests for stale and failed authoritative connectors
- V2 lifecycle proof assets including audit, benchmark, and scenario validation reports

## 5. Rule

No new core schema should be added without:

- a valid example
- inclusion in the schema validation test harness
