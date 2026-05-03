from conftest import assert_v10_skill_contract


def test_v10_pestle_synthesis_contract(root_dir):
    assert_v10_skill_contract(root_dir, "pestle_synthesis", "tests/test_v10_pestle_synthesis.py")
