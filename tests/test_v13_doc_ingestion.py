"""Tests for V13 document ingestion module."""

import json
from pathlib import Path

import pytest

from core.python.productos_runtime.doc_ingestion import (
    ingest_document,
    _classify_document_type,
    _extract_document_text,
    _heuristic_extract_entities,
    detect_contradictions,
    build_ingestion_report,
    classify_file_content_aware,
)


class TestDocumentClassification:
    def test_classify_prd(self):
        doc_type = _classify_document_type(Path("prd_onboarding.md"))
        assert doc_type == "prd_document"

    def test_classify_strategy(self):
        doc_type = _classify_document_type(Path("strategy_2026.md"))
        assert doc_type == "strategy_doc"

    def test_classify_unknown(self):
        doc_type = _classify_document_type(Path("random_file.txt"))
        assert doc_type in ("strategy_doc", "other")


class TestEntityExtraction:
    def test_heuristic_extraction(self):
        content = """
        Problem: Users cannot find the search feature.
        Persona: Jane the power user needs this.
        Feature: Advanced search with filters.
        Decision: We decided to build this in-house.
        Competitor: Acme Corp offers similar functionality.
        KPI: Target 90% search success rate.
        """
        entities = _heuristic_extract_entities(content)
        assert len(entities["problems"]) > 0
        assert len(entities["personas"]) > 0
        assert len(entities["features"]) > 0
        assert len(entities["decisions"]) > 0
        assert len(entities["competitors"]) > 0
        assert len(entities["metrics"]) > 0


class TestContradictionDetection:
    def test_no_contradiction_with_single_source(self):
        sources = [
            {"source_id": "src_1", "extracted_entities": {"features": ["f1", "f2"], "segments": []}},
        ]
        contradictions = detect_contradictions(sources)
        assert len(contradictions) == 0

    def test_detects_feature_overlap(self):
        sources = [
            {"source_id": "src_1", "extracted_entities": {"features": ["f1", "f2"], "segments": []}},
            {"source_id": "src_2", "extracted_entities": {"features": ["f1", "f3"], "segments": []}},
        ]
        contradictions = detect_contradictions(sources)
        assert len(contradictions) >= 1


class TestIngestionReport:
    def test_build_report_output(self, tmp_path):
        sources = [
            {"source_id": "src_1", "source_type": "prd_document", "extraction_confidence": "observed", "extracted_entities": {}},
        ]
        report = build_ingestion_report(tmp_path, sources, contradictions=[])
        assert report["schema_version"] == "1.0.0"
        assert len(report["ingested_sources"]) == 1
        assert "ingestion_coverage" in report

    def test_report_detects_domain_coverage(self, tmp_path):
        sources = [
            {"source_id": "s1", "source_type": "prd_document", "extraction_confidence": "observed", "extracted_entities": {}},
            {"source_id": "s2", "source_type": "screenshot", "extraction_confidence": "inferred", "extracted_entities": {}},
        ]
        report = build_ingestion_report(tmp_path, sources, contradictions=[])
        domains = report["ingestion_coverage"]["domain_areas"]
        assert len(domains) >= 2


class TestContentAwareClassification:
    def test_classify_by_content(self, tmp_path):
        md_file = tmp_path / "test_doc.md"
        md_file.write_text("# Strategy Document\n\nOur strategy for Q1 is to focus on retention.")
        result = classify_file_content_aware(md_file, tmp_path)
        assert "classification" in result
        assert "confidence" in result

    def test_fallback_on_empty(self, tmp_path):
        img_file = tmp_path / "screenshot.png"
        img_file.write_text("")
        result = classify_file_content_aware(img_file, tmp_path)
        assert result["classification"] == "visual_asset"
