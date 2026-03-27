# Stories To Acceptance Workflow

Purpose: Convert a structured `story_pack` into testable `acceptance_criteria_set` outputs without expanding scope beyond the originating story intent.

## 1. Outcome

Produce acceptance outputs that:

- make each story objectively testable
- preserve source intent from the story pack
- expose ambiguity before engineering or QA start delivery
- optionally provide starter test-case structure when useful

## 2. Inputs

Required inputs:

- `story_pack`

Optional inputs:

- `prd`
- requirement and user story entities
- linked feature and persona context
- prior acceptance or QA review notes

## 3. Primary agents

- `orchestrator`
- `librarian`
- `story-acceptance`
- `qa-readiness`
- `validation`

## 4. Workflow steps

### Step 1. Retrieve story intent

The librarian agent gathers:

- the source `story_pack`
- any attached implementation context referenced from the story pack
- linked PRD context where available
- persona, feature, and outcome references
- existing review notes that may already flag ambiguity

### Step 2. Convert each story into observable criteria

The story-acceptance agent writes criteria that:

- remain within the story's stated scope
- use observable, testable statements
- preserve target persona and feature intent
- use attached markdown or other context only to clarify the approved story, never to expand it silently
- avoid implementation-specific assumptions unless already stated upstream

### Step 3. Flag ambiguity early

When a story cannot be tested without guessing, emit ambiguity flags that explain:

- what assumption is missing
- why the criterion is not objectively verifiable yet
- whether clarification should route back to story or PRD revision

### Step 4. Prepare optional QA handoff

Where useful, create:

- `acceptance_criteria_set`
- optional `test_case_set`
- QA-readiness notes for complex or risky stories

### Step 5. Validate for downstream use

The validation and QA-readiness agents check:

- every criterion is observable and testable
- no criterion expands scope beyond the source story
- unresolved ambiguity is explicit rather than hidden

## 5. Trigger conditions

- story pack approval
- story revision affecting acceptance scope
- QA or PM request for testability review

## 6. Failure rules

Do not produce delivery-ready acceptance criteria if:

- story intent is too vague to test objectively
- key assumptions are missing from the story or PRD
- acceptance wording depends on invented downstream scope

In these cases, route back to story clarification or PRD revision instead of forcing completion.

## 7. Outputs

- `acceptance_criteria_set`
- optional `test_case_set`
- ambiguity flags for story clarification
- QA-readiness notes
