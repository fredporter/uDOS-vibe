#!/usr/bin/env python3
"""Set Google Places API key in Empire secret store."""

from __future__ import annotations

import argparse

from empire.services.secret_store import set_secret


def main() -> int:
    parser = argparse.ArgumentParser(description="Set Google Places API key")
    parser.add_argument("--api-key", required=True, help="Google Places API key value")
    args = parser.parse_args()

    set_secret("google_places_api_key", args.api_key)
    print("Google Places API key saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
