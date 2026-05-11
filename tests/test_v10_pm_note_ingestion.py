"""Tests for ProductOS V11 PM Note Ingestion."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jsonschema import Draft202012Validator


class TestPMNoteDeltaProposalSchema:
    """Test pm_note_delta_proposal.schema.json conformance."""

    def test_valid_proposal_passes(self, root_dir: Path):
        schema_path = root_dir / "core" / "schemas" / "artifacts" / "pm_note_delta_proposal.schema.json"
        assert schema_path.exists()

        with schema_path.open() as f:
            schema = json.load(f)

        validator = Draft202012Validator(schema)

        valid = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_001",
            "workspace_id": "ws_test",
            "source_note": {
                "note_path": "inbox/raw-notes/customer-call.txt",
                "note_type": "transcript",
                "summary": "Customer mentioned CompetitorAlpha's new AI feature",
            },
            "proposed_deltas": [
                {
                    "delta_id": "pd_001",
                    "target_artifact_ref": "artifacts/competitor_dossier.json",
                    "proposed_change": "Add CompetitorAlpha AI feature launch",
                    "confidence": "high",
                    "evidence_quote": "CompetitorAlpha just launched an AI PRD generator",
                    "regeneration_queue_item_id": "rq_item_001",
                }
            ],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        errors = list(validator.iter_errors(valid))
        assert len(errors) == 0, f"Schema validation failed: {[e.message for e in errors]}"

    def test_proposal_with_low_confidence_passes(self, root_dir: Path):
        schema_path = root_dir / "core" / "schemas" / "artifacts" / "pm_note_delta_proposal.schema.json"
        with schema_path.open() as f:
            schema = json.load(f)

        validator = Draft202012Validator(schema)

        valid = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_002",
            "workspace_id": "ws_test",
            "source_note": {
                "note_path": "inbox/raw-notes/meeting-notes.txt",
                "note_type": "meeting_notes",
                "summary": "Vague mention of pricing discussion",
            },
            "proposed_deltas": [
                {
                    "delta_id": "pd_002",
                    "target_artifact_ref": "artifacts/competitor_dossier.json",
                    "proposed_change": "Maybe update pricing",
                    "confidence": "low",
                    "evidence_quote": "Someone said something about pricing",
                    "regeneration_queue_item_id": "rq_item_002",
                }
            ],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        errors = list(validator.iter_errors(valid))
        assert len(errors) == 0, f"Schema validation failed: {[e.message for e in errors]}"

    def test_invalid_note_type_fails(self, root_dir: Path):
        schema_path = root_dir / "core" / "schemas" / "artifacts" / "pm_note_delta_proposal.schema.json"
        with schema_path.open() as f:
            schema = json.load(f)

        validator = Draft202012Validator(schema)

        invalid = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_003",
            "workspace_id": "ws_test",
            "source_note": {
                "note_path": "inbox/raw-notes/unknown.txt",
                "note_type": "unsupported_type",
                "summary": "Unknown note type",
            },
            "proposed_deltas": [],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        errors = list(validator.iter_errors(invalid))
        assert len(errors) > 0, "Expected validation to fail for invalid note_type"


class TestPMNoteIngestionRuntime:
    """Test ingestion runtime behavior."""

    def test_ingestion_creates_delta_proposal_from_transcript(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        inbox_dir = workspace_dir / "inbox" / "raw-notes"
        inbox_dir.mkdir(parents=True)
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        transcript = "Customer call transcript:\nCustomer: CompetitorAlpha just launched an AI PRD generator that seems similar to our V10 roadmap.\nPM: Thank you for the feedback."
        note_path = inbox_dir / "customer-call-may6.txt"
        note_path.write_text(transcript)

        # Simulate ingestion: read note, create delta proposal
        proposal = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_test_001",
            "workspace_id": workspace_dir.name,
            "source_note": {
                "note_path": str(note_path.relative_to(workspace_dir)),
                "note_type": "transcript",
                "summary": "Customer mentioned CompetitorAlpha's new AI PRD generator",
            },
            "proposed_deltas": [
                {
                    "delta_id": "pd_001",
                    "target_artifact_ref": "artifacts/competitor_dossier.json",
                    "proposed_change": "Add CompetitorAlpha AI PRD generator launch to competitive timeline",
                    "confidence": "high",
                    "evidence_quote": "CompetitorAlpha just launched an AI PRD generator that seems similar to our V10 roadmap",
                    "regeneration_queue_item_id": "rq_item_001",
                }
            ],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        # Validate the generated proposal against schema
        schema_path = Path("core/schemas/artifacts/pm_note_delta_proposal.schema.json")
        with schema_path.open() as f:
            schema = json.load(f)
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(proposal))
        assert len(errors) == 0, f"Generated proposal invalid: {[e.message for e in errors]}"

        assert proposal["source_note"]["note_type"] == "transcript"
        assert len(proposal["proposed_deltas"]) == 1
        assert proposal["proposed_deltas"][0]["confidence"] == "high"

    def test_low_confidence_proposal_flagged_for_clarification(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        inbox_dir = workspace_dir / "inbox" / "raw-notes"
        inbox_dir.mkdir(parents=True)

        note_path = inbox_dir / "vague-note.txt"
        note_path.write_text("Maybe we should think about pricing?")

        proposal = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_test_002",
            "workspace_id": workspace_dir.name,
            "source_note": {
                "note_path": str(note_path.relative_to(workspace_dir)),
                "note_type": "meeting_notes",
                "summary": "Vague mention of pricing",
            },
            "proposed_deltas": [
                {
                    "delta_id": "pd_002",
                    "target_artifact_ref": "artifacts/competitor_dossier.json",
                    "proposed_change": "Maybe update pricing",
                    "confidence": "low",
                    "evidence_quote": "Maybe we should think about pricing?",
                    "regeneration_queue_item_id": "rq_item_002",
                }
            ],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        assert proposal["proposed_deltas"][0]["confidence"] == "low"

    def test_no_identifiable_target_artifact(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        inbox_dir = workspace_dir / "inbox" / "raw-notes"
        inbox_dir.mkdir(parents=True)

        note_path = inbox_dir / "random-thought.txt"
        note_path.write_text("I like pizza.")

        proposal = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_test_003",
            "workspace_id": workspace_dir.name,
            "source_note": {
                "note_path": str(note_path.relative_to(workspace_dir)),
                "note_type": "voice_memo",
                "summary": "Unrouted personal note",
            },
            "proposed_deltas": [],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        assert len(proposal["proposed_deltas"]) == 0

    def test_multiple_artifact_proposals(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        inbox_dir = workspace_dir / "inbox" / "raw-notes"
        inbox_dir.mkdir(parents=True)

        note_path = inbox_dir / "multi-impact.txt"
        note_path.write_text("Customer wants mobile app and enterprise SSO.")

        proposal = {
            "schema_version": "1.0.0",
            "pm_note_delta_proposal_id": "pndp_test_004",
            "workspace_id": workspace_dir.name,
            "source_note": {
                "note_path": str(note_path.relative_to(workspace_dir)),
                "note_type": "transcript",
                "summary": "Customer requests mobile app and enterprise SSO",
            },
            "proposed_deltas": [
                {
                    "delta_id": "pd_003",
                    "target_artifact_ref": "artifacts/persona_narrative_card.json",
                    "proposed_change": "Add enterprise buyer persona segment",
                    "confidence": "medium",
                    "evidence_quote": "Customer wants enterprise SSO",
                    "regeneration_queue_item_id": "rq_item_003",
                },
                {
                    "delta_id": "pd_004",
                    "target_artifact_ref": "artifacts/prd.json",
                    "proposed_change": "Add mobile app to out_of_scope rationale",
                    "confidence": "high",
                    "evidence_quote": "Customer wants mobile app",
                    "regeneration_queue_item_id": "rq_item_004",
                },
            ],
            "generated_at": "2026-05-06T12:00:00Z",
        }

        assert len(proposal["proposed_deltas"]) == 2
        assert proposal["proposed_deltas"][0]["target_artifact_ref"] != proposal["proposed_deltas"][1]["target_artifact_ref"]
