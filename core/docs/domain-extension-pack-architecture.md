# ProductOS Domain Extension Pack Architecture

**Purpose:** Define the composable domain extension system that layers industry-specific and region-specific knowledge on top of core ProductOS artifacts.  
**Status:** V14.0 Foundation — domain content ships in V14.1+  
**Last Updated:** 2026-05-13

---

## The Problem

ProductOS core is intentionally domain-agnostic. It speaks in personas, journeys, PRDs, and workflows — not in HL7 FHIR, FIX protocol, or PCI-DSS. This is a feature, not a bug. Core ProductOS should work for a social media startup, a healthcare platform, a capital markets trading system, or a retail omnichannel experience without modification.

But domain specificity is unavoidable. A healthcare workflow needs HIPAA checkpoints. A finance workflow needs PCI-DSS gates. A social media workflow needs content moderation policies. If we embed domain logic into core, we destroy the domain-agnostic principle. If we ignore domain logic, ProductOS cannot serve regulated industries.

The solution: **domain extension packs** that layer on top of core artifacts without changing them.

---

## The Three-Layer Model

Every domain extension pack supports three composable layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: WORKFLOW PATTERNS (Optional)                      │
│  Pre-built orchestration maps for common scenarios           │
│  Example: "prior_authorization.workflow.json"               │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: REGIONAL OVERLAY (Optional)                       │
│  Country/regulation-specific requirements                    │
│  Example: "us.schema.overlay.json" for HIPAA + CMS         │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: BASE OVERLAY (Required)                           │
│  Universal data models, terminology, cross-regional standards  │
│  Example: "base.schema.overlay.json" for FHIR R4           │
└─────────────────────────────────────────────────────────────┘
```

### Base Overlay (Layer 1)

The base overlay defines what is universal across all regions in a domain:
- **Data models:** Common entity definitions, relationships, cardinalities
- **Terminology:** Controlled vocabularies, code sets, standard identifiers
- **Cross-regional standards:** International standards that apply regardless of region
- **Workflow primitives:** Common actions, states, and transitions that appear in all regional variants

**Constraints:**
- A base overlay cannot reference any regional overlay.
- A base overlay must be valid JSON Schema that extends (adds fields to) core ProductOS schemas.
- Base overlay additions are additive only — they never remove or redefine core schema fields.

### Regional Overlay (Layer 2)

The regional overlay adds country-specific or regulation-specific requirements:
- **Regulators:** Named regulatory bodies and their requirements
- **Compliance frameworks:** Specific rules, checkpoints, and audit requirements
- **Regional standards:** National or regional standards that override or extend international standards
- **Terminology extensions:** Region-specific codes, identifiers, and classifications

**Constraints:**
- A regional overlay must validate against its base overlay. It can only add fields, not remove base fields.
- A regional overlay cannot contradict its base. If base defines `Patient.identifier` as required, no regional overlay can make it optional.
- A workspace can activate multiple regions of the same pack (e.g., a product serving US and EU markets).

### Workflow Pattern (Layer 3)

Workflow patterns are pre-built orchestration maps for common domain+region scenarios:
- **Trigger conditions:** When this workflow starts
- **Persona roles:** Which personas participate, with domain-specific role names
- **Handoff definitions:** Standard handoffs with domain-specific data payloads
- **SLA templates:** Common SLA targets for this scenario in this region
- **Compliance gates:** Pre-configured checkpoints from the regional overlay

**Constraints:**
- A workflow pattern validates against the domain pack's base + activated regional overlay.
- Workflow patterns are templates, not instances. The PM customizes them for their specific product.
- Multiple workflow patterns can coexist in one workspace.

---

## File System Layout

```
core/domains/
  healthcare/
    README.md                           # Pack documentation: what it covers, how to activate
    base.schema.overlay.json            # Universal: FHIR R4 core resources, clinical coding basics
    regions/
      us.schema.overlay.json            # HIPAA, CMS, HITECH, X12, CPT/ICD-10/HCPCS, NCPDP
      eu.schema.overlay.json            # GDPR health provisions, MDR, IVDR, EMA
      uk.schema.overlay.json            # NHS Digital, GP systems, MHRA
      ca.schema.overlay.json            # PIPEDA, provincial privacy, CIHI
      au.schema.overlay.json            # My Health Record, Australian Medicines Terminology
      in.schema.overlay.json            # DPDP Act, ABDM, HMIS
      # Additional regions added in future versions
    workflows/
      prior_authorization.workflow.json     # US-specific: provider → payer auth flow
      eligibility_verification.workflow.json # US-specific: benefits check
      claims_submission.workflow.json       # US-specific: 837/835 lifecycle
      clinical_trial_enrollment.workflow.json # EU/International: CTIS workflow
      # Additional patterns added in future versions
    sub-packs/                           # Optional granular activation
      provider.manifest.json              # EMR integration, clinical documentation
      payer.manifest.json                 # Adjudication, benefits, authorization
      insurer.manifest.json               # Policy administration, risk, underwriting
      government.manifest.json            # CMS reporting, MACRA/MIPS
      pharma.manifest.json                # Clinical trials, FDA 21 CFR Part 11
      lifescience.manifest.json           # LIMS, specimen tracking
      # Sub-packs reference base + regions; they don't define new schemas

  finance/
    README.md
    base.schema.overlay.json            # Risk terminology, audit patterns, common compliance
    regions/
      us.schema.overlay.json            # SEC, FINRA, CFTC, OCC, Federal Reserve
      eu.schema.overlay.json            # MiFID II, EMIR, ECB, EBA
      # UK (FCA, PRA) → V14.3
      # Singapore (MAS), Hong Kong (HKMA) → future versions
    workflows/
      trade_execution.workflow.json       # FIX protocol, order management
      post_trade_processing.workflow.json # Confirm, clear, settle
      collateral_management.workflow.json # Margin, collateral, liquidity
      account_opening.workflow.json       # KYC, CDD, EDD, identity verification
      payment_processing.workflow.json    # Cards, ACH, wire (deferred to Payments sub-pack)
    sub-packs/
      capital_markets.manifest.json       # FIX, OMS, derivatives, clearing
      banking.manifest.json               # PCI-DSS, SWIFT, core banking, AML/KYC
      payments.manifest.json              # ACH, SEPA, RTP, FedNow, crypto (V14.4)
      insurance.manifest.json             # P&C, life, reinsurance (V14.5)
      wealth_management.manifest.json     # Portfolio, trust, family office (future)

  social_media/
    README.md
    base.schema.overlay.json            # Content taxonomy, engagement models, user trust
    regions/
      us.schema.overlay.json            # CCPA, COPPA, Section 230
      eu.schema.overlay.json            # GDPR, Digital Services Act, ePrivacy
      in.schema.overlay.json            # DPDP Act, IT Rules 2021
      # Additional regions in future versions
    workflows/
      content_moderation.workflow.json    # Upload → Review → Decision → Appeal
      creator_monetization.workflow.json    # Content → Ad matching → Payout
      trust_safety.workflow.json          # Report → Investigation → Action → Appeal
    sub-packs/
      content_moderation.manifest.json    # Moderation queues, appeal workflows
      creator_economy.manifest.json         # Monetization, payouts, tax forms
      growth_loops.manifest.json          # Referral, viral mechanics, engagement

  # Additional domain packs in V14.5+ (SaaS/GenAI, Retail, Media & Entertainment)
