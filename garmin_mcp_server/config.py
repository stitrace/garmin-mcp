"""Configuration loaded from environment variables / .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load a .env file from the current working directory if present. This never
# overrides variables already set in the real environment.
load_dotenv(override=False)

DEFAULT_TOKENSTORE = "~/.garminconnect"


def _expand(path: str) -> str:
    return str(Path(os.path.expanduser(path)))


@dataclass(frozen=True)
class GarminConfig:
    """Runtime configuration for the Garmin client."""

    email: str | None
    password: str | None
    tokenstore: str
    is_cn: bool

    @classmethod
    def from_env(cls) -> GarminConfig:
        # Accept both GARMINTOKENS (garminconnect convention) and
        # GARMIN_TOKEN_DIR (used by some sibling projects) for convenience.
        tokenstore = (
            os.getenv("GARMINTOKENS")
            or os.getenv("GARMIN_TOKEN_DIR")
            or DEFAULT_TOKENSTORE
        )
        is_cn = os.getenv("GARMIN_IS_CN", "false").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        return cls(
            email=os.getenv("GARMIN_EMAIL") or None,
            password=os.getenv("GARMIN_PASSWORD") or None,
            tokenstore=_expand(tokenstore),
            is_cn=is_cn,
        )

    @property
    def has_credentials(self) -> bool:
        return bool(self.email and self.password)
