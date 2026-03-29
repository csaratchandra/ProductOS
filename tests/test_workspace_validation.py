import json
from pathlib import Path

from core.python.productos_runtime.validation import inspect_workspace_source_note_card_refs


def test_workspace_source_note_card_validation_reports_missing_references(tmp_path: Path):
    workspace_dir = tmp_path / "workspace"
    artifacts_dir = workspace_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    (artifacts_dir / "competitor_dossier.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "competitor_dossier_id": "competitor_dossier_demo",
                "workspace_id": "ws_demo",
                "title": "Broken dossier",
                "research_scope": "Missing note-card reference coverage.",
                "competitors": [
                    {
                        "name": "Example competitor",
                        "competitor_type": "vendor",
                        "target_customer": "Example buyer",
                        "positioning_summary": "Example positioning",
                        "go_to_market_motion": "Example motion",
                        "pricing_signal": "Example pricing",
                        "icp_overlap": "high",
                        "substitution_risk": "high",
                        "ecosystem_role": "Example role",
                        "strengths": ["Example strength"],
                        "weaknesses": ["Example weakness"],
                        "implications": ["Example implication"],
                        "evidence_refs": ["source_note_card_missing_demo"],
                        "confidence": "high",
                        "last_checked_at": "2026-03-29T00:00:00Z",
                    }
                ],
                "created_at": "2026-03-29T00:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    summary, failures = inspect_workspace_source_note_card_refs(workspace_dir)

    assert summary == {"artifact_count": 1, "source_note_card_count": 0}
    assert len(failures) == 1
    assert "competitor_dossier.json:competitors.0.evidence_refs.0" in failures[0]
    assert "source_note_card_missing_demo" in failures[0]


def test_workspace_source_note_card_validation_passes_for_contract_intelligence_workspace(root_dir: Path):
    workspace_dir = root_dir / "workspaces" / "contract-intelligence-platform"

    summary, failures = inspect_workspace_source_note_card_refs(workspace_dir)

    assert summary["source_note_card_count"] == 3
    assert not failures
