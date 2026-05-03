from conftest import assert_v10_skill_contract


def test_v10_weak_signal_detection_contract(root_dir):
    assert_v10_skill_contract(root_dir, "weak_signal_detection", "tests/test_v10_weak_signal_detection.py")
