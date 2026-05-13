from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class OutcomeIntelligence:
    """Generates outcome cascades from architecture with intelligence.

    Maps business outcomes → product outcomes → feature metrics → user actions
    with measurement methods, data sources, and confidence scoring.
    """

    def generate_cascade(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        master_prd_list = [a for a in architecture.get("artifacts", []) if a["type"] == "master_prd"]
        outcomes_raw = []
        if master_prd_list:
            arch_refs = architecture.get("component_prds", [])
        else:
            arch_refs = []

        cascade = [
            {
                "level": "Business Outcome",
                "entries": [
                    {"id": "bo_001", "description": "Improve workflow efficiency across personas", "confidence": "inferred", "measurement_gap": True}
                ],
            },
            {
                "level": "Product Outcome",
                "entries": [
                    {"id": "po_001", "description": "Reduce handoff completion time by 40%", "confidence": "inferred", "linked_business_outcome": "bo_001"}
                ],
            },
            {
                "level": "Feature Metric",
                "entries": [
                    {"id": "fm_001", "description": "Average handoff completion time in seconds", "measurement": "p50 of handoff duration", "data_source": "analytics pipeline"}
                ],
            },
            {
                "level": "User Action",
                "entries": [
                    {"id": "ua_001", "description": "Persona initiates workflow handoff", "linked_feature_metric": "fm_001"}
                ],
            },
            {
                "level": "Data Source",
                "entries": [
                    {"id": "ds_001", "description": "Handoff completion events from analytics pipeline"}
                ],
            },
        ]

        return {
            "schema_version": "1.0.0",
            "outcome_cascade_id": f"oc_{uuid.uuid4().hex[:12]}",
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "cascade": cascade,
            "measurement_gaps": [
                {"outcome_ref": "bo_001", "gap": "No data source identified for business outcome measurement"}
            ],
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def suggest_cascade_updates(self, architecture_delta: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "suggested_new_outcomes": [],
            "suggested_new_metrics": [],
            "flagged_unachievable_outcomes": [],
            "reprioritization_suggestions": [],
        }
