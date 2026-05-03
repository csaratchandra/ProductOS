from conftest import assert_v10_skill_contract


def test_v10_persona_evidence_synthesis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "persona_evidence_synthesis", "tests/test_v10_persona_synthesis.py")
