# Transcript-To-Notes And Next-Step Extraction Workflow

Purpose: Convert transcripts into human-readable meeting notes and structured meeting records, not raw text dumps, so decisions and follow-through can feed the rest of ProductOS automatically.

## 1. Outcome

Produce:

- a `meeting_notes` artifact for human review
- a `meeting_record` artifact for structured downstream use

The meeting record should contain:

- agenda-aware summary
- decisions
- action items with owners and due dates
- open questions
- issues raised

## 2. Inputs

Required inputs:

- transcript text or transcript reference
- meeting metadata

Optional inputs:

- planned agenda
- prior meeting record
- issue log
- active increment plan
- existing `workflow_state` if resuming
- inbound `handoff_contract` when this transcript is part of a larger execution chain

## 3. Primary agents

- `librarian`
- `status-communications`
- `workflow`
- `detail-guardian`
- `validation`

## 4. Runtime control

Maintain a `workflow_state` artifact from transcript normalization through downstream routing.

Minimum expectations:

- low-confidence extraction regions remain visible in workflow state
- unresolved owner or due-date gaps create targeted PM questions
- downstream workflow routing should emit explicit `handoff_contract` payloads
- blocked transcript confidence should halt auto-approval

## 5. Workflow steps

### Step 1. Normalize transcript

Prepare the transcript into a structured working form:

- preserve timestamps where available
- identify speakers where available
- segment by topic shifts
- mark low-confidence extraction regions

### Step 2. Extract meeting structure

Infer or reconcile:

- actual agenda topics covered
- decisions made
- action items proposed or assigned
- unresolved questions
- risks and issues raised

### Step 3. Render notes and structured record

Build a `meeting_notes` artifact and a `meeting_record` artifact.

Action items must include:

- explicit description
- owner
- due date

If owner or due date is absent from the transcript, the system should mark it as unresolved and request PM confirmation.

### Step 4. Feed downstream systems

Route extracted data into:

- issue log maintenance
- item tracking log maintenance
- status mail drafting
- change event detection
- decision log update

Create a `handoff_contract` for each downstream workflow that needs structured follow-through.

### Step 5. Validate

The validation and detail guardian agents check:

- summary fidelity against transcript evidence
- whether invented certainty was introduced
- whether action items are concrete enough to be useful
- whether next steps conflict with active plans

## 6. Failure rules

Do not auto-approve transcript-derived notes when:

- transcript confidence is low
- speakers are too ambiguous for reliable owner assignment
- the transcript suggests conflicting decisions

In these cases, produce a review-needed draft and targeted PM prompts.

The workflow should remain `review_needed` or `blocked` until confidence or contradiction issues are resolved.

## 7. Outputs

- `meeting_notes`
- `meeting_record`
- `workflow_state`
- `handoff_contract`
- candidate issue updates
- candidate decision updates
- candidate next steps for status mail
