from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple


class GapIntelligence:
    """Detects gaps across all architecture layers with narrative explanations.

    Per-gap output includes: severity, impact narrative, concrete suggestion,
    auto-fix availability, and confidence scoring.
    """

    def analyze(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze architecture for gaps across all layers.

        Args:
            architecture: ProductArchitecture container from ArchitectureSynthesis

        Returns:
            GapAnalysis with detected gaps, summary statistics, and suggestions.
        """
        gaps: List[Dict[str, Any]] = []
        analysis_id = f"ga_{uuid.uuid4().hex[:12]}"

        persona_pack = architecture.get("persona_archetype_pack", {})
        workflow_map = architecture.get("workflow_orchestration_map", {})
        component_prds = architecture.get("component_prds", [])
        journey_maps = architecture.get("customer_journey_maps", [])
        api_contracts = architecture.get("api_contract_hypotheses", [])
        cross_links = architecture.get("cross_links", [])
        artifacts = architecture.get("artifacts", [])

        persona_refs = {a["persona_ref"] for a in persona_pack.get("archetypes", [])}
        handoffs = workflow_map.get("handoffs", [])
        compliance_gates = workflow_map.get("compliance_gates", [])
        handoff_personas: Set[str] = set()
        for h in handoffs:
            handoff_personas.add(h["source_persona"])
            handoff_personas.add(h["target_persona"])

        # 1. Missing handoffs (orphan personas with no handoff role)
        gaps.extend(self._detect_missing_handoffs(persona_refs, handoff_personas, handoffs))

        # 2. Orphan personas (persona with no handoff role at all)
        gaps.extend(self._detect_orphan_personas(persona_refs, handoff_personas))

        # 3. SLA inconsistencies
        gaps.extend(self._detect_sla_inconsistencies(handoffs))

        # 4. Compliance gaps
        gaps.extend(self._detect_compliance_gaps(persona_refs, workflow_map, compliance_gates))

        # 5. Persona coverage gaps
        gaps.extend(self._detect_persona_coverage_gaps(persona_refs, journey_maps))

        # 6. API contract gaps
        gaps.extend(self._detect_api_contract_gaps(handoffs, api_contracts))

        # 7. Outcome measurement gaps
        master_prd = next((a for a in artifacts if a["type"] == "master_prd"), None)
        gaps.extend(self._detect_outcome_measurement_gaps(architecture, master_prd))

        # 8. Broken cross-layer links
        gaps.extend(self._detect_broken_links(artifacts, cross_links))

        # 9. Circular dependencies
        gaps.extend(self._detect_circular_dependencies(component_prds))

        # Compute summary
        critical_count = sum(1 for g in gaps if g["severity"] == "critical")
        warning_count = sum(1 for g in gaps if g["severity"] == "warning")
        info_count = sum(1 for g in gaps if g["severity"] == "info")
        auto_fixable_count = sum(1 for g in gaps if g.get("auto_fix_available"))

        return {
            "schema_version": "1.0.0",
            "gap_analysis_id": analysis_id,
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "gaps": gaps,
            "summary": {
                "total_gaps": len(gaps),
                "critical_count": critical_count,
                "warning_count": warning_count,
                "info_count": info_count,
                "auto_fixable_count": auto_fixable_count,
            },
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    # ------------------------------------------------------------------
    # Gap detectors
    # ------------------------------------------------------------------

    def _detect_missing_handoffs(
        self, persona_refs: Set[str], handoff_personas: Set[str], handoffs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect personas with no handoff role and suggest missing handoffs."""
        gaps: List[Dict[str, Any]] = []
        personas_with_no_role = persona_refs - handoff_personas

        for pid in personas_with_no_role:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "missing_handoff",
                "severity": "critical",
                "description": f"Persona '{pid}' has no handoffs in the orchestration map",
                "impact": f"Without handoffs, '{pid}' cannot interact with other personas. The workflow isolates this persona, making collaboration impossible. Any workflow objects that '{pid}' produces have no receiver.",
                "suggestion": "Add at least one handoff involving '{}' — either as source ('{}' initiates action) or target (another persona hands off to '{}')".format(pid, pid, pid),
                "auto_fix_available": False,
                "confidence": 0.85,
                "affected_artifact_uuids": [pid],
            })

        return gaps

    def _detect_orphan_personas(
        self, persona_refs: Set[str], handoff_personas: Set[str]
    ) -> List[Dict[str, Any]]:
        """Detect personas that exist in the pack but have no role in any handoff."""
        gaps: List[Dict[str, Any]] = []
        orphans = persona_refs - handoff_personas

        for pid in orphans:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "orphan_persona",
                "severity": "warning",
                "description": f"Persona '{pid}' exists in archetype pack but has no handoff role",
                "impact": f"'{pid}' is defined as a persona but never participates in any workflow handoff. This means either the persona is unnecessary or a handoff is missing. Resource allocation for '{pid}' has no workflow justification.",
                "suggestion": f"Either add workflow handoffs involving '{pid}' or remove '{pid}' from the persona pack if not needed",
                "auto_fix_available": False,
                "confidence": 0.8,
                "affected_artifact_uuids": [pid],
            })

        return gaps

    def _detect_sla_inconsistencies(self, handoffs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect SLA target inconsistencies across handoffs."""
        gaps: List[Dict[str, Any]] = []
        if len(handoffs) < 2:
            return gaps

        sla_values = [(h["handoff_id"], h.get("sla_target_seconds", 0)) for h in handoffs if h.get("sla_target_seconds")]
        if not sla_values:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "sla_inconsistency",
                "severity": "info",
                "description": "No SLA targets defined on any handoff",
                "impact": "Without SLA targets, there is no way to measure workflow performance or detect bottlenecks. Simulation cannot predict completion times.",
                "suggestion": "Add SLA targets (in seconds) to each handoff in the orchestration map based on expected processing time",
                "auto_fix_available": False,
                "confidence": 0.9,
                "affected_artifact_uuids": [],
            })
            return gaps

        sorted_slas = sorted(sla_values, key=lambda x: x[1])
        min_sla = sorted_slas[0][1]
        max_sla = sorted_slas[-1][1]

        if max_sla > min_sla * 10:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "sla_inconsistency",
                "severity": "warning",
                "description": f"SLA targets vary significantly: {min_sla}s to {max_sla}s (10x difference)",
                "impact": f"The handoff '{sorted_slas[-1][0]}' has an SLA of {max_sla}s while the fastest handoff is {min_sla}s. This 10x+ disparity may indicate unrealistic expectations or a bottleneck that needs parallel processing.",
                "suggestion": f"Review SLA targets on '{sorted_slas[-1][0]}' — consider splitting into parallel handoffs or adjusting target to {max_sla // 2}s",
                "auto_fix_available": False,
                "confidence": 0.6,
                "affected_artifact_uuids": [h[0] for h in sla_values],
            })

        return gaps

    def _detect_compliance_gaps(
        self, persona_refs: Set[str], workflow_map: Dict[str, Any], compliance_gates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect missing compliance gates for regulated workflows."""
        gaps: List[Dict[str, Any]] = []
        handoffs = workflow_map.get("handoffs", [])

        if not handoffs:
            return gaps

        has_phi_handoff = any(
            "phi" in h.get("shared_artifact", "").lower() or "patient" in h.get("shared_artifact", "").lower() or "auth" in h.get("shared_artifact", "").lower()
            for h in handoffs
        )

        if has_phi_handoff and not compliance_gates:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "compliance_gap",
                "severity": "critical",
                "description": "Workflow handles PHI-like data but no compliance gates defined",
                "impact": "Without compliance gates, PHI-handling handoffs have no audit log, consent verification, or data privacy checks. This creates regulatory risk under HIPAA, GDPR, or equivalent frameworks.",
                "suggestion": "Add compliance gates at each handoff that handles sensitive data: audit_log required, consent_record required, data_minimization check required",
                "auto_fix_available": True,
                "auto_fix_payload": {
                    "compliance_gates_to_add": [
                        {"name": "PHI compliance check", "required_evidence": ["audit_log", "consent_record", "data_minimization"]}
                    ]
                },
                "confidence": 0.85,
                "affected_artifact_uuids": [h["handoff_id"] for h in handoffs if has_phi_handoff],
            })

        return gaps

    def _detect_persona_coverage_gaps(
        self, persona_refs: Set[str], journey_maps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect personas not covered by journey maps or journey stages with no persona."""
        gaps: List[Dict[str, Any]] = []
        mapped_personas = {jm["persona_ref"] for jm in journey_maps}
        unmapped = persona_refs - mapped_personas

        for pid in unmapped:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "persona_coverage_gap",
                "severity": "warning",
                "description": f"Persona '{pid}' has no customer journey map",
                "impact": f"Without a journey map for '{pid}', their experience is undefined. You cannot identify pain points, moments of truth, or opportunities for this persona.",
                "suggestion": f"Generate a customer journey map for '{pid}' based on their handoff roles and workflow stages",
                "auto_fix_available": True,
                "auto_fix_payload": {"persona_ref": pid, "action": "generate_journey_map"},
                "confidence": 0.9,
                "affected_artifact_uuids": [pid],
            })

        return gaps

    def _detect_api_contract_gaps(
        self, handoffs: List[Dict[str, Any]], api_contracts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect shared artifacts with no API contract definition."""
        gaps: List[Dict[str, Any]] = []
        shared_artifacts = {h.get("shared_artifact", "") for h in handoffs if h.get("shared_artifact")}
        contracted = {a.get("resource", "") for a in api_contracts}
        missing = shared_artifacts - contracted

        for artifact in missing:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "api_contract_gap",
                "severity": "warning",
                "description": f"Shared artifact '{artifact}' has no API contract definition",
                "impact": f"'{artifact}' is passed between personas but has no defined API contract. This means data format, required fields, and operations are unspecified — leading to integration issues during implementation.",
                "suggestion": f"Add API contract for resource '{artifact}' with POST/GET operations and required data fields",
                "auto_fix_available": True,
                "auto_fix_payload": {"resource": artifact, "suggested_operations": ["POST", "GET"]},
                "confidence": 0.85,
                "affected_artifact_uuids": [],
            })

        return gaps

    def _detect_outcome_measurement_gaps(
        self, architecture: Dict[str, Any], master_prd: Dict[str, Any] | None
    ) -> List[Dict[str, Any]]:
        """Detect business outcomes with no feature metric."""
        gaps: List[Dict[str, Any]] = []
        if not master_prd:
            return gaps

        outcomes = master_prd.get("business_outcomes", [])
        for o in outcomes:
            measurement = o.get("measurement", "")
            if "TBD" in measurement or not measurement:
                gaps.append({
                    "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                    "gap_type": "outcome_measurement_gap",
                    "severity": "warning",
                    "description": f"Outcome '{o.get('outcome_id', '')}' has no concrete measurement",
                    "impact": f"Business outcome '{o.get('description', '')[:60]}...' has no defined measurement method. Without it, you cannot track progress toward the outcome or verify its achievement.",
                    "suggestion": f"Define a concrete measurement for outcome '{o.get('outcome_id', '')}': e.g., specific metric, data source, collection frequency, and target value",
                    "auto_fix_available": False,
                    "confidence": 0.8,
                    "affected_artifact_uuids": [o.get("outcome_id", "")],
                })

        return gaps

    def _detect_broken_links(
        self, artifacts: List[Dict[str, Any]], cross_links: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect broken cross-layer links referencing non-existent artifacts."""
        gaps: List[Dict[str, Any]] = []
        artifact_uuids = {a["uuid"] for a in artifacts}

        for link in cross_links:
            source = link.get("source_artifact_uuid", "")
            target = link.get("target_artifact_uuid", "")
            if source and source not in artifact_uuids:
                gaps.append({
                    "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                    "gap_type": "broken_cross_layer_link",
                    "severity": "critical",
                    "description": f"Cross-link references non-existent source artifact: {source}",
                    "impact": f"A cross-link claims artifact '{source}' exists, but no artifact with that UUID is found in the architecture bundle. This means the link points to nothing — traceability is broken.",
                    "suggestion": f"Either create artifact with UUID {source} or remove the cross-link that references it",
                    "auto_fix_available": False,
                    "confidence": 0.95,
                    "affected_artifact_uuids": [source, target],
                })
            if target and target not in artifact_uuids:
                gaps.append({
                    "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                    "gap_type": "broken_cross_layer_link",
                    "severity": "critical",
                    "description": f"Cross-link references non-existent target artifact: {target}",
                    "impact": f"A cross-link claims artifact '{target}' exists, but no artifact with that UUID is found. Traceability is broken from source to target.",
                    "suggestion": f"Either create artifact with UUID {target} or remove the cross-link that references it",
                    "auto_fix_available": False,
                    "confidence": 0.95,
                    "affected_artifact_uuids": [source, target],
                })

        return gaps

    def _detect_circular_dependencies(self, component_prds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect circular dependencies in component graph."""
        gaps: List[Dict[str, Any]] = []

        if len(component_prds) < 3:
            return gaps

        dep_graph: Dict[str, Set[str]] = {}
        for c in component_prds:
            cid = c.get("component_prd_id", "")
            deps = set(c.get("handoff_refs", []))
            dep_graph[cid] = deps

        def _find_cycle(graph: Dict[str, Set[str]]) -> List[str] | None:
            visited: Set[str] = set()
            recursion_stack: Set[str] = set()

            def dfs(node: str, path: List[str]) -> List[str] | None:
                visited.add(node)
                recursion_stack.add(node)
                path.append(node)

                for neighbor in graph.get(node, set()):
                    if neighbor not in visited:
                        result = dfs(neighbor, path)
                        if result:
                            return result
                    elif neighbor in recursion_stack:
                        cycle_start = path.index(neighbor)
                        return path[cycle_start:] + [neighbor]

                path.pop()
                recursion_stack.discard(node)
                return None

            for node in graph:
                if node not in visited:
                    result = dfs(node, [])
                    if result:
                        return result
            return None

        cycle = _find_cycle(dep_graph)
        if cycle:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "circular_dependency",
                "severity": "critical",
                "description": f"Circular dependency detected in component graph: {' → '.join(cycle)}",
                "impact": f"Components form a circular dependency cycle: {' → '.join(cycle)}. This means component A depends on B which depends on C which depends on A again. This prevents clean implementation sequencing and can cause infinite loops in the build pipeline.",
                "suggestion": f"Break the circular dependency by: (1) extracting shared functionality into a new common component, or (2) inverting one dependency direction, or (3) merging the cycle into a single component",
                "auto_fix_available": False,
                "confidence": 0.95,
                "affected_artifact_uuids": cycle,
            })

        return gaps

    def suggest_fixes(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return concrete, implementable suggestions for detected gaps."""
        suggestions = []
        for g in gaps:
            suggestion = {
                "gap_ref": g["gap_id"],
                "suggestion": g.get("suggestion", ""),
                "auto_fix_available": g.get("auto_fix_available", False),
                "auto_fix_payload": g.get("auto_fix_payload", {}),
                "effort_estimate": self._estimate_effort(g),
            }
            suggestions.append(suggestion)

        return {
            "suggestion_set_id": f"ss_{uuid.uuid4().hex[:12]}",
            "total_suggestions": len(suggestions),
            "auto_fix_count": sum(1 for s in suggestions if s["auto_fix_available"]),
            "suggestions": suggestions,
        }

    def _estimate_effort(self, gap: Dict[str, Any]) -> str:
        severity_map = {
            "critical": "L",
            "warning": "M",
            "info": "S",
        }
        return severity_map.get(gap.get("severity", "info"), "M")