```

---

## Schema Overlay Mechanism

A schema overlay is a JSON document that declares additions to core ProductOS schemas. It does not replace the core schema — it extends it.

### Overlay Format

```json
{
  "schema_version": "1.0.0",
  "pack_id": "healthcare",
  "layer": "base",
  "region": null,
  "overlays": [
    {
      "target_schema": "workflow_orchestration_map.schema.json",
      "additions": {
        "properties": {
          "clinical_data_model_refs": {
            "type": "array",
            "items": { "type": "string" },
            "description": "FHIR resource references for shared artifacts"
          }
        }
      }
    },
    {
      "target_schema": "component_prd.schema.json",
      "additions": {
        "properties": {
          "data_model_refs": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "standard": { "type": "string", "enum": ["FHIR_R4", "HL7_v2", "X12"] },
                "resource": { "type": "string" },
                "profile": { "type": "string" }
              }
            }
          }
        }
      }
    }
  ]
}
```

### Validation Rules

1. **Target schema must exist.** The overlay cannot add fields to a schema that doesn't exist in core.
2. **Additions only.** The overlay cannot remove, redefine, or change the type of existing core fields.
3. **No required overrides.** The overlay cannot make an optional core field required. It can add new required fields that the overlay introduces.
4. **Enum extensions allowed.** The overlay can add new enum values to core enum fields, but cannot remove existing values.
5. **Regional overlay validates against base.** Before a regional overlay is accepted, it must validate that all its additions are compatible with the base overlay.

### Activation and Merge

When a domain pack is activated:

```bash
productos domain enable --pack healthcare --region us --sub-pack provider,payer
```

ProductOS performs the following merge:

1. Load base overlay for `healthcare`
2. Load `us` regional overlay for `healthcare`
3. Validate regional against base (must be additive and non-contradictory)
4. Load `provider` and `payer` sub-pack manifests
5. Validate sub-packs against base + regional
6. Merge all additions into a unified overlay document
7. Register the merged overlay in the workspace's `domain_extension_state.json`
8. All artifact validation in the workspace now includes the merged overlay constraints

### Multiple Packs in One Workspace

A workspace can activate multiple domain packs:

```bash
productos domain enable --pack healthcare --region us --sub-pack provider
productos domain enable --pack finance --region us --sub-pack banking
```

**Cross-pack validation rules:**
1. Each pack's overlay is validated independently.
2. If two packs add fields with the same name to the same core schema, the field definitions must be compatible (same type, same structure).
3. If two packs add fields with the same name but incompatible definitions, the activation is blocked with an error message identifying the conflict.
4. A workspace can have multiple regions of the same pack active simultaneously.

---

## Sub-Pack System

Sub-packs are not schema overlays. They are **manifests** that reference base + regional overlay fields and declare which workflow patterns and persona archetypes are relevant.

### Sub-Pack Manifest Format

```json
{
  "sub_pack_id": "provider",
  "pack_id": "healthcare",
  "required_base_fields": ["clinical_data_model_refs", "data_model_refs"],
  "required_region": "us",
  "persona_archetypes": [
    {
      "archetype_type": "user",
      "role_name": "Clinical Provider",
      "workflow_traits": ["emr_integration", "clinical_documentation", "prescription_management"]
    },
    {
      "archetype_type": "operator",
      "role_name": "Medical Coder",
      "workflow_traits": ["icd_10_coding", "cpt_coding", "claims_preparation"]
    }
  ],
  "workflow_patterns": ["prior_authorization", "eligibility_verification", "claims_submission"],
  "compliance_checkpoints": [
    {
      "name": "HIPAA_Audit_Log",
      "required_for_handoffs": true,
      "required_for_data_access": true
    }
  ]
}
```

### Activation

Sub-packs are activated as part of the `domain enable` command:

```bash
productos domain enable --pack healthcare --region us --sub-pack provider,payer,insurer
```

If a sub-pack requires a region that is not activated, the activation fails with a clear error.

---

## Domain Validation

After activating a domain pack, the workspace can be validated:

```bash
productos domain validate --pack healthcare --region us
```

Validation checks:
1. All activated overlays are registered in `domain_extension_state.json`
2. All artifacts in the workspace comply with the merged overlay constraints
3. No artifact is missing required fields introduced by the overlay
4. All workflow patterns referenced by sub-packs are present in the pack
5. All persona archetypes referenced by sub-packs have corresponding entries in the workspace's `persona_archetype_pack`

Validation produces a report:
```
Domain Validation Report: healthcare (us)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Base overlay:          ✓ Valid
Regional overlay (us): ✓ Valid
Sub-packs:
  provider:            ✓ Valid
  payer:               ✓ Valid
  insurer:             ⚠ Missing persona archetype: "Insurance Underwriter"

