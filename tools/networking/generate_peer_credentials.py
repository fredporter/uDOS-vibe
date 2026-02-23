#!/usr/bin/env python3
"""Generate peer Ed25519 signature + WireGuard keypair.

Outputs a JSON payload suitable for /api/networking/pairing/complete and
WireGuard peer registration.
"""

from __future__ import annotations

import argparse
import base64
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate peer credentials")
    parser.add_argument("--challenge", required=True, help="Pairing challenge string")
    parser.add_argument("--peer-name", default="peer-node", help="Peer display name")
    parser.add_argument("--pairing-token", default=None, help="Pairing token to include in payload")
    args = parser.parse_args()

    ed_private = Ed25519PrivateKey.generate()
    ed_public = ed_private.public_key()
    signature = ed_private.sign(args.challenge.encode("utf-8"))

    wg_private = X25519PrivateKey.generate()
    wg_public = wg_private.public_key()

    payload = {
        "peer_name": args.peer_name,
        "peer_public_key": _b64(ed_public.public_bytes_raw()),
        "peer_private_key": _b64(ed_private.private_bytes_raw()),
        "signature": _b64(signature),
        "wireguard": {
            "peer_public_key": _b64(wg_public.public_bytes_raw()),
            "peer_private_key": _b64(wg_private.private_bytes_raw()),
        },
    }

    if args.pairing_token:
        payload["pairing_complete_payload"] = {
            "pairing_token": args.pairing_token,
            "peer_name": args.peer_name,
            "peer_public_key": payload["peer_public_key"],
            "signature": payload["signature"],
        }

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
