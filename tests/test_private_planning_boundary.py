from __future__ import annotations

import subprocess
from pathlib import Path


DISALLOWED_PUBLIC_PLAN_FILENAMES = (
    "execution-plan",
    "release-plan",
    "scope-brief",
    "stop-ship",
    "superpower-plan",
)

DISALLOWED_PRIVATE_INTERNAL_REFS = (
    "internal/plans/",
    "internal/workspaces/",
    "internal/proof/",
    "internal/experiments/",
)


def test_core_docs_has_no_public_version_plan_files(root_dir: Path):
    docs_dir = root_dir / "core" / "docs"
    offending = [
        path.name
        for path in docs_dir.glob("*.md")
        if any(marker in path.name for marker in DISALLOWED_PUBLIC_PLAN_FILENAMES)
    ]
    assert offending == []


def test_repo_has_no_public_references_to_private_internal_paths(root_dir: Path):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    tracked_files = []
    for relative_path in result.stdout.splitlines():
        path = root_dir / relative_path
        if (
            path.is_file()
            and "internal" not in path.parts
            and path.suffix in {".md", ".json", ".py"}
            and path.name not in {"test_private_planning_boundary.py", "productos.py"}
        ):
            tracked_files.append(path)

    offending: list[str] = []
    for path in tracked_files:
        text = path.read_text(encoding="utf-8")
        for ref in DISALLOWED_PRIVATE_INTERNAL_REFS:
            if ref in text:
                offending.append(f"{path.relative_to(root_dir).as_posix()} -> {ref}")

    assert offending == []


def test_repo_has_no_tracked_internal_release_records(root_dir: Path):
    for relative_dir in [
        "core/mission-briefs",
        "registry/scorecards",
        "registry/workspaces",
        "registry/suites",
    ]:
        assert not (root_dir / relative_dir).exists()
