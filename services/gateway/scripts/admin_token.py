#!/usr/bin/env python3
from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

TOKEN_ENV_VAR = "ADMIN_API_TOKEN"
DEFAULT_TOKEN_FILE = Path(__file__).resolve().parents[1] / ".admin_token"
TOKEN_FILE = Path(os.getenv("ADMIN_TOKEN_FILE", str(DEFAULT_TOKEN_FILE)))


def generate_admin_token() -> str:
    return secrets.token_urlsafe(32)


def ensure_admin_token() -> str:
    token = os.getenv(TOKEN_ENV_VAR)
    if token:
        print("[admin-token] Using ADMIN_API_TOKEN from environment.", file=sys.stderr)
        return token

    token = generate_admin_token()
    os.environ[TOKEN_ENV_VAR] = token

    try:
        TOKEN_FILE.write_text(token, encoding="utf-8")
        print(f"[admin-token] Stored token in {TOKEN_FILE}", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"[admin-token] Failed to write token file: {exc}", file=sys.stderr)

    print(f"[admin-token] Generated ADMIN_API_TOKEN: {token}", file=sys.stderr)
    return token


if __name__ == "__main__":
    sys.stdout.write(ensure_admin_token())

