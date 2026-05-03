from conftest import assert_v10_skill_contract


def test_v10_empathy_map_generation_contract(root_dir):
    assert_v10_skill_contract(root_dir, "empathy_map_generation", "tests/test_v10_empathy_map.py")
