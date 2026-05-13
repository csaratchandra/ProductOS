from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HEALTHCARE_INTENT = (
    "A HIPAA-compliant prior authorization platform for US providers and payers "
    "with AI-assisted review"
)


def _run_cli(root_dir: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/productos.py", *args],
        cwd=root_dir,
        capture_output=True,
        text=True,
        input=input_text,
        check=False,
    )


def test_architect_dry_run_exits_after_decomposition(root_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "architect-dry-run"
    result = _run_cli(
        root_dir,
        "architect",
        "--intent",
        HEALTHCARE_INTENT,
        "--dry-run",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Dry-run complete." in result.stdout
    assert not (output_dir / "master_prd.json").exists()


def test_architect_wizard_generates_outputs(root_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "architect-wizard"
    result = _run_cli(
        root_dir,
        "architect",
        "--intent",
        HEALTHCARE_INTENT,
        "--wizard",
        "--output-dir",
        str(output_dir),
        input_text="y\ny\n",
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Wizard Checkpoint 1" in result.stdout
    assert "Wizard Checkpoint 2" in result.stdout
    assert (output_dir / "pm_briefing.md").exists()
    assert (output_dir / "executive_summary_pdf.pdf").exists()
    assert (output_dir / "compliance_report.json").exists()
    assert (output_dir / "executive_summary_pdf.pdf").read_text(encoding="utf-8").startswith("%PDF-1.4")


def test_architect_auto_generates_enriched_bundle(root_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "architect-auto"
    result = _run_cli(
        root_dir,
        "architect",
        "--intent",
        HEALTHCARE_INTENT,
        "--auto",
        "--output-dir",
        str(output_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Architecture complete" in result.stdout
    assert (output_dir / "product_architecture.json").exists()
    assert (output_dir / "enrichment_report.json").exists()
    assert (output_dir / "compliance_report.json").exists()
