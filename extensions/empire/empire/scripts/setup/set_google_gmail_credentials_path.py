#!/usr/bin/env python3
"""Store Gmail credentials.json path in the secret store."""

from __future__ import annotations

import argparse

from empire.services.secret_store import set_secret


def main() -> int:
    parser = argparse.ArgumentParser(description="Set Gmail credentials.json path")
    parser.add_argument("--path", required=True, help="Path to credentials.json")
    args = parser.parse_args()

    set_secret("google_gmail_credentials_path", args.path)
    print("Gmail credentials path saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
