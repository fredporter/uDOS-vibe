#!/usr/bin/env python3
"""Set HubSpot token in Empire secret store."""

from __future__ import annotations

import argparse

from empire.services.secret_store import set_secret


def main() -> int:
    parser = argparse.ArgumentParser(description="Set HubSpot private app token")
    parser.add_argument("--token", required=True, help="HubSpot token value")
    args = parser.parse_args()

    set_secret("hubspot_private_app_token", args.token)
    print("HubSpot token saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
