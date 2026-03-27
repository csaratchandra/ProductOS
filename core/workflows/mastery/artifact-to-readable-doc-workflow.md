# Artifact To Readable Doc Workflow

Purpose: Generate a readable product document from validated source artifacts while preserving traceability, audience fit, and sync ownership.

## Inputs

- [product-document-system.md](/Users/sarat/Documents/code/ProductOS/core/docs/product-document-system.md)
- [validation-tier-policy.md](/Users/sarat/Documents/code/ProductOS/core/docs/validation-tier-policy.md)
- source artifact such as `problem_brief`, `concept_brief`, `prototype_record`, `prd`, `increment_plan`, or `release_gate_decision`
- readable-doc template or target section standard
- current document metadata rules and audience expectations

## Outputs

- readable markdown document
- `document_sync_state`
- draft routing guidance for the next validation lane

## Operating Sequence

1. Confirm the document type, target audience, and required sections for the selected artifact.
2. Pull only the source fields and evidence that are appropriate for the readable document.
3. Generate the markdown document with explicit status, owner, audience, updated-at, and source-artifact metadata.
4. Record the generated or updated document in `document_sync_state` with sync status and source refs.
5. Route the document into `AI Reviewer` and `AI Tester`, then add manual validation if the chosen tier requires it.

## Rules

- do not invent unsupported claims while filling readability gaps
- keep the source artifact as the system of record and the readable doc as the governed human-facing form
- if required metadata or traceability is missing, stop and mark the document for revise rather than silently publishing
- do not let freeform manual edits break source linkage without updating `document_sync_state`
