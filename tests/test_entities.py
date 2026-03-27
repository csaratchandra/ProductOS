from pathlib import Path

from conftest import load_json
from jsonschema import Draft202012Validator


ENTITY_SCHEMA_EXAMPLE_MAP = {
    "artifact.schema.json": "artifact.example.json",
    "customer.schema.json": "customer.example.json",
    "decision.schema.json": "decision.example.json",
    "experiment.schema.json": "experiment.example.json",
    "feature.schema.json": "feature.example.json",
    "hypothesis.schema.json": "hypothesis.example.json",
    "market.schema.json": "market.example.json",
    "metric.schema.json": "metric.example.json",
    "opportunity.schema.json": "opportunity.example.json",
    "outcome.schema.json": "outcome.example.json",
    "persona.schema.json": "persona.example.json",
    "portfolio.schema.json": "portfolio.example.json",
    "problem.schema.json": "problem.example.json",
    "prototype.schema.json": "prototype.example.json",
    "release.schema.json": "release.example.json",
    "requirement.schema.json": "requirement.example.json",
    "segment.schema.json": "segment.example.json",
    "stakeholder.schema.json": "stakeholder.example.json",
    "support_issue.schema.json": "support_issue.example.json",
    "user_story.schema.json": "user_story.example.json",
    "workflow.schema.json": "workflow.example.json",
}


def test_entity_examples_match_entity_schemas(entity_schema_dir: Path, entity_example_dir: Path):
    for schema_name, example_name in ENTITY_SCHEMA_EXAMPLE_MAP.items():
        schema = load_json(entity_schema_dir / schema_name)
        example = load_json(entity_example_dir / example_name)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(example), key=lambda item: list(item.path))
        assert not errors, f"{example_name} failed {schema_name}: {[error.message for error in errors]}"
