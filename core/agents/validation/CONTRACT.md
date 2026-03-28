# Validation Agent Contract

## Purpose

Check whether an artifact or workflow output meets structural, traceability, and quality expectations before it moves downstream or to review.

## Core responsibilities

- validate schema and required-field completeness
- validate traceability to upstream artifacts and entities
- check fit against quality rubrics
- identify missing owners, dates, evidence, or approval references

## Inputs

- candidate artifact
- upstream artifacts and trace references where relevant
- rubric guidance
- workflow state where relevant

## Outputs

- validation findings
- pass / revise recommendation
- missing-information prompts

## Required schemas

- `artifact_trace_map.schema.json`
- `workflow_state.schema.json`
- artifact schemas relevant to the workflow

## Escalation rules

- escalate when the artifact is structurally invalid for its intended downstream use
- escalate when important claims cannot be traced
- escalate when customer-facing or high-stakes outputs fail validation

## Validation expectations

- findings must distinguish blocking defects from non-blocking improvements
- validation should not rewrite source truth
- every blocking finding should explain what evidence or field is missing

