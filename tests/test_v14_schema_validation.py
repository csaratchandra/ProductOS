"""Schema validation suite for V14 artifact schemas.

Validates every V14 schema against example fixtures,
required field constraints, type definitions, and edge cases.
"""

import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, Draft202012Validator

from conftest import load_json, SCHEMA_DIR


V14_SCHEMAS = [
    "intent_decomposition.schema.json",
    "product_architecture.schema.json",
    "consistency_report.schema.json",
    "gap_analysis.schema.json",
    "simulation_forecast.schema.json",
    "what_if_scenario.schema.json",
    "domain_activation.schema.json",
    "enrichment_report.schema.json",
    "compliance_report.schema.json",
    "pm_briefing.schema.json",
    "analytics_plan.schema.json",
    "ai_layer_plan.schema.json",
    "outcome_cascade.schema.json",
    "market_simulation_result.schema.json",
    "experience_plan.schema.json",
]

REQUIRED_V14_SCHEMAS = [
    "intent_decomposition.schema.json",
    "product_architecture.schema.json",
    "consistency_report.schema.json",
    "gap_analysis.schema.json",
    "simulation_forecast.schema.json",
    "what_if_scenario.schema.json",
    "domain_activation.schema.json",
    "enrichment_report.schema.json",
    "compliance_report.schema.json",
    "pm_briefing.schema.json",
]


class TestV14SchemaExistence:
    """All V14 plan schemas must exist on disk."""

    def test_all_required_v14_schemas_exist(self):
        for name in REQUIRED_V14_SCHEMAS:
            path = SCHEMA_DIR / name
            assert path.exists(), f"Missing required V14 schema: {path}"

    def test_all_v14_schemas_are_valid_json(self):
        for name in V14_SCHEMAS:
            path = SCHEMA_DIR / name
            if not path.exists():
                continue
            try:
                load_json(path)
            except json.JSONDecodeError as exc:
                pytest.fail(f"{name} is not valid JSON: {exc}")


class TestV14SchemaStructure:
    """V14 schemas must follow ProductOS conventions."""

    @pytest.mark.parametrize("schema_name", V14_SCHEMAS)
    def test_schema_has_required_top_level_keys(self, schema_name):
        path = SCHEMA_DIR / schema_name
        if not path.exists():
            pytest.skip(f"{schema_name} not yet on disk")
        schema = load_json(path)
        for key in ("$schema", "$id", "title", "type", "properties"):
            assert key in schema, f"{schema_name} missing top-level key: {key}"

    @pytest.mark.parametrize("schema_name", V14_SCHEMAS)
    def test_schema_has_schema_version_const(self, schema_name):
        path = SCHEMA_DIR / schema_name
        if not path.exists():
            pytest.skip(f"{schema_name} not yet on disk")
        schema = load_json(path)
        sv = schema.get("properties", {}).get("schema_version", {})
        assert sv.get("const") == "1.0.0", f"{schema_name} schema_version must be const 1.0.0"

    @pytest.mark.parametrize("schema_name", V14_SCHEMAS)
    def test_schema_disallows_additional_properties(self, schema_name):
        path = SCHEMA_DIR / schema_name
        if not path.exists():
            pytest.skip(f"{schema_name} not yet on disk")
        schema = load_json(path)
        assert schema.get("additionalProperties") is False, f"{schema_name} must set additionalProperties: false"

    @pytest.mark.parametrize("schema_name", V14_SCHEMAS)
    def test_schema_compiles_validator(self, schema_name):
        path = SCHEMA_DIR / schema_name
        if not path.exists():
            pytest.skip(f"{schema_name} not yet on disk")
        schema = load_json(path)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            pytest.fail(f"{schema_name} failed schema compilation: {exc}")


