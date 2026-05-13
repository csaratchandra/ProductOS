from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class PredictiveAnalytics:
    """Auto-generates analytics instrumentation plans from architecture.

    Infers event taxonomy, metrics, funnel predictions, A/B test candidates,
    privacy risk assessments, and dashboard layouts.
    """

    def auto_plan(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        workflow_map = architecture.get("workflow_orchestration_map", {})
        handoffs = workflow_map.get("handoffs", [])
        personas = workflow_map.get("personas", [])
        journey_maps = architecture.get("customer_journey_maps", [])

        events = self._infer_events(handoffs, personas)
        metrics = self._infer_metrics(handoffs)
        dropoffs = self._predict_dropoffs(journey_maps)
        ab_tests = self._suggest_ab_tests(handoffs)
        privacy = self._assess_privacy(events)
        dashboards = self._suggest_dashboards(personas)

        return {
            "schema_version": "1.0.0",
            "analytics_plan_id": f"ap_{uuid.uuid4().hex[:12]}",
            "architecture_ref": architecture.get("product_architecture_id", ""),
            "event_taxonomy": events,
            "metric_definitions": metrics,
            "predicted_funnel_dropoffs": dropoffs,
            "ab_test_candidates": ab_tests,
            "privacy_risk_assessment": privacy,
            "dashboard_specs": dashboards,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def _infer_events(self, handoffs: List[Dict], personas: List[str]) -> List[Dict]:
        events = []
        for h in handoffs:
            hid = h["handoff_id"]
            events.append({
                "event_name": f"handoff_{hid}_initiated",
                "trigger": f"{h.get('source_persona', '?')} initiates {h.get('shared_artifact', 'workflow')}",
                "persona_ref": h.get("source_persona", ""),
                "properties": ["handoff_id", "source_persona", "target_persona", "timestamp", "artifact_type"],
                "privacy_classification": "behavioral",
            })
            events.append({
                "event_name": f"handoff_{hid}_completed",
                "trigger": f"{h.get('target_persona', '?')} receives {h.get('shared_artifact', 'workflow')}",
                "persona_ref": h.get("target_persona", ""),
                "properties": ["handoff_id", "source_persona", "target_persona", "duration_ms", "timestamp"],
                "privacy_classification": "behavioral",
            })
        return events

    def _infer_metrics(self, handoffs: List[Dict]) -> List[Dict]:
        return [
            {"metric_name": "handoff_completion_time", "formula": "p50/p90/p95 of handoff duration", "data_sources": ["handoff_completed_events"], "aggregation": "percentile", "alert_threshold": "p95 > SLA"},
            {"metric_name": "bottleneck_frequency", "formula": "count of handoffs exceeding SLA / total handoffs", "data_sources": ["handoff_completed_events"], "aggregation": "ratio", "alert_threshold": ">0.1"},
            {"metric_name": "active_workflows", "formula": "count of workflows in progress", "data_sources": ["handoff_initiated_events", "handoff_completed_events"], "aggregation": "count", "alert_threshold": "N/A"},
        ]

    def _predict_dropoffs(self, journey_maps: List[Dict]) -> List[Dict]:
        dropoffs = []
        for jm in journey_maps:
            stages = jm.get("stages", [])
            for i, s in enumerate(stages):
                emotion = s.get("emotion_score", 5)
                if emotion <= 4:
                    dropoffs.append({
                        "stage": s.get("stage_name", f"stage_{i}"),
                        "predicted_dropoff_rate": round(0.5 - emotion * 0.1, 2),
                        "suggested_improvement": f"Improve experience at '{s.get('stage_name')}' for persona '{jm.get('persona_ref')}'",
                    })
        return dropoffs

    def _suggest_ab_tests(self, handoffs: List[Dict]) -> List[Dict]:
        if not handoffs:
            return []
        return [
            {"hypothesis": "Parallel processing at bottleneck reduces completion time by 30%", "target_metric": "handoff_completion_time", "expected_lift": "-30%", "required_sample_size": 200},
        ]

    def _assess_privacy(self, events: List[Dict]) -> List[Dict]:
        return [
            {"event": e["event_name"], "regulation": "GDPR", "risk_level": "low", "mitigation": "Anonymize persona refs in event properties"}
            for e in events[:3]
        ]

    def _suggest_dashboards(self, personas: List[str]) -> List[Dict]:
        return [
            {"audience": "PM", "widgets": ["handoff_completion_times", "bottleneck_heatmap", "sla_violation_rate", "active_workflows"]},
            {"audience": "executive", "widgets": ["overall_workflow_health", "bottleneck_summary", "completion_time_trend"]},
        ]
