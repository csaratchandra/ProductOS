from scripts.audit_v10_superpower_plan import MANIFEST_PATH, build_audit_report


def test_v10_audit_uses_manifest_scope_by_default():
    report = build_audit_report(run_tests=False)

    assert report["summary"]["scope_source"] == "manifest"
    assert report["manifest"]["manifest_path"] == "core/docs/v10-superpower-manifest.json"
    assert report["release_state"]["target_version"] == "10.0.0"
    assert report["advisories"]["plan_sync"], "Expected stale prose-plan findings to be advisory in manifest mode."
    assert not report["findings"]["scope_manifest"], "Plan drift should not block when manifest mode is active."


def test_v10_audit_can_make_plan_sync_blocking():
    report = build_audit_report(run_tests=False, manifest_path=MANIFEST_PATH, strict_plan_sync=True)

    assert report["findings"]["scope_manifest"], "Strict plan sync should promote plan drift into blocking findings."
