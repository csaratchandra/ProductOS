from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class AIArchitecture:
    """Plans AI layer for product architecture.

    Analyzes workflows and suggests automation candidates, human-in-the-loop
    checkpoints, trust framework, consent flows, data privacy guards, and
    regulatory alignment.
    """

    def plan_ai_layer(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        workflow_map = architecture.get("workflow_orchestration_map", {})
        handoffs = workflow_map.get("handoffs", [])

        automation_candidates = []
        for h in handoffs:
            automation_candidates.append({
                "workflow_stage": h["handoff_id"],
                "current_burden": "Manual review and routing",
                "automation_approach": "AI-assisted document classification and routing",
                "estimated_roi": "60% reduction in processing time",
                "risk_level": "medium",
                "confidence": 0.75,
            })

        return {
            "schema_version": "1.0.0",
            "ai_layer_plan_id": f"ai_{uuid.uuid4().hex[:12]}",
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "automation_candidates": automation_candidates,
            "human_in_the_loop_checkpoints": [
                {"stage": "compliance_gate", "approval_required": True, "escalation_rules": "Auto-escalate to senior reviewer after 24h"}
            ],
            "per_persona_ai_features": [
                {"persona": h.get("source_persona", ""), "ai_feature": "Smart routing", "trigger": "Handoff initiated", "explanation_requirement": "Show routing rationale"}
                for h in handoffs[:2]
            ],
            "failure_modes": [
                {"what_can_go_wrong": "AI misclassifies document", "detection_method": "Confidence score < 0.6", "rollback_procedure": "Route to manual review", "fallback_experience": "Human reviewer prompt"}
            ],
            "regulatory_alignment": [
                {"regulation": "EU AI Act", "compliance_status": "partial", "required_actions": ["Implement human oversight for high-risk automation"]}
            ],
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
