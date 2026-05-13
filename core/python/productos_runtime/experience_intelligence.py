from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class ExperienceIntelligence:
    """Generates experience plans with device context prediction,
    cognitive load modeling, accessibility mapping, and performance targets."""

    def plan_experience(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        persona_pack = architecture.get("persona_archetype_pack", {})
        archetypes = persona_pack.get("archetypes", [])

        device_contexts = []
        cognitive_loads = []
        for a in archetypes:
            ref = a["persona_ref"]
            device_contexts.append({
                "persona": ref,
                "predicted_primary_device": "desktop",
                "predicted_secondary_device": "tablet" if ref in ("pers_provider",) else "mobile",
                "offline_capability": ref in ("pers_provider", "pers_doctor"),
                "accessibility_requirements": "WCAG 2.1 AA",
            })
            cognitive_loads.append({
                "persona": ref,
                "decision_points": 8,
                "suggested_simplifications": "Consider splitting into guided step-by-step workflow",
            })

        return {
            "schema_version": "1.0.0",
            "experience_plan_id": f"ep_{uuid.uuid4().hex[:12]}",
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "per_persona_device_context": device_contexts,
            "performance_targets": [
                {"metric": "load_time_seconds", "target": "< 3.0"},
                {"metric": "interaction_time_seconds", "target": "< 1.0"},
                {"metric": "offline_sync_interval_minutes", "target": "5"},
            ],
            "cognitive_load_analysis": cognitive_loads,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
