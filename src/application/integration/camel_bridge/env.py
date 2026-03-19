"""Environment helpers for CAMEL.Bridge."""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(env_path: str | None = None, override: bool = False) -> str | None:
    candidates = [Path(env_path)] if env_path else [Path.cwd() / ".env", Path(__file__).resolve().parents[4] / ".env"]
    for candidate in candidates:
        if not candidate.exists() or not candidate.is_file():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and (override or key not in os.environ):
                os.environ[key] = value
        return str(candidate)
    return None


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
