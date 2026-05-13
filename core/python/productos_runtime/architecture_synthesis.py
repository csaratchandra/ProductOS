from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .intent_engine import IntentEngine


class ArchitectureSynthesis:
    """Generates all architecture artifacts in parallel from a master PRD.

    Produces 6 artifact groups cross-linked by UUID references and validates
    cross-layer consistency.
    """

    def __init__(self, provider: Any = None):
        self._provider = provider
        self._intent_engine = IntentEngine(provider)

    def synthesize(
        self, master_prd: Dict[str, Any], mode: str = "standard"
    ) -> Dict[str, Any]:
        """Generate all 6 artifact groups from a master PRD.

        Args:
            master_prd: Master PRD from IntentEngine.generate_master_prd()
            mode: Generation mode (standard, quick, full)

        Returns:
            Unified ProductArchitecture container.
        """
        start_ms = int(time.time() * 1000)
        arch_id = f"arch_{uuid.uuid4().hex[:12]}"

        persona_pack = self._build_persona_archetype_pack(master_prd)
        workflow_map = self._build_workflow_orchestration_map(master_prd, persona_pack)

        with ThreadPoolExecutor(max_workers=3) as executor:
            component_future = executor.submit(
                self._build_component_prd_stubs, master_prd, workflow_map
            )
            journey_future = executor.submit(
                self._build_customer_journey_maps,
                master_prd,
                persona_pack,
                workflow_map,
            )
            api_future = executor.submit(
                self._build_api_contract_hypotheses, master_prd, workflow_map
            )

            component_prds = component_future.result()
            journey_maps = journey_future.result()
            api_contracts = api_future.result()

        zoom_map = self._build_zoom_navigation_map(master_prd, persona_pack, component_prds)

        artifacts = [
            self._make_artifact_ref("master_prd", master_prd),
            self._make_artifact_ref("persona_archetype_pack", persona_pack),
            self._make_artifact_ref("workflow_orchestration_map", workflow_map),
            *[self._make_artifact_ref("component_prd", c) for c in component_prds],
            *[self._make_artifact_ref("customer_journey_map", j) for j in journey_maps],
            *[self._make_artifact_ref("api_contract_hypothesis", a) for a in api_contracts],
            self._make_artifact_ref("zoom_navigation_map", zoom_map),
        ]

        cross_links = self._build_cross_links(
            master_prd, persona_pack, workflow_map, component_prds, journey_maps, api_contracts, zoom_map
        )

        duration_ms = int(time.time() * 1000) - start_ms

        return {
            "schema_version": "1.0.0",
            "product_architecture_id": arch_id,
            "workspace_id": master_prd.get("workspace_id", ""),
            "decomposition_ref": master_prd.get("generated_from_intent", ""),
            "source_master_prd": master_prd,
            "artifacts": artifacts,
            "cross_links": cross_links,
            "persona_archetype_pack": persona_pack,
            "workflow_orchestration_map": workflow_map,
            "component_prds": component_prds,
            "customer_journey_maps": journey_maps,
            "api_contract_hypotheses": api_contracts,
            "zoom_navigation_map": zoom_map,
            "generation_metadata": {
                "mode": mode,
                "duration_ms": duration_ms,
                "decomposition_uuid": master_prd.get("generated_from_intent", ""),
            },
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    # ------------------------------------------------------------------
    # Artifact builders
    # ------------------------------------------------------------------

    def _build_persona_archetype_pack(self, master_prd: Dict[str, Any]) -> Dict[str, Any]:
        """Build persona archetype pack from master PRD persona coverage map."""
        coverage = master_prd.get("persona_coverage_map", [])
        archetypes = []
        for i, pc in enumerate(coverage):
            archetypes.append({
                "archetype_id": f"arch_{i + 1:03d}",
                "persona_ref": pc["persona_ref"],
                "label": pc.get("label", f"Persona {i + 1}"),
                "archetype_type": pc.get("archetype", "user"),
                "coverage_status": pc.get("coverage_status", "primary"),
                "role_summary": f"Primary role for {pc.get('label', 'persona')}",
                "goals": [f"Complete workflow tasks for {pc.get('label', 'persona')}"],
                "pains": ["Manual process overhead", "Tool fragmentation"],
                "triggers": ["Workflow initiation event"],
                "blockers": ["Missing information from upstream persona"],
                "handoff_preferences": ["async", "sync"],
                "priority_score": 80 if pc.get("coverage_status") == "primary" else 50,
                "priority_rationale": f"Derived from intent decomposition confidence",
            })
        return {
            "persona_archetype_pack_id": f"pap_{uuid.uuid4().hex[:12]}",
            "archetypes": archetypes,
            "generated_from": master_prd.get("master_prd_id", ""),
        }

    def _build_workflow_orchestration_map(
        self, master_prd: Dict[str, Any], persona_pack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build workflow orchestration map from persona pack and PRD."""
        archetypes = persona_pack.get("archetypes", [])
        personas = [a["persona_ref"] for a in archetypes]

        handoffs = []
        for i in range(len(personas) - 1):
            handoffs.append({
                "handoff_id": f"ho_{i + 1:03d}",
                "source_persona": personas[i],
                "target_persona": personas[i + 1],
                "shared_artifact": f"workflow_object_{i + 1}",
                "trigger_event": f"{personas[i]} completes action",
                "sla_target_seconds": 3600,
                "escalation_path": f"escalate_{personas[i + 1]}",
            })

        if len(personas) >= 2:
            handoffs.append({
                "handoff_id": f"ho_{len(personas):03d}",
                "source_persona": personas[-1],
                "target_persona": personas[0],
                "shared_artifact": "completion_record",
                "trigger_event": f"{personas[-1]} completes final action",
                "sla_target_seconds": 7200,
                "escalation_path": f"escalate_{personas[0]}",
            })

        compliance_gates = []
        constraints = master_prd.get("scope_boundaries", [])
        for c in constraints:
            if "compliance" in c.lower() or "regulatory" in c.lower() or "hipaa" in c.lower() or "pci" in c.lower():
                compliance_gates.append({
                    "gate_id": f"gate_{len(compliance_gates) + 1:03d}",
                    "name": f"Compliance check: {c[:50]}",
                    "description": c,
                    "trigger_handoff_ids": [h["handoff_id"] for h in handoffs[:1]] if handoffs else [],
                    "required_evidence": ["audit_log", "consent_record"],
                })

        return {
            "workflow_orchestration_map_id": f"wom_{uuid.uuid4().hex[:12]}",
            "personas": personas,
            "handoffs": handoffs,
            "compliance_gates": compliance_gates,
            "generated_from": master_prd.get("master_prd_id", ""),
        }

    def _build_component_prd_stubs(
        self, master_prd: Dict[str, Any], workflow_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build component PRD stubs from workflow handoff boundaries."""
        handoffs = workflow_map.get("handoffs", [])
        components = []

        seen_boundaries = set()
        for i, h in enumerate(handoffs):
            boundary = f"{h['source_persona']}_to_{h['target_persona']}"
            if boundary not in seen_boundaries:
                seen_boundaries.add(boundary)
                components.append({
                    "component_prd_id": f"cprd_{uuid.uuid4().hex[:12]}",
                    "component_name": f"Component: {h['source_persona']} → {h['target_persona']}",
                    "summary": f"Handles handoff from {h['source_persona']} to {h['target_persona']} via {h['shared_artifact']}",
                    "assigned_personas": [h["source_persona"], h["target_persona"]],
                    "handoff_refs": [h["handoff_id"]],
                    "api_endpoints": self._infer_api_endpoints(h),
                    "linked_outcomes": master_prd.get("business_outcomes", [])[:1],
                    "generated_from": master_prd.get("master_prd_id", ""),
                })

        if not components:
            components.append({
                "component_prd_id": f"cprd_{uuid.uuid4().hex[:12]}",
                "component_name": "Core Application",
                "summary": "Primary application component",
                "assigned_personas": workflow_map.get("personas", []),
                "handoff_refs": [],
                "api_endpoints": [],
                "linked_outcomes": master_prd.get("business_outcomes", []),
                "generated_from": master_prd.get("master_prd_id", ""),
            })

        return components

    def _infer_api_endpoints(self, handoff: Dict[str, Any]) -> List[Dict[str, str]]:
        return [{
            "method": "POST",
            "path": f"/api/v1/handoffs/{handoff['handoff_id']}",
            "description": f"Submit {handoff['shared_artifact']} from {handoff['source_persona']} to {handoff['target_persona']}",
        }]

    def _build_customer_journey_maps(
        self, master_prd: Dict[str, Any], persona_pack: Dict[str, Any], workflow_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build customer journey maps per persona from archetype + workflow."""
        archetypes = persona_pack.get("archetypes", [])
        handoffs = workflow_map.get("handoffs", [])
        maps = []

        for a in archetypes:
            persona_handoffs = [h for h in handoffs if h["source_persona"] == a["persona_ref"] or h["target_persona"] == a["persona_ref"]]
            stages = []
            for j, h in enumerate(persona_handoffs):
                stages.append({
                    "stage_id": f"stage_{a['persona_ref']}_{j + 1:03d}",
                    "stage_name": f"Handoff {j + 1}: {h['source_persona']} → {h['target_persona']}",
                    "description": f"Persona {a['persona_ref']} participates in handoff for {h['shared_artifact']}",
                    "linked_handoff_id": h["handoff_id"],
                    "actions": [f"Receive {h['shared_artifact']}", f"Process and forward"],
                    "emotion_score": 7,
                })
            maps.append({
                "journey_map_id": f"cjm_{a['persona_ref']}_{uuid.uuid4().hex[:8]}",
                "persona_ref": a["persona_ref"],
                "persona_label": a.get("label", a["persona_ref"]),
                "stages": stages,
                "generated_from": master_prd.get("master_prd_id", ""),
            })

        return maps

    def _build_api_contract_hypotheses(
        self, master_prd: Dict[str, Any], workflow_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build API contract hypotheses from shared artifacts in orchestration map."""
        handoffs = workflow_map.get("handoffs", [])
        contracts = []

        for h in handoffs:
            contracts.append({
                "contract_id": f"api_{h['handoff_id']}",
                "handoff_ref": h["handoff_id"],
                "resource": h["shared_artifact"],
                "operations": [
                    {"method": "POST", "path": f"/api/v1/{h['shared_artifact']}", "description": f"Create {h['shared_artifact']}"},
                    {"method": "GET", "path": f"/api/v1/{h['shared_artifact']}/{{id}}", "description": f"Read {h['shared_artifact']}"},
                ],
                "data_contract": {
                    "required_fields": ["id", "status", "created_at"],
                    "optional_fields": ["notes", "attachments"],
                },
                "generated_from": master_prd.get("master_prd_id", ""),
            })

        return contracts

    def _build_zoom_navigation_map(
        self, master_prd: Dict[str, Any], persona_pack: Dict[str, Any],
        component_prds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build zoom navigation hierarchy from component hierarchy."""
        levels = [
            {
                "level": 1,
                "label": "Product",
                "entries": [{"id": master_prd.get("master_prd_id", ""), "title": master_prd.get("title", "Product")}],
            },
            {
                "level": 2,
                "label": "Persona",
                "entries": [{"id": a["persona_ref"], "title": a.get("label", a["persona_ref"])} for a in persona_pack.get("archetypes", [])],
            },
            {
                "level": 3,
                "label": "Component",
                "entries": [{"id": c.get("component_prd_id", ""), "title": c.get("component_name", "")} for c in component_prds],
            },
        ]
        return {
            "zoom_navigation_map_id": f"znm_{uuid.uuid4().hex[:12]}",
            "levels": levels,
            "generated_from": master_prd.get("master_prd_id", ""),
        }

    # ------------------------------------------------------------------
    # Cross-linking
    # ------------------------------------------------------------------

    def _build_cross_links(
        self, master_prd: Dict[str, Any],
        persona_pack: Dict[str, Any],
        workflow_map: Dict[str, Any],
        component_prds: List[Dict[str, Any]],
        journey_maps: List[Dict[str, Any]],
        api_contracts: List[Dict[str, Any]],
        zoom_map: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Build cross-layer UUID links between all artifacts."""
        links: List[Dict[str, Any]] = []

        mprd_id = master_prd.get("master_prd_id", "")
        pap_id = persona_pack.get("persona_archetype_pack_id", "")
        wom_id = workflow_map.get("workflow_orchestration_map_id", "")
        znm_id = zoom_map.get("zoom_navigation_map_id", "")

        if mprd_id:
            links.append({"source_artifact_uuid": mprd_id, "target_artifact_uuid": pap_id, "link_type": "references", "confidence": 0.9})
            links.append({"source_artifact_uuid": mprd_id, "target_artifact_uuid": wom_id, "link_type": "references", "confidence": 0.85})

        for c in component_prds:
            cid = c.get("component_prd_id", "")
            links.append({"source_artifact_uuid": pap_id, "target_artifact_uuid": cid, "link_type": "implements", "confidence": 0.75})
            links.append({"source_artifact_uuid": wom_id, "target_artifact_uuid": cid, "link_type": "depends_on", "confidence": 0.7})

        for jm in journey_maps:
            jid = jm.get("journey_map_id", "")
            links.append({"source_artifact_uuid": pap_id, "target_artifact_uuid": jid, "link_type": "references", "confidence": 0.8})
            links.append({"source_artifact_uuid": jid, "target_artifact_uuid": wom_id, "link_type": "validates", "confidence": 0.75})

        for ac in api_contracts:
            acid = ac.get("contract_id", "")
            links.append({"source_artifact_uuid": acid, "target_artifact_uuid": wom_id, "link_type": "implements", "confidence": 0.8})

        links.append({"source_artifact_uuid": znm_id, "target_artifact_uuid": pap_id, "link_type": "references", "confidence": 0.9})
        links.append({"source_artifact_uuid": znm_id, "target_artifact_uuid": wom_id, "link_type": "references", "confidence": 0.85})

        return links

    def _make_artifact_ref(self, artifact_type: str, artifact: Dict[str, Any]) -> Dict[str, Any]:
        alt_ids = [
            f"{artifact_type}_id",
            "persona_archetype_pack_id",
            "workflow_orchestration_map_id",
            "zoom_navigation_map_id",
            "journey_map_id",
            "contract_id",
            "component_prd_id",
        ]
        uid = f"art_{uuid.uuid4().hex[:12]}"
        for aid in alt_ids:
            if aid in artifact and artifact[aid]:
                uid = artifact[aid]
                break
        return {
            "uuid": uid,
            "type": artifact_type,
            "version": "1.0.0",
            "generation_timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "confidence_metadata": {
                "overall_confidence": 0.8,
                "method": "deterministic",
            },
        }

    # ------------------------------------------------------------------
    # Cross-consistency validation
    # ------------------------------------------------------------------

    def validate_cross_consistency(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-layer validation checks across all artifacts."""
        report_id = f"cr_{uuid.uuid4().hex[:12]}"
        checks_passed: List[str] = []
        checks_failed: List[Dict[str, Any]] = []
        warnings: List[str] = []
        auto_fixes: List[Dict[str, Any]] = []
        requires_review: List[str] = []

        persona_pack = architecture.get("persona_archetype_pack", {})
        workflow_map = architecture.get("workflow_orchestration_map", {})
        component_prds = architecture.get("component_prds", [])
        journey_maps = architecture.get("customer_journey_maps", [])
        api_contracts = architecture.get("api_contract_hypotheses", [])

        persona_refs = set(a["persona_ref"] for a in persona_pack.get("archetypes", []))
        handoff_personas = set()
        for h in workflow_map.get("handoffs", []):
            handoff_personas.add(h["source_persona"])
            handoff_personas.add(h["target_persona"])

        # Check 1: Every persona appears in orchestration map
        missing_from_orch = persona_refs - handoff_personas
        if missing_from_orch:
            checks_failed.append({
                "check_name": "persona_in_orchestration",
                "severity": "warning",
                "description": f"Personas missing from orchestration map: {missing_from_orch}",
            })
        else:
            checks_passed.append("All personas appear in orchestration map")

        # Check 2: Every handoff has source/target in persona pack
        unknown_personas = handoff_personas - persona_refs
        if unknown_personas:
            checks_failed.append({
                "check_name": "handoff_persona_exists",
                "severity": "critical",
                "description": f"Handoffs reference unknown personas: {unknown_personas}",
            })
        else:
            checks_passed.append("All handoff personas exist in archetype pack")

        # Check 3: Every component PRD has assigned personas from archetype pack
        for c in component_prds:
            assigned = set(c.get("assigned_personas", []))
            unknown = assigned - persona_refs
            if unknown:
                checks_failed.append({
                    "check_name": "component_persona_exists",
                    "severity": "warning",
                    "description": f"Component '{c.get('component_name', '')}' references unknown personas: {unknown}",
                })
        if not any(f["check_name"] == "component_persona_exists" for f in checks_failed):
            checks_passed.append("All component PRDs reference valid personas")

        # Check 4: Every journey map links to orchestration map stages
        for jm in journey_maps:
            stages = jm.get("stages", [])
            for s in stages:
                if not s.get("linked_handoff_id"):
                    warnings.append(f"Journey stage '{s.get('stage_name', '')}' has no linked handoff")
        if not warnings:
            checks_passed.append("All journey stages link to orchestration map")

        # Check 5: Shared artifacts have API contract fields
        handoff_artifacts = {h["shared_artifact"] for h in workflow_map.get("handoffs", []) if h.get("shared_artifact")}
        contracted_artifacts = {a.get("resource", "") for a in api_contracts}
        missing_contracts = handoff_artifacts - contracted_artifacts
        if missing_contracts:
            checks_failed.append({
                "check_name": "shared_artifact_contract",
                "severity": "warning",
                "description": f"Shared artifacts without API contracts: {missing_contracts}",
            })
        else:
            checks_passed.append("All shared artifacts have API contracts")

        # Check 6: Orphan artifacts
        all_uuids = set()
        for art in architecture.get("artifacts", []):
            all_uuids.add(art["uuid"])
        linked_uuids = set()
        for link in architecture.get("cross_links", []):
            linked_uuids.add(link["source_artifact_uuid"])
            linked_uuids.add(link["target_artifact_uuid"])
        orphans = all_uuids - linked_uuids
        if orphans:
            checks_failed.append({
                "check_name": "orphan_artifacts",
                "severity": "warning",
                "description": f"Orphan artifacts found (no links): {sorted(orphans)}",
            })
        else:
            checks_passed.append("No orphan artifacts")

        overall = "passed"
        if checks_failed:
            criticals = [f for f in checks_failed if f["severity"] == "critical"]
            if criticals:
                overall = "failed"
            else:
                overall = "warning"

        return {
            "schema_version": "1.0.0",
            "consistency_report_id": report_id,
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "warnings": warnings,
            "auto_fixes_applied": auto_fixes,
            "requires_pm_review": requires_review,
            "overall_status": overall,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
