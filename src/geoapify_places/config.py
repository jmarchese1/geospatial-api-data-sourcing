"""Central configuration helpers for the Geoapify Places integration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_BASE_URL = "https://api.geoapify.com/v2/places"
API_KEY_ENV_VAR = "GEOAPIFY_API_KEY"
DEFAULT_ENV_FILE = Path(".env")


@dataclass(frozen=True)
class GeoapifySettings:
    """Holds configuration that higher-level clients rely on."""

    api_key: str
    base_url: str = DEFAULT_BASE_URL


def load_settings(env_file: Optional[Path] = DEFAULT_ENV_FILE) -> GeoapifySettings:
    """
    Load settings for connecting to Geoapify Places.

    The helper optionally parses a local .env file (only if it exists) to
    populate the expected environment variables, then validates that the API
    key is present.
    """

    _load_env_file(env_file)

    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        raise RuntimeError(
            f"{API_KEY_ENV_VAR} is not set. "
            "Create a .env file (copy .env.example) or export the variable."
        )

    return GeoapifySettings(api_key=api_key.strip())


def _load_env_file(env_file: Optional[Path]) -> None:
    """Rudimentary .env parsing to avoid extra dependencies in phase 1."""

    if not env_file:
        return

    path = Path(env_file)
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue
        key, value = cleaned.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


__all__ = ["GeoapifySettings", "load_settings", "DEFAULT_BASE_URL", "API_KEY_ENV_VAR"]