Artifact compliance:
  workflow_orchestration_map.json: ✓ 12/12 required fields present
  component_prd.json:              ✓ 8/8 required fields present
  master_prd.json:                 ⚠ Missing "compliance_checkpoints" (required by us overlay)

Recommended action:
  Add "Insurance Underwriter" persona to persona_archetype_pack
  Add compliance_checkpoints to master_prd.json
```

---

## Implementation Roadmap

### V14.0 — Architecture Foundation
- Domain extension pack system designed and validated
- Schema overlay mechanism implemented
- `domain_extension_pack.schema.json` created
- `productos domain enable` and `productos domain validate` CLI commands functional
- No domain content shipped — architecture validated with synthetic test packs

### V14.1 — Healthcare Pack (US Region)
- `core/domains/healthcare/` base overlay: FHIR R4 core resources, clinical coding basics
- `core/domains/healthcare/regions/us.schema.overlay.json`: HIPAA, CMS, X12, CPT/ICD-10/HCPCS
- Sub-packs: provider, payer, insurer
- Workflow patterns: prior authorization, eligibility verification, claims submission

### V14.2 — Finance Pack (US + EU Regions)
- `core/domains/finance/` base overlay: risk terminology, audit patterns, common compliance
- `core/domains/finance/regions/us.schema.overlay.json`: SEC, FINRA, CFTC, OCC, Federal Reserve
- `core/domains/finance/regions/eu.schema.overlay.json`: MiFID II, EMIR, ECB, EBA
- Sub-packs: capital_markets, banking
- Workflow patterns: trade execution, post-trade processing, collateral management, account opening

### V14.3 — Healthcare Expansion (EU, UK, Canada)
- EU regional overlay: GDPR health provisions, MDR, IVDR
- UK regional overlay: NHS Digital, MHRA, FCA (health-fintech crossover)
- Canada regional overlay: PIPEDA, CIHI, provincial privacy
- Sub-packs: pharma, lifescience
- Workflow patterns: clinical trial enrollment, pharmacovigilance

### V14.4 — Finance Expansion (Payments Sub-Pack)
- Payments sub-pack: ACH, SEPA, RTP, FedNow, SWIFT gpi, crypto basics
- US regional overlay additions: CFPB regulations, Nacha rules
- EU regional overlay additions: PSD2, SEPA Instant

### V14.5 — Social Media Pack
- Base overlay: content taxonomy, engagement models, trust frameworks
- US regional overlay: CCPA, COPPA, Section 230
- EU regional overlay: GDPR, Digital Services Act, ePrivacy
- Sub-packs: content moderation, creator economy, growth loops

### V14.6 — SaaS/GenAI Pack
- Base overlay: multi-tenant patterns, AI governance frameworks, API marketplace
- US regional overlay: AI Executive Orders, state AI legislation
- EU regional overlay: AI Act, GDPR AI provisions
- Sub-packs: multi-tenant SaaS, AI feature governance, API marketplace

### V14.7+ — Retail, Media & Entertainment, Additional Regions

---

## Pack Development Guide

### For Contributors Adding New Domain Packs

1. **Create `core/domains/<pack>/` directory**
2. **Draft `base.schema.overlay.json`** — reference only international standards and universal concepts
3. **Draft at least one regional overlay** — validate it against base before submission
4. **Draft at least one workflow pattern** — validate it against base + regional
5. **Write `README.md`** — document what the pack covers, which regions and sub-packs are available, and how to activate
6. **Add tests** — `tests/test_domains_<pack>.py` validates overlay merge, activation, and artifact compliance
7. **Submit PR** — pack is reviewed for: schema correctness, no contradictions with core, documentation completeness

### For Contributors Adding New Regions to Existing Packs

1. **Study the base overlay** — understand what is universal
2. **Study existing regional overlays** — understand patterns and depth expectations
3. **Draft `<region>.schema.overlay.json`** — focus on regulators, compliance frameworks, and regional standards
4. **Validate against base** — run `productos domain validate --pack <pack> --region <region>` on test fixtures
5. **Add tests** — extend `tests/test_domains_<pack>.py` with region-specific fixtures
6. **Submit PR**

---

## Anti-Patterns

### Pack-Level Anti-Patterns

1. **Base overlay references a regional standard.** Base must be universal. If FHIR R4 is international, it belongs in base. If X12 is US-only, it belongs in `us` regional.
2. **Regional overlay contradicts base.** A regional overlay cannot make a base-required field optional. It cannot redefine a base enum.
3. **Pack embeds core schema changes.** Domain packs overlay core schemas. They never modify core schema files.
4. **Sub-pack defines new schemas.** Sub-packs are manifests, not schemas. New schema fields belong in base or regional overlays.
5. **Workflow pattern hardcodes a product name.** Patterns are templates, not product specifications. They must be customizable.

### Activation Anti-Patterns

1. **Activating a region without its base.** The CLI blocks this, but manual editing of `domain_extension_state.json` could create an invalid state.
2. **Activating conflicting regions without understanding overlap.** US HIPAA and EU GDPR have overlapping but distinct privacy requirements. The PM must understand both.
3. **Ignoring validation warnings.** A validation warning about a missing persona archetype means the orchestration map may have gaps.
4. **Using workflow patterns without customization.** Patterns are starting points, not final specifications. The PM must adapt them to their product.

---

## Reference

- Execution Plan: `internal/plans/version-history/v14-orchestration-superpowers-execution-plan.md`
- Bounded Claim: `core/docs/v14-bounded-claim.md`
- Orchestration Model: `core/docs/v14-orchestration-model.md`
- Core Schema Directory: `core/schemas/artifacts/`
- Test Fixtures: `tests/fixtures/workspaces/`
