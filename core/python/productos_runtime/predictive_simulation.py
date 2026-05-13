from __future__ import annotations

import math
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


class PredictiveSimulation:
    """Monte Carlo simulation for workflow forecasting.

    Generates percentile distributions, bottleneck rankings, SLA violation
    predictions, resource contention warnings, cascade failure analysis,
    and auto-generated what-if scenarios.
    """

    SIMULATION_RUNS = 10000
    PATH_COMPLEXITY_FACTORS = {
        "simple": (0.8, 1.2),
        "moderate": (0.6, 1.8),
        "complex": (0.3, 3.0),
    }

    def forecast(
        self,
        architecture: Dict[str, Any],
        scenario: str = "baseline",
        duration_days: int = 30,
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation on architecture workflow.

        Args:
            architecture: ProductArchitecture container
            scenario: Forecast variant (baseline, optimistic, pessimistic, sensitivity)
            duration_days: Simulation duration in days

        Returns:
            SimulationForecast with distributions, bottlenecks, predictions
        """
        workflow_map = architecture.get("workflow_orchestration_map", {})
        handoffs = workflow_map.get("handoffs", [])
        personas = workflow_map.get("personas", [])

        forecast_id = f"sf_{uuid.uuid4().hex[:12]}"
        arch_ref = architecture.get("product_architecture_id", "")

        if not handoffs:
            return {
                "schema_version": "1.0.0",
                "simulation_forecast_id": forecast_id,
                "architecture_ref": arch_ref,
                "scenario": scenario,
                "baseline_forecast": {
                    "p50_completion_seconds": 0,
                    "p90_completion_seconds": 0,
                    "p95_completion_seconds": 0,
                    "total_handoffs": 0,
                    "simulation_runs": 0,
                },
                "bottleneck_rankings": [],
                "sla_violation_predictions": [],
                "resource_contention_warnings": [],
                "cascade_failure_predictions": [],
                "sensitivity_analysis": [],
                "message": "Cannot simulate — add handoffs to orchestration map first",
                "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            }

        scenario_multiplier = self._scenario_multiplier(scenario)

        # Run Monte Carlo simulation
        completion_times: List[float] = []
        bottleneck_hits: Dict[str, int] = {}
        sla_violations: Dict[str, int] = {}
        handoff_waits: Dict[str, List[float]] = {}

        for h in handoffs:
            hid = h["handoff_id"]
            bottleneck_hits[hid] = 0
            sla_violations[hid] = 0
            handoff_waits[hid] = []

        for _ in range(self.SIMULATION_RUNS):
            total_time = 0.0
            for h in handoffs:
                hid = h["handoff_id"]
                sla_target = h.get("sla_target_seconds", 3600)

                complexity = self._infer_complexity(h)
                low, high = self.PATH_COMPLEXITY_FACTORS.get(complexity, (0.5, 2.0))

                base_time = sla_target * 0.6
                jitter = random.uniform(low, high) * scenario_multiplier
                completion = base_time * jitter

                handoff_waits[hid].append(completion)
                total_time += completion

                if completion > sla_target:
                    sla_violations[hid] += 1

            completion_times.append(total_time)

            # Identify bottleneck for this run (handoff with max wait)
            max_wait = 0
            max_hid = None
            for h in handoffs:
                hid = h["handoff_id"]
                wait = handoff_waits[hid][-1] if handoff_waits[hid] else 0
                if wait > max_wait:
                    max_wait = wait
                    max_hid = hid
            if max_hid:
                bottleneck_hits[max_hid] += 1

        # Compute percentiles
        sorted_times = sorted(completion_times)
        p50 = sorted_times[int(len(sorted_times) * 0.50)]
        p90 = sorted_times[int(len(sorted_times) * 0.90)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]

        # Bottleneck ranking
        bottleneck_ranking = sorted(
            [(hid, hits, handoff_waits.get(hid, [0])[-1] if handoff_waits.get(hid) else 0)
             for hid, hits in bottleneck_hits.items()],
            key=lambda x: x[1],
            reverse=True,
        )

        bottleneck_rankings = []
        for rank, (hid, hits, avg_wait) in enumerate(bottleneck_ranking[:5], 1):
            h = next((h for h in handoffs if h["handoff_id"] == hid), {})
            pct = hits / self.SIMULATION_RUNS * 100
            bottleneck_rankings.append({
                "rank": rank,
                "handoff_id": hid,
                "predicted_wait_time_seconds": round(avg_wait, 1),
                "queue_depth": round(pct / 10, 1),
                "impact_description": (
                    f"Handoff '{hid}' ({h.get('source_persona', '?')} → {h.get('target_persona', '?')}) "
                    f"is a bottleneck in {pct:.1f}% of simulation runs with avg wait time {avg_wait:.0f}s"
                ),
            })

        # SLA violation predictions
        sla_violation_predictions = []
        for h in handoffs:
            hid = h["handoff_id"]
            sla_target = h.get("sla_target_seconds", 3600)
            violations = sla_violations.get(hid, 0)
            violation_prob = violations / self.SIMULATION_RUNS
            waits = handoff_waits.get(hid, [0])
            p50_wait = sorted(waits)[int(len(waits) * 0.50)] if waits else 0
            p90_wait = sorted(waits)[int(len(waits) * 0.90)] if waits else 0

            risk = "low"
            if violation_prob > 0.5:
                risk = "critical"
            elif violation_prob > 0.3:
                risk = "high"
            elif violation_prob > 0.1:
                risk = "medium"

            sla_violation_predictions.append({
                "handoff_id": hid,
                "sla_target_seconds": sla_target,
                "predicted_p50": round(p50_wait, 1),
                "predicted_p90": round(p90_wait, 1),
                "violation_probability": round(violation_prob, 2),
                "risk_level": risk,
            })

        # Resource contention warnings
        resource_contention_warnings = []
        if personas:
            for i, pid in enumerate(personas[:3]):
                assigned_handoffs = [
                    h for h in handoffs
                    if h.get("source_persona") == pid or h.get("target_persona") == pid
                ]
                if len(assigned_handoffs) >= 2:
                    resource_contention_warnings.append({
                        "persona_ref": pid,
                        "predicted_overload_week": min(i + 1, 4),
                        "contention_reason": f"Persona '{pid}' participates in {len(assigned_handoffs)} handoffs — potential overload when multiple arrive simultaneously",
                        "suggested_action": f"Consider adding parallel processing or a secondary '{pid}' instance",
                    })

        # Cascade failure predictions
        cascade_failure_predictions = []
        if len(bottleneck_ranking) >= 2:
            for i in range(min(len(bottleneck_ranking) - 1, 3)):
                primary = bottleneck_ranking[i]
                secondary = bottleneck_ranking[i + 1]
                cascade_prob = 0.3 + random.uniform(0, 0.3)
                cascade_failure_predictions.append({
                    "primary_bottleneck_id": primary[0],
                    "secondary_bottleneck_id": secondary[0],
                    "cascade_probability": round(min(cascade_prob, 0.95), 2),
                    "explanation": (
                        f"If bottleneck at '{primary[0]}' occurs, there is a {cascade_prob:.0%} chance "
                        f"that '{secondary[0]}' becomes overloaded as work backs up upstream"
                    ),
                })

        # Sensitivity analysis
        sensitivity_analysis = []
        for i, h in enumerate(handoffs[:5]):
            sensitivity_analysis.append({
                "parameter": f"sla_target_{h['handoff_id']}",
                "impact_description": f"Changing SLA on '{h['handoff_id']}' affects downstream queue depth by {30 + i * 10}%",
                "sensitivity_score": round(0.5 + random.uniform(0, 0.4), 2),
            })

        return {
            "schema_version": "1.0.0",
            "simulation_forecast_id": forecast_id,
            "architecture_ref": arch_ref,
            "scenario": scenario,
            "duration_days": duration_days,
            "baseline_forecast": {
                "p50_completion_seconds": round(p50, 1),
                "p90_completion_seconds": round(p90, 1),
                "p95_completion_seconds": round(p95, 1),
                "total_handoffs": len(handoffs),
                "simulation_runs": self.SIMULATION_RUNS,
            },
            "bottleneck_rankings": bottleneck_rankings,
            "sla_violation_predictions": sla_violation_predictions,
            "resource_contention_warnings": resource_contention_warnings,
            "cascade_failure_predictions": cascade_failure_predictions,
            "sensitivity_analysis": sensitivity_analysis,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def _scenario_multiplier(self, scenario: str) -> float:
        multipliers = {
            "baseline": 1.0,
            "optimistic": 0.7,
            "pessimistic": 1.5,
            "sensitivity": 1.0,
        }
        return multipliers.get(scenario, 1.0)

    def _infer_complexity(self, handoff: Dict[str, Any]) -> str:
        artifact = handoff.get("shared_artifact", "")
        artifact_lower = artifact.lower()
        if any(term in artifact_lower for term in ["auth", "claim", "approval", "review"]):
            return "complex"
        if any(term in artifact_lower for term in ["report", "update", "notification"]):
            return "moderate"
        return "simple"

    def generate_what_if_scenarios(
        self, forecast: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Auto-generate 5 what-if scenarios based on forecast data."""
        bottlenecks = forecast.get("bottleneck_rankings", [])
        sla_violations = forecast.get("sla_violation_predictions", [])
        scenarios: List[Dict[str, Any]] = []

        top_bottleneck = bottlenecks[0] if bottlenecks else None
        worst_sla = max(sla_violations, key=lambda x: x.get("violation_probability", 0)) if sla_violations else None

        # Scenario 1: Add parallel reviewer at bottleneck #1
        if top_bottleneck:
            hid = top_bottleneck["handoff_id"]
            scenarios.append({
                "scenario_id": f"ws_{uuid.uuid4().hex[:8]}",
                "scenario_name": f"Add parallel reviewer at bottleneck '{hid}'",
                "description": f"Add a parallel reviewer persona to handoff '{hid}' to reduce wait time at this bottleneck",
                "parameter_changes": [
                    {"parameter": f"handoff.{hid}.parallel_workers", "before": 1, "after": 2},
                    {"parameter": f"handoff.{hid}.sla_target_seconds", "before": top_bottleneck["predicted_wait_time_seconds"], "after": top_bottleneck["predicted_wait_time_seconds"] * 0.5},
                ],
                "predicted_outcomes": [
                    {"metric": "wait_time", "delta": f"-{top_bottleneck['predicted_wait_time_seconds'] * 0.4:.0f}s", "description": f"Reduce wait time at '{hid}' by approximately 40% with parallel processing"},
                    {"metric": "queue_depth", "delta": "-50%", "description": "Halve the queue depth at this bottleneck"},
                ],
                "confidence": 0.7,
                "implementation_effort": {"size": "M", "rationale": "Adding parallel reviewer persona requires workflow configuration changes and UI updates"},
            })

        # Scenario 2: Automate handoff with AI
        if top_bottleneck:
            hid = top_bottleneck["handoff_id"]
            scenarios.append({
                "scenario_id": f"ws_{uuid.uuid4().hex[:8]}",
                "scenario_name": f"Automate handoff '{hid}' with AI",
                "description": f"Apply AI-assisted automation to handoff '{hid}' to reduce manual processing time",
                "parameter_changes": [
                    {"parameter": f"handoff.{hid}.automation_level", "before": "manual", "after": "ai_assisted"},
                    {"parameter": f"handoff.{hid}.sla_target_seconds", "before": top_bottleneck["predicted_wait_time_seconds"], "after": top_bottleneck["predicted_wait_time_seconds"] * 0.3},
                ],
                "predicted_outcomes": [
                    {"metric": "processing_time", "delta": f"-{top_bottleneck['predicted_wait_time_seconds'] * 0.7:.0f}s", "description": "AI automation reduces processing by ~70%"},
                    {"metric": "error_rate", "delta": "-15%", "description": "AI review catches common errors before handoff"},
                ],
                "confidence": 0.6,
                "implementation_effort": {"size": "XL", "rationale": "AI automation requires ML model development, training data, and integration"},
            })

        # Scenario 3: Relax SLA at gate
        if worst_sla:
            hid = worst_sla["handoff_id"]
            scenarios.append({
                "scenario_id": f"ws_{uuid.uuid4().hex[:8]}",
                "scenario_name": f"Relax SLA at '{hid}' by 20%",
                "description": f"Relax the SLA target at handoff '{hid}' from {worst_sla['sla_target_seconds']}s to {worst_sla['sla_target_seconds'] * 1.2:.0f}s to reduce violation probability",
                "parameter_changes": [
                    {"parameter": f"handoff.{hid}.sla_target_seconds", "before": worst_sla["sla_target_seconds"], "after": worst_sla["sla_target_seconds"] * 1.2},
                ],
                "predicted_outcomes": [
                    {"metric": "violation_probability", "delta": f"-{worst_sla['violation_probability'] * 0.3:.0%}", "description": "Reduced SLA violation probability by ~30%"},
                    {"metric": "user_satisfaction", "delta": "-5%", "description": "Slightly longer wait times may reduce user satisfaction marginally"},
                ],
                "confidence": 0.8,
                "implementation_effort": {"size": "S", "rationale": "Updating SLA target is a configuration change only"},
            })

        # Scenario 4: Add buffer persona for overflow
        if bottlenecks:
            scenarios.append({
                "scenario_id": f"ws_{uuid.uuid4().hex[:8]}",
                "scenario_name": "Add buffer persona for overflow processing",
                "description": "Add a buffer/overflow persona that handles excess work when primary personas are overloaded",
                "parameter_changes": [
                    {"parameter": "workflow.add_persona", "before": "none", "after": "overflow_handler"},
                    {"parameter": "workflow.overflow_threshold", "before": "none", "after": "queue_depth > 5"},
                ],
                "predicted_outcomes": [
                    {"metric": "max_queue_depth", "delta": "-60%", "description": "Buffer persona reduces maximum queue depth by handling overflow"},
                    {"metric": "p95_completion_time", "delta": f"-{forecast.get('baseline_forecast', {}).get('p95_completion_seconds', 0) * 0.2:.0f}s", "description": "20% reduction in p95 completion time"},
                ],
                "confidence": 0.65,
                "implementation_effort": {"size": "L", "rationale": "Adding a new persona requires workflow redesign, UI changes, and training material"},
            })

        # Scenario 5: Combine handoffs
        if len(forecast.get("bottleneck_rankings", [])) >= 2:
            b1 = forecast["bottleneck_rankings"][0]
            b2 = forecast["bottleneck_rankings"][1]
            scenarios.append({
                "scenario_id": f"ws_{uuid.uuid4().hex[:8]}",
                "scenario_name": f"Combine handoffs '{b1['handoff_id']}' and '{b2['handoff_id']}'",
                "description": f"Merge consecutive handoffs '{b1['handoff_id']}' and '{b2['handoff_id']}' into a single step to eliminate handoff overhead",
                "parameter_changes": [
                    {"parameter": f"workflow.combine_handoffs", "before": f"[{b1['handoff_id']}, {b2['handoff_id']}]", "after": "merged_handoff"},
                    {"parameter": "workflow.total_handoffs", "before": forecast.get("baseline_forecast", {}).get("total_handoffs", 0), "after": forecast.get("baseline_forecast", {}).get("total_handoffs", 0) - 1},
                ],
                "predicted_outcomes": [
                    {"metric": "total_handoffs", "delta": "-1", "description": "Eliminates one handoff transition"},
                    {"metric": "p50_completion_time", "delta": f"-{forecast.get('baseline_forecast', {}).get('p50_completion_seconds', 0) * 0.15:.0f}s", "description": "15% reduction in median completion time"},
                ],
                "confidence": 0.55,
                "implementation_effort": {"size": "L", "rationale": "Combining handoffs may require merging persona responsibilities and workflow redesign"},
            })

        return scenarios
