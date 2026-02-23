#!/usr/bin/env python3
"""Phase 3 integration preflight checks (no live API calls)."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from empire.services.secret_store import get_secret
from empire.services.storage import ensure_schema
from empire.services.normalization_service import normalize_payload


def _ok(name: str, detail: str) -> Dict[str, str]:
    return {"check": name, "status": "PASS", "detail": detail}


def _warn(name: str, detail: str) -> Dict[str, str]:
    return {"check": name, "status": "WARN", "detail": detail}


def _fail(name: str, detail: str) -> Dict[str, str]:
    return {"check": name, "status": "FAIL", "detail": detail}


def _check_import(module_name: str) -> Dict[str, str]:
    try:
        importlib.import_module(module_name)
        return _ok(f"import:{module_name}", "module import succeeded")
    except Exception as exc:
        return _fail(f"import:{module_name}", f"{type(exc).__name__}: {exc}")


def _check_path(label: str, path_value: Optional[str]) -> Dict[str, str]:
    if not path_value:
        return _warn(label, "not configured")
    p = Path(path_value)
    if p.exists():
        return _ok(label, f"exists at {p}")
    return _fail(label, f"configured but missing: {p}")


def _check_db(db_path: Path) -> Dict[str, str]:
    try:
        ensure_schema(db_path)
        return _ok("db:schema", f"schema ensured at {db_path}")
    except Exception as exc:
        return _fail("db:schema", f"{type(exc).__name__}: {exc}")


def _check_normalization(source: str, raw: Dict[str, object]) -> Dict[str, str]:
    try:
        record = normalize_payload(source, raw)
        if record.name or record.email or record.organization:
            return _ok(f"normalize:{source}", f"record_id={record.record_id}")
        return _fail(f"normalize:{source}", "normalized record empty")
    except Exception as exc:
        return _fail(f"normalize:{source}", f"{type(exc).__name__}: {exc}")


def _status_counts(results: List[Dict[str, str]]) -> Dict[str, int]:
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for item in results:
        counts[item["status"]] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Empire integration preflight (no live data)")
    parser.add_argument(
        "--integrations",
        default="hubspot,gmail,places",
        help="Comma-separated integrations to validate",
    )
    parser.add_argument("--db", default="data/empire.db", help="SQLite DB path")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on WARN in addition to FAIL")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    selected = {name.strip().lower() for name in args.integrations.split(",") if name.strip()}
    db_path = Path(args.db)
    results: List[Dict[str, str]] = []

    results.append(_check_db(db_path))

    if "hubspot" in selected:
        results.append(_check_import("empire.integrations.hubspot"))
        token = get_secret("hubspot_private_app_token")
        results.append(_ok("hubspot:token", "configured") if token else _warn("hubspot:token", "missing secret hubspot_private_app_token"))
        results.append(
            _check_normalization(
                "hubspot",
                {"name": "Phase3 HubSpot", "email": "phase3-hubspot@example.com", "company": "Empire QA", "title": "QA"},
            )
        )

    if "gmail" in selected:
        results.append(_check_import("empire.integrations.google_gmail"))
        cred_path = get_secret("google_gmail_credentials_path")
        token_path = get_secret("google_gmail_token_path")
        results.append(_check_path("gmail:credentials_path", cred_path))
        results.append(_check_path("gmail:token_path", token_path))
        results.append(
            _check_normalization(
                "gmail",
                {"name": "Phase3 Gmail", "email": "phase3-gmail@example.com", "company": "Empire QA"},
            )
        )

    if "places" in selected:
        results.append(_check_import("empire.integrations.google_places"))
        api_key = get_secret("google_places_api_key")
        results.append(_ok("places:api_key", "configured") if api_key else _warn("places:api_key", "missing secret google_places_api_key"))
        results.append(
            _check_normalization(
                "google_places",
                {"name": "Phase3 Places", "company": "Empire QA", "phone": "+1-555-0109"},
            )
        )

    counts = _status_counts(results)
    if args.json:
        print(json.dumps({"results": results, "counts": counts}, indent=2))
    else:
        for item in results:
            print(f"{item['status']} {item['check']} :: {item['detail']}")
        print(f"SUMMARY PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")

    if counts["FAIL"] > 0:
        return 1
    if args.strict and counts["WARN"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
