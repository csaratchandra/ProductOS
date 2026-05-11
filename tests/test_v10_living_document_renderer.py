"""Tests for ProductOS V11 Living Document Renderer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.markdown_renderer import (
    load_template,
    preserve_annotations,
    render_living_document,
    resolve_source_artifacts,
)


class TestLivingDocumentRenderer:
    """Test the living markdown renderer end-to-end."""

    def test_render_living_document_prd(self, tmp_path: Path, root_dir: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        docs_dir = workspace_dir / "docs"
        docs_dir.mkdir(parents=True)

        prd = {
            "schema_version": "1.0.0",
            "title": "Test PRD",
            "description": "A test PRD for validation.",
            "problem_statement": "Users need faster checkout",
            "solution_approach": "Optimize the checkout pipeline",
            "out_of_scope": ["iOS app", "Enterprise SSO"],
            "acceptance_criteria": ["Checkout completes in <3s", "Mobile responsive"],
        }
        problem_brief = {
            "schema_version": "1.0.0",
            "title": "Problem Brief",
            "summary": "Checkout is too slow.",
        }
        research_notebook = {
            "schema_version": "1.0.0",
            "title": "Research",
            "findings": ["Users abandon at 5s"],
        }
        acceptance_criteria_set = {
            "schema_version": "1.0.0",
            "title": "ACs",
            "criteria": ["<3s checkout"],
        }

        for name, data in [
            ("prd.json", prd),
            ("problem_brief.json", problem_brief),
            ("research_notebook.json", research_notebook),
            ("acceptance_criteria_set.json", acceptance_criteria_set),
        ]:
            with (artifacts_dir / name).open("w") as f:
                json.dump(data, f)

        rendered = render_living_document("prd", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert "Test PRD" in rendered
        assert "Users need faster checkout" in rendered
        assert "Optimize the checkout pipeline" in rendered
        assert "iOS app" in rendered
        assert "Enterprise SSO" in rendered
        assert "Checkout completes in <3s" in rendered
        assert "Mobile responsive" in rendered
        assert "2026-05-06T12:00:00Z" in rendered

    def test_render_living_document_problem_brief(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        problem_brief = {
            "schema_version": "1.0.0",
            "title": "Slow Checkout",
            "summary": "Users abandon checkout due to speed.",
        }
        customer_pulse = {
            "schema_version": "1.0.0",
            "title": "Pulse",
            "quotes": ["This is too slow"],
        }
        persona_narrative_card = {
            "schema_version": "1.0.0",
            "title": "Persona",
            "narrative": "Busy shopper on mobile.",
        }

        for name, data in [
            ("problem_brief.json", problem_brief),
            ("customer_pulse.json", customer_pulse),
            ("persona_narrative_card.json", persona_narrative_card),
        ]:
            with (artifacts_dir / name).open("w") as f:
                json.dump(data, f)

        rendered = render_living_document("problem-brief", workspace_dir, generated_at="2026-05-06T12:00:00Z")

        assert "Slow Checkout" in rendered
        assert "Users abandon checkout due to speed." in rendered

    def test_render_living_document_missing_source_raises(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        (workspace_dir / "artifacts").mkdir(parents=True)

        with pytest.raises(ValueError) as exc_info:
            render_living_document("prd", workspace_dir)

        assert "Missing source artifacts" in str(exc_info.value)

    def test_load_template_existing(self, root_dir: Path):
        template = load_template("prd.md.jinja2")
        assert "{{" in template
        assert "prd" in template.lower() or "product" in template.lower()

    def test_load_template_missing_raises(self):
        with pytest.raises(FileNotFoundError):
            load_template("nonexistent.md.jinja2")

    def test_preserve_annotations_appends(self):
        existing = "# Title\n\nContent\n\n<!-- PM NOTE: Keep pricing hidden until launch -->"
        new_md = "# Title\n\nUpdated content"

        result = preserve_annotations(existing, new_md)
        assert "Keep pricing hidden until launch" in result
        assert "Updated content" in result

    def test_resolve_source_artifacts_all_present(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        artifacts_dir = workspace_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)

        data = {"schema_version": "1.0.0", "title": "Test"}
        with (artifacts_dir / "prd.json").open("w") as f:
            json.dump(data, f)

        sources = resolve_source_artifacts(["artifacts/prd.json"], workspace_dir)
        assert sources["artifacts/prd.json"]["title"] == "Test"

    def test_resolve_source_artifacts_missing_none(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        sources = resolve_source_artifacts(["artifacts/missing.json"], workspace_dir)
        assert sources["artifacts/missing.json"] is None
