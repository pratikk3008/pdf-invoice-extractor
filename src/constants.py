"""Shared application constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = PROJECT_ROOT / "config" / "extraction_rules.yaml"
DEFAULT_SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
DEFAULT_UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
APP_VERSION = "1.1.0"
