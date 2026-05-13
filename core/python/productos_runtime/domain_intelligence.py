from __future__ import annotations

from copy import deepcopy
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class DomainIntelligence:
    """Auto-activates domain intelligence based on intent decomposition.

    Applies domain-specific data models, compliance gates, SLA constraints,
    and audit trail requirements to the architecture. Validates compliance
    coverage per regulation and region.
    """

    DOMAIN_REGISTRY: Dict[str, Dict[str, Any]] = {
        "healthcare": {
            "label": "Healthcare",
            "base_refs": ["FHIR R4", "clinical_coding"],
            "regions": {
                "us": {
                    "regulations": ["HIPAA", "HITECH", "CMS"],
                    "compliance_requirements": [
                        "audit_log_at_phi_handoffs",
                        "consent_record_at_data_access",
                        "breach_notification_workflow",
                        "data_minimization",
                        "phi_encryption_at_rest",
                        "phi_encryption_in_transit",
                    ],
                    "sla_constraints": [
                        {"regulation": "CMS", "handoff_type": "prior_authorization", "sla_hours": 72},
                    ],
                },
                "eu": {
                    "regulations": ["GDPR"],
                    "compliance_requirements": [
                        "consent_record_at_data_access",
                        "data_minimization",
                        "right_to_be_forgotten",
                        "data_portability",
                    ],
                    "sla_constraints": [],
                },
            },
            "sub_packs": {
                "provider": {"refs": ["EMR integration", "clinical_documentation"]},
                "payer": {"refs": ["adjudication", "benefits", "authorization"]},
                "insurer": {"refs": ["policy_administration", "risk", "underwriting"]},
            },
        },
        "finance": {
            "label": "Finance",
            "base_refs": ["ISO 20022", "LEI", "risk_terminology"],
            "regions": {
                "us": {
                    "regulations": ["SEC", "FINRA", "CFTC", "OCC"],
                    "compliance_requirements": [
                        "audit_log_at_trade_execution",
                        "transaction_reporting",
                        "best_execution_records",
                    ],
                    "sla_constraints": [],
                },
                "eu": {
                    "regulations": ["MiFID II", "EMIR"],
                    "compliance_requirements": [
                        "transaction_reporting",
                        "trade_transparency",
                        "clearing_obligation",
                    ],
                    "sla_constraints": [],
                },
            },
            "sub_packs": {
                "capital_markets": {"refs": ["FIX protocol", "OMS", "derivatives", "clearing"]},
                "banking": {"refs": ["PCI-DSS", "SWIFT", "AML/KYC", "lending"]},
            },
        },
    }

    def __init__(self):
        pass

    def auto_activate(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest domain pack activation based on intent decomposition.

        Args:
            decomposition: IntentDecomposition from IntentEngine

        Returns:
            DomainActivation with suggested packs, regions, sub-packs
        """
        domain_match = decomposition.get("domain_match", {})
        domain = domain_match.get("domain", "general")
        confidence = domain_match.get("confidence", 0.0)
        decomposition_id = decomposition.get("intent_decomposition_id", "")

        if domain == "general" or confidence < 0.3:
            return {
                "schema_version": "1.0.0",
                "domain_activation_id": f"da_{uuid.uuid4().hex[:12]}",
                "decomposition_ref": decomposition_id,
                "domain": "general",
                "sub_domains": [],
                "regions": [],
                "sub_packs": [],
                "confidence": confidence,
                "compatibility_notes": ["No domain detected — request PM clarification"],
                "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            }

        activation_id = f"da_{uuid.uuid4().hex[:12]}"
        domain_info = self.DOMAIN_REGISTRY.get(domain, {})
        regions = domain_match.get("regions", [])
        sub_domains = domain_match.get("sub_domains", [])

        sub_packs = []
        intent_text = decomposition.get("raw_text", "").lower()
        persona_labels = [
            persona.get("label", "").lower()
            for persona in decomposition.get("inferred_personas", [])
        ]
        for sp_name, sp_info in domain_info.get("sub_packs", {}).items():
            sp_terms = {sp_name.replace("_", " "), sp_name}
            if any(ref.lower() in intent_text for ref in sp_info.get("refs", [])) or any(
                term in intent_text or any(term in label for label in persona_labels)
                for term in sp_terms
            ):
                sub_packs.append(sp_name)

        compatibility_notes = []
        if len(regions) > 1:
            compatibility_notes.append(f"Cross-region activation: {', '.join(regions)} — verify compatibility")

        return {
            "schema_version": "1.0.0",
            "domain_activation_id": activation_id,
            "decomposition_ref": decomposition_id,
            "domain": domain,
            "sub_domains": sub_domains,
            "regions": regions,
            "sub_packs": sub_packs,
            "confidence": confidence,
            "compatibility_notes": compatibility_notes,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def enrich_architecture(
        self, architecture: Dict[str, Any], domain_activation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply domain intelligence to enrich architecture artifacts.

        Args:
            architecture: ProductArchitecture container
            domain_activation: DomainActivation from auto_activate()

        Returns:
            EnrichedArchitecture with additions report
        """
        domain = domain_activation.get("domain", "")
        regions = domain_activation.get("regions", [])
        domain_info = self.DOMAIN_REGISTRY.get(domain, {})

        additions: List[Dict[str, Any]] = []
        enriched_architecture = deepcopy(architecture)
        workflow_map = enriched_architecture.setdefault("workflow_orchestration_map", {})
        handoffs = workflow_map.get("handoffs", [])
        compliance_gates = workflow_map.setdefault("compliance_gates", [])
        component_prds = enriched_architecture.setdefault("component_prds", [])

        # Add compliance gates from regional overlay
        for region in regions:
            region_info = domain_info.get("regions", {}).get(region, {})
            for req in region_info.get("compliance_requirements", []):
                existing = any(req.replace("_", " ") in g.get("name", "").lower() for g in compliance_gates)
                if not existing:
                    gate = {
                        "gate_id": f"gate_{len(compliance_gates) + 1:03d}",
                        "name": req.replace("_", " "),
                        "description": f"{req.replace('_', ' ')} required for {region}",
                        "trigger_handoff_ids": [
                            handoff.get("handoff_id", "")
                            for handoff in handoffs
                            if handoff.get("handoff_id")
                        ],
                        "required_evidence": [req.replace("_", " ")],
                    }
                    compliance_gates.append(gate)
                    additions.append({
                        "addition_type": "compliance_gate",
                        "target_location": f"workflow_orchestration_map.{region}",
                        "description": f"Added compliance requirement: {req.replace('_', ' ')}",
                        "rationale": f"Required by {', '.join(region_info.get('regulations', []))} for region {region}",
                        "confidence": 0.85,
                    })

        # Add SLA constraints from regional overlay
        for region in regions:
            region_info = domain_info.get("regions", {}).get(region, {})
            for sla in region_info.get("sla_constraints", []):
                sla_desc = f"{sla['regulation']} {sla['sla_hours']}h SLA for {sla['handoff_type']}"
                existing = any(sla_desc in g.get("description", "") for g in compliance_gates)
                if not existing:
                    compliance_gates.append({
                        "gate_id": f"gate_{len(compliance_gates) + 1:03d}",
                        "name": f"{sla['regulation']} SLA constraint",
                        "description": sla_desc,
                        "trigger_handoff_ids": [
                            handoff.get("handoff_id", "")
                            for handoff in handoffs
                            if sla["handoff_type"].replace("_", " ")
                            in handoff.get("shared_artifact", "").replace("_", " ")
                        ]
                        or [handoff.get("handoff_id", "") for handoff in handoffs if handoff.get("handoff_id")][:1],
                        "required_evidence": [sla["regulation"]],
                    })
                    additions.append({
                        "addition_type": "sla_constraint",
                        "target_location": f"workflow_orchestration_map.compliance_gates",
                        "description": sla_desc,
                        "rationale": f"Regulatory requirement from {sla['regulation']}",
                        "confidence": 0.9,
                    })

        # Add data model refs from base domain
        for ref in domain_info.get("base_refs", []):
            for component in component_prds:
                refs = component.setdefault("domain_references", [])
                if ref not in refs:
                    refs.append(ref)
            additions.append({
                "addition_type": "data_model_ref",
                "target_location": "architecture.component_prds",
                "description": f"Suggested data model reference: {ref}",
                "rationale": f"Base domain reference for {domain}",
                "confidence": 0.75,
            })

        # Add sub-pack domain fields
        for sp in domain_activation.get("sub_packs", []):
            sp_info = domain_info.get("sub_packs", {}).get(sp, {})
            for ref in sp_info.get("refs", []):
                for component in component_prds:
                    fields = component.setdefault("domain_fields", [])
                    if ref not in fields:
                        fields.append(ref)
                additions.append({
                    "addition_type": "domain_field",
                    "target_location": f"architecture.component_prds.{sp}",
                    "description": f"Added domain field: {ref}",
                    "rationale": f"Sub-pack {sp} domain reference",
                    "confidence": 0.7,
                })

        # Compute summary
        compliance_gates_added = sum(1 for a in additions if a["addition_type"] == "compliance_gate")
        data_model_refs_added = sum(1 for a in additions if a["addition_type"] == "data_model_ref")
        sla_constraints_added = sum(1 for a in additions if a["addition_type"] == "sla_constraint")
        audit_trail_requirements_added = sum(1 for a in additions if a["addition_type"] == "audit_trail_requirement")

        return {
            "schema_version": "1.0.0",
            "enrichment_report_id": f"er_{uuid.uuid4().hex[:12]}",
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "domain_activation_ref": domain_activation.get("domain_activation_id", ""),
            "additions": additions,
            "enriched_architecture": enriched_architecture,
            "summary": {
                "total_additions": len(additions),
                "compliance_gates_added": compliance_gates_added,
                "data_model_refs_added": data_model_refs_added,
                "sla_constraints_added": sla_constraints_added,
                "audit_trail_requirements_added": audit_trail_requirements_added,
            },
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def validate_compliance_coverage(
        self, architecture: Dict[str, Any], domain_activation: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Validate compliance coverage per domain and region.

        Args:
            architecture: ProductArchitecture container
            domain_activation: Optional DomainActivation (auto-detected if not provided)

        Returns:
            ComplianceReport with per-regulation coverage, gaps, and score
        """
        if domain_activation is None:
            decomposition = architecture.get("decomposition_ref", "")
            domain_activation = {"domain": "general", "regions": [], "confidence": 0.0}

        domain = domain_activation.get("domain", "general")
        regions = domain_activation.get("regions", ["us"])
        domain_info = self.DOMAIN_REGISTRY.get(domain, {})
        workflow_map = architecture.get("workflow_orchestration_map", {})
        compliance_gates = workflow_map.get("compliance_gates", [])

        report_id = f"cr_{uuid.uuid4().hex[:12]}"
        regulations_list: List[Dict[str, Any]] = []
        critical_gaps: List[Dict[str, Any]] = []

        gate_names_lower = [g.get("name", "").lower() for g in compliance_gates]
        gate_desc_lower = [g.get("description", "").lower() for g in compliance_gates]

        for region in regions:
            region_info = domain_info.get("regions", {}).get(region, {})
            for regulation in region_info.get("regulations", []):
                reg_lower = regulation.lower()
                requirements = region_info.get("compliance_requirements", [])
                relevant_reqs = [r for r in requirements if reg_lower in r or any(term in r for term in [reg_lower])]
                if not relevant_reqs:
                    relevant_reqs = requirements

                gates_present = 0
                gates_required = len(relevant_reqs) if relevant_reqs else 1

                for req in relevant_reqs:
                    req_terms = req.replace("_", " ")
                    if any(req_terms in g for g in gate_names_lower) or any(req_terms in g for g in gate_desc_lower):
                        gates_present += 1

                coverage_score = gates_present / max(gates_required, 1)
                if coverage_score >= 1.0:
                    status = "compliant"
                elif coverage_score >= 0.5:
                    status = "partial"
                elif gates_required == 0:
                    status = "not_applicable"
                else:
                    status = "non_compliant"

                regulations_list.append({
                    "regulation": regulation,
                    "coverage_score": round(coverage_score, 2),
                    "gates_present": gates_present,
                    "gates_required": gates_required,
                    "status": status,
                    "notes": f"Compliance coverage for {regulation} in {region}",
                })

                if status in ("non_compliant", "partial"):
                    for req in relevant_reqs:
                        req_terms = req.replace("_", " ")
                        if not any(req_terms in g for g in gate_names_lower):
                            critical_gaps.append({
                                "regulation": regulation,
                                "description": f"Missing compliance gate: {req_terms}",
                                "required_action": f"Add compliance gate '{req.replace('_', ' ')}' to workflow orchestration map for {region}",
                                "severity": "high" if status == "non_compliant" else "medium",
                            })

        overall_score = 0.0
        if regulations_list:
            overall_score = sum(r["coverage_score"] for r in regulations_list) / len(regulations_list)

        return {
            "schema_version": "1.0.0",
            "compliance_report_id": report_id,
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "regulations": regulations_list,
            "overall_coverage_score": round(overall_score, 2),
            "critical_gaps": critical_gaps,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
