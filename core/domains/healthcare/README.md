# ProductOS Healthcare Domain Pack

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-05-13

This domain pack provides US healthcare intelligence for ProductOS V14.

## Structure

- `base.schema.overlay.json` — FHIR R4 core resources, clinical coding basics
- `regions/us.schema.overlay.json` — HIPAA, CMS, HITECH, X12, CPT/ICD-10/HCPCS, NCPDP
- `workflows/prior_authorization.workflow.json` — CMS 72h SLA, provider → payer flow
- `sub-packs/provider.manifest.json` — EMR integration, clinical documentation
- `sub-packs/payer.manifest.json` — Adjudication, benefits, authorization

## Intelligence Features

- Auto-detection from intent keywords (prior auth, provider, payer, HIPAA)
- CMS 72-hour prior authorization SLA enforcement
- FHIR resource mapping suggestions
- Compliance coverage matrix (HIPAA requirements)
- X12 transaction awareness (278, 837, 835)
