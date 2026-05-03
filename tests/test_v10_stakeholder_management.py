from conftest import assert_v10_skill_contract


def test_v10_stakeholder_management_contract(root_dir):
    assert_v10_skill_contract(root_dir, "stakeholder_management", "tests/test_v10_stakeholder_management.py")
