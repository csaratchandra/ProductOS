from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import DeterministicProvider


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas" / "artifacts"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_schema(schema_name: str) -> dict[str, Any]:
    with (SCHEMA_DIR / schema_name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_from_schema(
    schema_name: str,
    *,
    workspace_dir: Path,
    artifact_id_key: str,
    artifact_id_value: str,
    title: str,
    generated_at_key: str,
    generated_at: str,
) -> dict[str, Any]:
    payload = DeterministicProvider().generate_structured(title, _load_schema(schema_name))
    payload[artifact_id_key] = artifact_id_value
    payload["workspace_id"] = workspace_dir.name
    if "title" in _load_schema(schema_name).get("properties", {}):
        payload["title"] = title
    payload[generated_at_key] = generated_at
    return payload


def run_prd_scope_boundary_check(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    from .prd_scope_boundary import build_prd_boundary_report

    return build_prd_boundary_report(workspace_dir, generated_at=generated_at or _now_iso())


def run_trade_off_analysis(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "schema_version": "1.0.0",
        "decision_analysis_id": f"decision_analysis_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "title": "Trade-Off Analysis",
        "decision_question": "Which bounded delivery option best proves the next ProductOS wedge?",
        "analysis_type": ["trade_off", "decision_tree", "premortem"],
        "status": "analysis_complete",
        "context": {
            "stakes": "The next slice should improve proof without expanding release claims prematurely.",
            "stakeholders": ["Product Manager", "Builder", "Reviewer"],
            "timeline_pressure": "short_term",
            "constraints": ["Keep scope bounded", "Maintain repo-backed proof"],
        },
        "trade_off_analysis": {
            "options": [
                {
                    "option_id": "opt_a",
                    "name": "Finish living-system gaps",
                    "description": "Complete the queue, review, and readable-doc gaps.",
                    "expected_outcome": "Strongest near-term release proof.",
                    "cost_estimate": "med",
                    "timeline_estimate": "one_week",
                    "risk_level": "medium",
                },
                {
                    "option_id": "opt_b",
                    "name": "Broaden launch collateral",
                    "description": "Invest in collateral and onboarding before runtime hardening.",
                    "expected_outcome": "Better demo polish but weaker runtime proof.",
                    "cost_estimate": "med",
                    "timeline_estimate": "one_week",
                    "risk_level": "high",
                },
            ],
            "criteria": [
                {"criterion_id": "proof", "name": "Proof", "weight": 50, "type": "must_have"},
                {"criterion_id": "speed", "name": "Speed", "weight": 25, "type": "quantitative"},
                {"criterion_id": "clarity", "name": "Clarity", "weight": 25, "type": "qualitative"},
            ],
            "scoring_matrix": {
                "scores": [
                    {"option_id": "opt_a", "criterion_scores": {"proof": 9, "speed": 7, "clarity": 8}},
                    {"option_id": "opt_b", "criterion_scores": {"proof": 5, "speed": 7, "clarity": 6}},
                ],
                "weighted_totals": {"opt_a": 825, "opt_b": 575},
                "ranked_options": ["opt_a", "opt_b"],
            },
            "recommendation": {
                "recommended_option_id": "opt_a",
                "rationale": "It strengthens the stable release claim boundary directly.",
                "key_trade_offs": ["Less collateral polish in the short term."],
                "what_is_lost": "A broader marketing-ready surface this week.",
            },
        },
        "decision_tree": {
            "nodes": [
                {"node_id": "n1", "type": "decision", "label": "Prioritize runtime proof"},
                {"node_id": "n2", "type": "chance", "label": "Proof passes tests"},
                {"node_id": "n3", "type": "outcome", "label": "Stable promotion ready"},
            ],
            "probabilities": [
                {"from_node_id": "n1", "to_node_id": "n2", "probability": 0.8, "label": "Execute"},
                {"from_node_id": "n2", "to_node_id": "n3", "probability": 0.75, "label": "Pass"},
            ],
            "expected_values": {"n3": 80},
            "recommended_path": "n1->n2->n3",
        },
        "premortem": {
            "failure_scenarios": [
                {
                    "scenario": "Release claim outruns repo proof.",
                    "probability": "possible",
                    "impact_if_occurs": "severe",
                    "leading_indicators": ["Unvalidated features", "Stale verification docs"],
                },
                {
                    "scenario": "A key adapter surface lands without stable CLI validation coverage.",
                    "probability": "unlikely",
                    "impact_if_occurs": "moderate",
                    "leading_indicators": ["New commands lack tests", "JSON contracts drift"],
                },
            ],
            "early_warning_indicators": [
                "Tests cover fewer surfaces than the release claim.",
                "Verification status falls behind implementation changes.",
            ],
            "reversal_triggers": ["Stable release alignment fails."],
        },
        "reversibility_scoring": {
            "reversibility_level": "reversible_with_effort",
            "cost_to_reverse": "One follow-up patch and release note correction.",
            "time_to_reverse": "1 day",
            "irreversible_after": "Public promotion and downstream adoption.",
            "recommendation": "Prefer proof before promotion.",
        },
        "recommended_decision": {
            "recommendation": "Finish runtime proof before expanding scope.",
            "confidence": "moderate",
            "assumptions": ["Current tests cover the highest-risk surfaces."],
            "review_trigger": "Any regression in queue, new, or adapter flows.",
        },
        "source_evidence_refs": ["tests", "verification_doc"],
        "generated_at": generated_at,
    }


def run_decision_tree_construction(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "decision_tree_id": f"decision_tree_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "title": "Decision Tree Construction",
        "expected_value_summary": "Use the generated decision analysis plus explicit branch probabilities before committing to a wider wedge.",
        "generated_at": generated_at,
    }


def run_premortem_analysis(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "schema_version": "1.0.0",
        "decision_premortem_id": f"decision_premortem_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "decision_statement": "Promote the current V12 slice only after repo proof and release surfaces align.",
        "failure_causes": ["Queue and release evidence drift apart after implementation."],
        "early_warning_indicators": ["Verification doc no longer matches the codebase."],
        "reversal_triggers": ["Validation coverage regresses or README claims outrun proof."],
        "success_conditions": ["Targeted and broadened tests remain green."],
        "created_at": generated_at,
    }


def run_battle_card_generation(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "schema_version": "1.0.0",
        "battle_card_id": f"battle_card_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "title": "Battle Card",
        "competitor_ref": "static_docs_stack",
        "overview": {
            "one_liner": "Compete on living execution, not just drafting.",
            "our_positioning_vs_theirs": "We maintain repo-native truth and bounded review gates while static docs require manual propagation.",
            "primary_competitive_advantage": "Living artifact execution.",
            "primary_competitive_disadvantage": "Lower category awareness.",
        },
        "feature_comparison": [
            {"feature": "Structured artifacts", "our_capability": "strong", "their_capability": "weak", "advantage": "us", "detail": "Schema-backed."},
            {"feature": "Living docs", "our_capability": "strong", "their_capability": "adequate", "advantage": "us", "detail": "Auto-regenerates."},
            {"feature": "Agent context", "our_capability": "strong", "their_capability": "absent", "advantage": "us", "detail": "CLI-native."},
            {"feature": "Ad hoc collaboration", "our_capability": "adequate", "their_capability": "strong", "advantage": "them", "detail": "Broader default familiarity."},
            {"feature": "Release governance", "our_capability": "strong", "their_capability": "weak", "advantage": "us", "detail": "Repo-proof gating."},
        ],
        "pricing_comparison": "We compete on execution proof rather than document-seat bundling.",
        "ideal_customer_profile": "PM teams that need AI assistance without giving up bounded reviewability.",
        "win_themes": [
            {"theme": "Proof", "description": "Lead with repo-backed living execution."},
            {"theme": "Control", "description": "Emphasize bounded review and release posture."},
        ],
        "loss_themes": [
            {"theme": "Awareness", "description": "We have less broad category familiarity."}
        ],
        "objection_handling": [
            {"objection": "Why not stay in docs?", "response": "Docs stay static while ProductOS keeps the same source of truth live across outputs.", "supporting_evidence": "Queue + render flows."},
            {"objection": "Is this too opinionated?", "response": "The repo remains open and inspectable, so the operating model stays reviewable and adaptable.", "supporting_evidence": "Repo-native CLI and schemas."},
        ],
        "sales_conversation_guide": "Anchor the conversation on living artifact proof, explicit boundaries, and agent-native execution readiness.",
        "recent_competitive_moves": "Static and AI drafting tools are converging, but most still lack repo-native living execution.",
        "generated_at": generated_at,
    }


def run_investor_content_generation(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    section = lambda title, content: {
        "title": title,
        "content": content,
        "key_claims": [content[:80] + " claim"],
    }
    return {
        "schema_version": "1.0.0",
        "investor_memo_id": f"investor_memo_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "company_name": "ProductOS",
        "executive_summary": "ProductOS is building the repo-native PM operating system for teams that need AI assistance, bounded reviewability, and machine-readable execution context across living artifacts and release workflows.",
        "sections": [
            section("Problem", "PM teams lose time reconciling static documents and fragmented tools before work becomes reviewable."),
            section("Solution", "ProductOS turns schemas, CLI, and living updates into one repo-native operating surface."),
            section("Market", "AI-native execution is increasing demand for tools agents can drive directly rather than scrape."),
            section("Advantage", "Repo-backed truth and bounded release posture create defensibility and trust."),
            section("Go To Market", "Start with PM teams that already work in repos and need faster review cycles."),
            section("Risks", "Proof must stay ahead of claims or trust erodes quickly in decision-driving workflows."),
        ],
        "generated_at": generated_at,
    }


def run_api_contract_generation(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "schema_version": "1.0.0",
        "api_contract_id": f"api_contract_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "title": "API Contract",
        "base_path": "/v1",
        "endpoints": [
            {
                "method": "POST",
                "path": "/artifacts/render",
                "summary": "Render a structured artifact into a readable output.",
                "request": {"content_type": "application/json", "parameters": [], "body_schema": {}, "example_body": {}},
                "responses": [{"status_code": 200, "description": "Artifact rendered successfully.", "body_schema": {}, "example_body": {}}],
                "tags": ["artifacts"],
            }
        ],
        "auth": {"type": "none"},
        "rate_limiting": {"requests_per_minute": 60, "headers": True, "burst_limit": 10},
        "common_error_responses": [
            {"status_code": 400, "error_code": "BAD_INPUT", "message": "The request payload was invalid.", "resolution_hint": "Validate the artifact reference and required fields."}
        ],
        "generated_at": generated_at,
    }


def run_stakeholder_management(workspace_dir: Path, *, generated_at: str | None = None) -> dict[str, Any]:
    generated_at = generated_at or _now_iso()
    return {
        "schema_version": "1.0.0",
        "stakeholder_map_id": f"stakeholder_map_{workspace_dir.name}",
        "workspace_id": workspace_dir.name,
        "title": "Stakeholder Map",
        "stakeholders": [
            {
                "stakeholder_id": "pm",
                "name": "Product Manager",
                "role": "PM owner",
                "power_level": 5,
                "interest_level": 5,
                "current_position": "supporter",
                "key_concerns": ["Keeps scope bounded and proof visible."],
                "communication_preference": "Weekly written review with explicit next steps.",
            },
            {
                "stakeholder_id": "builder",
                "name": "Engineering Lead",
                "role": "Build partner",
                "power_level": 4,
                "interest_level": 4,
                "current_position": "neutral",
                "key_concerns": ["Needs clear boundaries and test coverage."],
                "communication_preference": "Short implementation notes and concrete acceptance checks.",
            },
            {
                "stakeholder_id": "reviewer",
                "name": "Release Reviewer",
                "role": "Release gate",
                "power_level": 4,
                "interest_level": 3,
                "current_position": "supporter",
                "key_concerns": ["Claims must stay aligned with proof."],
                "communication_preference": "Pre-release checklist with validation evidence.",
            },
        ],
        "visual_spec": {"title": "Power / Interest Grid", "grid_type": "power_interest_grid"},
        "generated_at": generated_at,
    }
