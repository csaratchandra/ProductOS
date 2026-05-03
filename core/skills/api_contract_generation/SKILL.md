# API Contract Generation

## 1. Purpose

Generate OpenAPI-compliant API contracts from user stories, including endpoint definitions, request/response schemas, authentication requirements, error codes, rate limits, and developer documentation.

## 2. Trigger / When To Use

Story pack complete with stories specifying API interactions. Developer handoff pack being assembled. PM or engineering requests technical specification.

## 3. Prerequisites

- Current feature prioritization data (feature_prioritization_brief, prioritization_decision_record)
- Engineering team structure and velocity data (from capacity_model or PM input)
- OKR or strategic objectives defined for the planning period
- (Recommended) PESTLE analysis and market context
- (Recommended) Previous roadmap scenario for comparison

## 4. Input Specification

| Field | Type | Source | Required | Notes |
|---|---|---|---|---|
| `feature_backlog` | `array[object]` | feature_prioritization_brief, prioritization_decision_record | Yes | Prioritized features with story points |
| `team_data` | `array[object]` | PM input or capacity_model | Yes | Team velocity, headcount, allocation |
| `time_horizon_months` | `integer` | PM input | Yes | Planning horizon (3-24 months) |

## 5. Execution Steps

1. Scan stories for API interactions: Identify stories that describe external-facing endpoints or data exchange. Extract: resource, action, data shape.
2. Define endpoints: Per interaction: method (GET/POST/PUT/PATCH/DELETE), path, summary. Follow REST conventions.
3. Specify request: Content type, path/query/header parameters, body schema with types. Include example body.
4. Specify responses: Success (200/201) with body schema. Error responses (400/422/401/429/500) with error codes and resolution hints.
5. Define auth: Type (bearer, api_key, oauth2). Header name. Required scopes.
6. Define rate limiting: Requests per minute, burst limit, rate limit headers.
7. Add common errors: Reusable error responses (401, 429, 500) applicable to all endpoints.
8. Link back to stories: Tag each endpoint with originating story_ref for traceability.

## 6. Output Specification

Primary output artifact: specified in schema reference below.

## 7. Guardrails

- Endpoint not grounded in story: API contract specifies endpoint with no corresponding user story → flag. Every endpoint must trace to at least one story.
- Missing error responses: Only success path specified → require at minimum: 401, 422, 500. Production APIs fail.
- When to escalate: Auth model undefined — security review required before contract can be finalized. Rate limiting conflicts with story requirements (story needs 1000 rpm, infrastructure supports 100).

## 8. Gold Standard Checklist

- [ ] Every endpoint traces to at least one user story
- [ ] All success AND error responses are specified
- [ ] Example bodies are realistic (not {"key": "value"})
- [ ] Auth model is specified per endpoint
- [ ] OpenAPI 3.0 compatible — generated contract validates against spec
- [ ] Framework alignment: validates against OpenAPI 3.0 specification, REST API design (Fielding), API-first development
- [ ] Every recommendation includes explicit evidence basis
- [ ] PM has clear next action with owner and timeline

## 9. Examples

See example artifacts in `core/examples/artifacts/`.

## 10. Cross-References

- **Upstream skills**: story_decomposition_and_ambiguity_detection, non_functional_requirement_extraction
- **Downstream skills**: developer_handoff_pack assembly, technical review
- **Schemas**: api_contract.schema.json, story_pack.schema.json

## 11. Maturity Band Variations

| Band | Depth Adjustment |
|---|---|
| 0→1 | Exhaustive: multiple scenario modeling with qualitative depth. Capacity model lean — early team is small. |
| 1→10 | Deep: 3-scenario model. Capacity modeling important — team scaling. |
| 10→100 | Standard: 2-scenario model. Capacity modeling data-driven. Resource allocation focus. |
| 100→10K+ | Focused: portfolio-level scenarios. Capacity modeling across multiple teams. |

## 12. Validation Criteria

- **Schema conformance**: validates against associated schemas
- **Test file**: TBD in target sprint
- **Example fixture**: see associated `.example.json` files
