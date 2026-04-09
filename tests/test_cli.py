from __future__ import annotations

from pathlib import Path

from src.cli import main


def test_cli_dry_run_does_not_create_summary(tmp_path: Path, monkeypatch) -> None:
    samples = Path(__file__).resolve().parents[1] / "data" / "samples"
    output = tmp_path / "summary.json"
    monkeypatch.chdir(tmp_path)
    exit_code = main(["--input-dir", str(samples), "--output", str(output), "--dry-run"])
    assert exit_code == 2
    assert not output.exists()
