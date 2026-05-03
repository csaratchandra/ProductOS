from conftest import assert_v10_skill_contract


def test_v10_decision_tree_construction_contract(root_dir):
    assert_v10_skill_contract(root_dir, "decision_tree_construction", "tests/test_v10_decision_tree_construction.py")
