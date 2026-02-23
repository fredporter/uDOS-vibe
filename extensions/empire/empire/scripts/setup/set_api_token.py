#!/usr/bin/env python3
"""Set Empire API token in the secret store."""

from __future__ import annotations

import argparse

from empire.services.secret_store import set_secret


def main() -> int:
    parser = argparse.ArgumentParser(description="Set Empire API token")
    parser.add_argument("--token", required=True, help="API token value")
    args = parser.parse_args()

    set_secret("empire_api_token", args.token)
    print("Empire API token saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
