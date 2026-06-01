"""One-time interactive login that caches Garmin OAuth/DI tokens.

Run this once (it supports multi-factor authentication). The MCP server then
authenticates using the cached tokens — no password is needed at runtime.

    garmin-mcp-server-login
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

from garminconnect import Garmin, GarminConnectAuthenticationError

from .config import GarminConfig


def _prompt(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (default or "")


def main() -> int:
    cfg = GarminConfig.from_env()

    print("Garmin Connect — interactive login")
    print("-" * 40)

    email = cfg.email or _prompt("Email")
    if not email:
        print("Email is required.", file=sys.stderr)
        return 2
    password = cfg.password or getpass.getpass("Password: ")
    if not password:
        print("Password is required.", file=sys.stderr)
        return 2

    tokenstore = cfg.tokenstore
    Path(tokenstore).mkdir(parents=True, exist_ok=True)

    try:
        # Passing a prompt_mfa callback + tokenstore lets garminconnect handle the
        # whole flow: prompt for an MFA code if required and persist the resulting
        # tokens to `tokenstore` so future runs never need the password again.
        garmin = Garmin(
            email=email,
            password=password,
            is_cn=cfg.is_cn,
            prompt_mfa=lambda: _prompt("MFA / 2FA code"),
        )
        garmin.login(tokenstore)
    except GarminConnectAuthenticationError as exc:
        print(f"\nAuthentication failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - interactive/network edge
        print(f"\nLogin error: {exc}", file=sys.stderr)
        return 1

    try:
        name = garmin.get_full_name()
    except Exception:
        name = email

    print("-" * 40)
    print(f"Success! Logged in as: {name}")
    print(f"Tokens cached to: {tokenstore}")
    print("\nYou can now start the MCP server with `garmin-mcp-server`.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
