"""Configuration and project path helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
RAW_DATA_ROOT = DATA_ROOT / "raw"
INTERIM_DATA_ROOT = DATA_ROOT / "interim"
PROCESSED_DATA_ROOT = DATA_ROOT / "processed"
MODEL_ROOT = PROJECT_ROOT / "models"
CONFIG_ROOT = PROJECT_ROOT / "configs"


def ensure_project_directories() -> None:
    for path in (RAW_DATA_ROOT, INTERIM_DATA_ROOT, PROCESSED_DATA_ROOT, MODEL_ROOT, CONFIG_ROOT):
        path.mkdir(parents=True, exist_ok=True)


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
