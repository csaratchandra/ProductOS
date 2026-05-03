from pathlib import Path
import json
import re


STANDARD_SKILL_HEADERS_V9 = [
    "Purpose",
    "Trigger / When To Use",
    "Inputs",
    "Outputs",
    "Guardrails",
    "Execution Pattern",
    "Validation Expectations",
]

STANDARD_SKILL_HEADERS_V10 = [
    "1. Purpose",
    "2. Trigger / When To Use",
    "3. Prerequisites",
    "4. Input Specification",
    "5. Execution Steps",
    "6. Output Specification",
    "7. Guardrails",
    "8. Gold Standard Checklist",
    "9. Examples",
    "10. Cross-References",
    "11. Maturity Band Variations",
    "12. Validation Criteria",
]

REQUIRED_CORE_SKILLS = [
    "source_discovery",
    "source_normalization",
    "source_ranking",
    "freshness_scoring",
    "contradiction_detection",
    "evidence_extraction",
    "retrieval_selection",
    "strategy_refresh",
    "decision_packet_synthesis",
    "publish_safe_summarization",
]

def test_all_core_skills_follow_standard_section_order(root_dir: Path):
    for skill_path in sorted((root_dir / "core" / "skills").glob("*/SKILL.md")):
        if skill_path.name == "SKILL_CONTRACT_TEMPLATE.md":
            continue
        text = skill_path.read_text(encoding="utf-8")
        headers = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
        is_v9 = headers == STANDARD_SKILL_HEADERS_V9
        is_v10 = headers == STANDARD_SKILL_HEADERS_V10
        assert is_v9 or is_v10, (
            f"{skill_path} follows neither V9 nor V10 section order.\n"
            f"Expected V9: {STANDARD_SKILL_HEADERS_V9}\n"
            f"Expected V10: {STANDARD_SKILL_HEADERS_V10}\n"
            f"Got: {headers}"
        )


def test_required_core_skills_exist(root_dir: Path):
    for skill_name in REQUIRED_CORE_SKILLS:
        skill_path = root_dir / "core" / "skills" / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing required core skill: {skill_path}"


def test_persona_profile_skill_refs_resolve_to_core_skills(root_dir: Path):
    payload = json.loads((root_dir / "core" / "examples" / "artifacts" / "persona_operating_profile.example.json").read_text(encoding="utf-8"))
    skill_refs = {
        skill_ref
        for profile in payload["profiles"]
        for skill_ref in profile["skill_refs"]
    }
    assert skill_refs, "persona_operating_profile.example.json should reference at least one skill"
    for skill_ref in sorted(skill_refs):
        resolved = root_dir / skill_ref
        assert resolved.exists(), f"Missing skill referenced by persona profile: {skill_ref}"


def test_required_core_skills_are_used_by_persona_profiles(root_dir: Path):
    payload = json.loads((root_dir / "core" / "examples" / "artifacts" / "persona_operating_profile.example.json").read_text(encoding="utf-8"))
    referenced_skill_names = {
        Path(skill_ref).parts[-2]
        for profile in payload["profiles"]
        for skill_ref in profile["skill_refs"]
    }
    for skill_name in REQUIRED_CORE_SKILLS:
        assert skill_name in referenced_skill_names, f"{skill_name} should be referenced by at least one persona profile"
