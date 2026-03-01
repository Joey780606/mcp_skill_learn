"""Generic JSON config loader with basic validation."""
import json
import os
from pathlib import Path


class ConfigError(ValueError):
    pass


# Project root: three levels up from this file (app/config/loader.py → project root)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_project_root() -> str:
    return _PROJECT_ROOT


def load_json_config(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")
    with open(p, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in {path}: {e}") from e
