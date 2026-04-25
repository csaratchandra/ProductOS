from pathlib import Path
import re


STANDARD_CONTRACT_HEADERS = [
    "Purpose",
    "Core responsibilities",
    "Inputs",
    "Outputs",
    "Required schemas",
    "Escalation rules",
    "Validation expectations",
]

PRESENTATION_CONTRACT_NAMES = [
    "editor",
    "presentation",
    "publisher",
    "storyteller",
    "visual-design",
]

CORRIDOR_CONTRACT_NAMES = [
    "workflow-corridor",
    "workflow-corridor-publisher",
]

PRESENTATION_EXAMPLE_NAMES = [
    "presentation_brief.example.json",
    "evidence_pack.example.json",
    "presentation_story.example.json",
    "render_spec.example.json",
    "publish_check.example.json",
    "ppt_export_plan.example.json",
]

VISUAL_SKILL_NAMES = [
    "visual_message_hierarchy",
    "visual_pattern_selection",
    "visual_composition_planning",
    "visual_publish_safety",
    "dual_target_fidelity",
    "visual_regression_review",
    "workflow_corridor_design",
]


def test_all_agent_contracts_follow_standard_section_order(root_dir: Path):
    for contract_path in sorted((root_dir / "core" / "agents").glob("*/CONTRACT.md")):
        text = contract_path.read_text(encoding="utf-8")
        headers = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
        assert headers == STANDARD_CONTRACT_HEADERS, f"{contract_path} has inconsistent section order: {headers}"


def test_presentation_component_contracts_are_exposed_through_core_symlinks(root_dir: Path):
    for contract_name in PRESENTATION_CONTRACT_NAMES:
        core_contract = root_dir / "core" / "agents" / contract_name / "CONTRACT.md"
        component_contract = root_dir / "components" / "presentation" / "contracts" / contract_name / "CONTRACT.md"
        assert core_contract.is_symlink(), f"{core_contract} should stay a symlink to the component-owned contract"
        assert core_contract.resolve() == component_contract.resolve()


def test_presentation_system_doc_is_exposed_through_core_symlink(root_dir: Path):
    core_doc = root_dir / "core" / "docs" / "presentation-system.md"
    component_doc = root_dir / "components" / "presentation" / "docs" / "presentation-system.md"
    assert core_doc.is_symlink(), f"{core_doc} should stay a symlink to the component-owned doc"
    assert core_doc.resolve() == component_doc.resolve()


def test_workflow_corridor_contracts_are_exposed_through_core_symlinks(root_dir: Path):
    for contract_name in CORRIDOR_CONTRACT_NAMES:
        core_contract = root_dir / "core" / "agents" / contract_name / "CONTRACT.md"
        component_contract = root_dir / "components" / "workflow_corridor" / "contracts" / contract_name / "CONTRACT.md"
        assert core_contract.is_symlink(), f"{core_contract} should stay a symlink to the component-owned contract"
        assert core_contract.resolve() == component_contract.resolve()


def test_core_presentation_examples_match_component_examples(root_dir: Path):
    core_examples = root_dir / "core" / "examples" / "artifacts"
    component_examples = root_dir / "components" / "presentation" / "examples" / "artifacts"

    for example_name in PRESENTATION_EXAMPLE_NAMES:
        core_example = core_examples / example_name
        component_example = component_examples / example_name
        assert core_example.exists(), f"Missing core presentation example mirror: {core_example}"
        assert component_example.exists(), f"Missing component presentation example: {component_example}"
        assert core_example.read_text(encoding="utf-8") == component_example.read_text(
            encoding="utf-8"
        ), f"Presentation example drift detected for {example_name}"


def test_presentation_docs_reference_current_adapter_surface(root_dir: Path):
    readme = (root_dir / "components" / "presentation" / "README.md").read_text(encoding="utf-8")
    system_doc = (root_dir / "components" / "presentation" / "docs" / "presentation-system.md").read_text(
        encoding="utf-8"
    )

    for text in [readme, system_doc]:
        assert "scripts/export_presentation.py" in text
        assert "scripts/presentation_export_pptx.mjs" in text

    assert "scripts/productos/runner.py" not in readme
    assert "scripts/productos/transforms.py" not in readme


def test_visual_skills_are_listed_and_present(root_dir: Path):
    skills_readme = (root_dir / "core" / "skills" / "README.md").read_text(encoding="utf-8")

    for skill_name in VISUAL_SKILL_NAMES:
        skill_path = root_dir / "core" / "skills" / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing visual skill: {skill_path}"
        assert skill_name in skills_readme


def test_visual_docs_reference_canonical_visual_cli(root_dir: Path):
    readme = (root_dir / "README.md").read_text(encoding="utf-8")
    visual_boundaries = (root_dir / "core" / "docs" / "visual-system-boundaries.md").read_text(encoding="utf-8")
    presentation_readme = (root_dir / "components" / "presentation" / "README.md").read_text(encoding="utf-8")
    corridor_readme = (root_dir / "components" / "workflow_corridor" / "README.md").read_text(encoding="utf-8")

    for text in [readme, visual_boundaries]:
        assert "./productos visual export deck" in text
        assert "./productos visual export corridor" in text
        assert "./productos visual export map" in text

    assert "./productos visual export deck" in presentation_readme
    assert "./productos visual export corridor" in corridor_readme
