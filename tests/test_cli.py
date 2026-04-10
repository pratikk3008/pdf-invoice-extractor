from __future__ import annotations

from pathlib import Path

from src.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
RULES_PATH = PROJECT_ROOT / "config" / "extraction_rules.yaml"


def test_cli_dry_run_does_not_create_summary(tmp_path: Path) -> None:
    output = tmp_path / "summary.json"
    exit_code = main(
        [
            "--input-dir",
            str(SAMPLES_DIR),
            "--rules",
            str(RULES_PATH),
            "--output",
            str(output),
            "--dry-run",
        ]
    )
    assert exit_code == 2
    assert not output.exists()
