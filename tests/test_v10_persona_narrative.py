from conftest import assert_v10_skill_contract


def test_v10_persona_narrative_generation_contract(root_dir):
    assert_v10_skill_contract(root_dir, "persona_narrative_generation", "tests/test_v10_persona_narrative.py")