class TestV14SchemaRequiredFields:
    """V14 schemas must have proper required field declarations."""

    @pytest.mark.parametrize("schema_name", V14_SCHEMAS)
    def test_required_fields_are_declared(self, schema_name):
        path = SCHEMA_DIR / schema_name
        if not path.exists():
            pytest.skip(f"{schema_name} not yet on disk")
        schema = load_json(path)
        required = schema.get("required", [])
        assert "schema_version" in required, f"{schema_name} must require schema_version"
        assert len(required) >= 2, f"{schema_name} must have at least 2 required fields"

    def test_intent_decomposition_required_fields(self):
        schema = load_json(SCHEMA_DIR / "intent_decomposition.schema.json")
        required = schema.get("required", [])
        for field in ("intent_decomposition_id", "raw_text", "extracted_problem", "inferred_personas", "domain_match", "confidence_scores"):
            assert field in required, f"intent_decomposition missing required field: {field}"

    def test_gap_analysis_required_fields(self):
        schema = load_json(SCHEMA_DIR / "gap_analysis.schema.json")
        required = schema.get("required", [])
        for field in ("gap_analysis_id", "gaps"):
            assert field in required, f"gap_analysis missing required field: {field}"


class TestV14SchemaEnumValues:
    """V14 schemas must use valid enum values where constrained."""

    def test_simulation_forecast_scenario_enum(self):
        schema = load_json(SCHEMA_DIR / "simulation_forecast.schema.json")
        scenario_prop = schema["properties"]["scenario"]
        assert set(scenario_prop["enum"]) == {"baseline", "optimistic", "pessimistic", "sensitivity"}

    def test_gap_severity_enum(self):
        schema = load_json(SCHEMA_DIR / "gap_analysis.schema.json")
        gap_def = schema["$defs"]["gap"]
        severity_prop = gap_def["properties"]["severity"]
        assert set(severity_prop["enum"]) == {"critical", "warning", "info"}

    def test_consistency_severity_enum(self):
        schema = load_json(SCHEMA_DIR / "consistency_report.schema.json")
        check_def = schema["$defs"]["checkFailure"]
        severity_prop = check_def["properties"]["severity"]
        assert set(severity_prop["enum"]).issuperset({"critical", "warning", "info"})


class TestV14SchemaEdgeCases:
    """V14 schemas must handle edge cases properly."""

    def test_empty_intent_decomposition_rejected(self):
        validator = Draft202012Validator(load_json(SCHEMA_DIR / "intent_decomposition.schema.json"))
        with pytest.raises(ValidationError):
            validator.validate({})

    def test_decomposition_without_raw_text_rejected(self):
        validator = Draft202012Validator(load_json(SCHEMA_DIR / "intent_decomposition.schema.json"))
        with pytest.raises(ValidationError):
            validator.validate({"schema_version": "1.0.0", "intent_decomposition_id": "test"})

    def test_gap_analysis_minimal_valid(self):
        validator = Draft202012Validator(load_json(SCHEMA_DIR / "gap_analysis.schema.json"))
        minimal = {
            "schema_version": "1.0.0",
            "gap_analysis_id": "ga_test",
            "architecture_ref": "pa_test",
            "gaps": [],
            "summary": {"total_gaps": 0, "critical_count": 0, "warning_count": 0, "info_count": 0},
            "created_at": "2026-05-14T00:00:00Z",
        }
        try:
            validator.validate(minimal)
        except ValidationError as exc:
            pytest.fail(f"Minimal gap_analysis should be valid: {exc}")

    def test_forecast_minimal_valid(self):
        validator = Draft202012Validator(load_json(SCHEMA_DIR / "simulation_forecast.schema.json"))
        minimal = {
            "schema_version": "1.0.0",
            "simulation_forecast_id": "sf_test",
            "architecture_ref": "pa_test",
            "scenario": "baseline",
            "baseline_forecast": {
                "p50_completion_seconds": 120.0,
                "p90_completion_seconds": 300.0,
                "p95_completion_seconds": 600.0,
                "total_handoffs": 3,
                "simulation_runs": 1000,
            },
            "created_at": "2026-05-14T00:00:00Z",
        }
        try:
            validator.validate(minimal)
        except ValidationError as exc:
            pytest.fail(f"Minimal simulation_forecast should be valid: {exc}")
