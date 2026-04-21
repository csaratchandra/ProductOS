# Problem Brief To PRD Workflow

Purpose: Convert a validated `problem_brief` into a PRD while preserving target segment, target persona, upstream evidence, and scope discipline.

## 1. Outcome

Produce a `prd` that:

- stays anchored to the validated problem and target user context
- translates evidence into clear scope and outcomes
- preserves traceability to upstream artifacts and entities
- identifies unresolved questions before downstream delivery work starts

## 2. Inputs

Required inputs:

- `problem_brief`

Optional inputs:

- `concept_brief`
- `prototype_record`
- `strategy_context_brief`
- `product_vision_brief`
- `market_strategy_brief`
- linked entities
- workflow constraints
- supporting research artifacts

## 3. Primary agents

- `orchestrator`
- `librarian`
- `prd`
- `strategist`
- `validation`

## 4. Workflow steps

### Step 1. Verify the upstream source bundle

The librarian agent confirms:

- the `problem_brief` is current and canonical
- linked entities and upstream artifacts are available
- prototype and research inputs are attached where they materially affect scope
- strategy context, product vision, and market posture are attached when they constrain scope or positioning

### Step 2. Translate problem framing into requirement framing

The PRD agent drafts:

- problem summary
- outcome summary
- scope summary
- target segment and persona references
- linked entities and upstream artifact references

### Step 3. Check scope discipline

The strategist and PRD agents ensure:

- the PRD does not create unsupported delivery scope
- evidence and outcomes align with requested scope
- unresolved decisions or ambiguities are made explicit

### Step 4. Produce traceability outputs

Generate:

- `prd`
- `artifact_trace_map`
- unresolved-question notes where downstream delivery would otherwise guess

### Step 5. Validate before handoff

The validation agent checks:

- required fields and schema alignment
- traceability to the source `problem_brief`
- preservation of target segment and target persona
- preservation of strategy context, product vision, and market posture constraints when present upstream
- whether remaining ambiguity should route back to research or prototype work

## 5. Trigger conditions

- validated `problem_brief` approval
- PM request to convert discovery output into requirement framing
- substantive revision to the underlying problem or prototype evidence

## 6. Failure rules

Do not produce a committed PRD if:

- no validated `problem_brief` exists
- target user or outcome context is materially missing
- strategy context, product vision, strategic posture, or offering ambiguity remains high enough that downstream delivery would invent product scope
- ambiguity remains high enough that downstream delivery would be forced to infer scope

In these cases, route back to prototype or research rather than forcing a weak PRD.

## 7. Outputs

- `prd`
- `artifact_trace_map`
- unresolved-question list
- handoff recommendation for story creation
