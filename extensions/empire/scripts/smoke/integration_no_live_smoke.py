#!/usr/bin/env python3
"""Run integration sync smoke tests with mocked providers (no live data)."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Dict, List

from empire.integrations import hubspot, google_gmail, google_places
from empire.services.storage import ensure_schema


def run_hubspot(db_path: Path) -> Dict[str, int]:
    original_fetch_contacts = hubspot.fetch_contacts
    original_fetch_companies = hubspot.fetch_companies
    try:
        hubspot.fetch_contacts = lambda **_: [  # type: ignore[assignment]
            {
                "id": "contact-1",
                "properties": {
                    "firstname": "Phase3",
                    "lastname": "HubSpot",
                    "email": "phase3-hubspot@example.com",
                    "phone": "+1-555-1001",
                    "jobtitle": "QA",
                    "company": "Empire QA",
                },
            }
        ]
        hubspot.fetch_companies = lambda **_: [  # type: ignore[assignment]
            {
                "id": "company-1",
                "properties": {
                    "name": "Empire QA",
                    "domain": "empire-qa.example",
                    "website": "https://empire-qa.example",
                    "phone": "+1-555-1002",
                },
            }
        ]
        counts = hubspot.sync_all(token="dummy", db_path=db_path, limit=5, max_pages=1)
        return counts
    finally:
        hubspot.fetch_contacts = original_fetch_contacts  # type: ignore[assignment]
        hubspot.fetch_companies = original_fetch_companies  # type: ignore[assignment]


def run_gmail(db_path: Path) -> int:
    original_resolve_paths = google_gmail._resolve_paths
    original_list_messages = google_gmail.list_messages
    original_get_message = google_gmail.get_message
    original_process_emails = google_gmail.process_emails
    try:
        google_gmail._resolve_paths = lambda *_args, **_kwargs: (Path("/tmp/cred.json"), Path("/tmp/token.json"))  # type: ignore[assignment]
        google_gmail.list_messages = lambda **_: [{"id": "msg-1"}, {"id": "msg-2"}]  # type: ignore[assignment]
        google_gmail.get_message = lambda **kwargs: {  # type: ignore[assignment]
            "subject": "Phase3 Gmail",
            "from": "Phase3 Gmail <phase3-gmail@example.com>",
            "date": "Sun, 15 Feb 2026 10:00:00 +0000",
            "body": "test",
            "message_id": f"<{kwargs.get('message_id')}>",
            "id": kwargs.get("message_id", ""),
        }
        google_gmail.process_emails = lambda *_args, **_kwargs: []  # type: ignore[assignment]
        return google_gmail.fetch_and_ingest(
            credentials_path=None,
            token_path=None,
            query="",
            max_results=10,
            db_path=db_path,
        )
    finally:
        google_gmail._resolve_paths = original_resolve_paths  # type: ignore[assignment]
        google_gmail.list_messages = original_list_messages  # type: ignore[assignment]
        google_gmail.get_message = original_get_message  # type: ignore[assignment]
        google_gmail.process_emails = original_process_emails  # type: ignore[assignment]


def run_places(db_path: Path) -> int:
    original_client = google_places.GooglePlacesClient

    class MockPlacesClient:
        def __init__(self, *, api_key: str):
            self.api_key = api_key

        def search(self, query: str, location: str = "", radius_meters: int = 5000) -> List[Dict[str, str]]:
            _ = (query, location, radius_meters)
            return [{"place_id": "place-1", "name": "Empire QA Place", "formatted_address": "1 Test St"}]

        def details(self, place_id: str) -> Dict[str, str]:
            _ = place_id
            return {
                "name": "Empire QA Place",
                "formatted_address": "1 Test St",
                "international_phone_number": "+1-555-1003",
                "website": "https://places-qa.example",
            }

    try:
        google_places.GooglePlacesClient = MockPlacesClient  # type: ignore[assignment]
        return google_places.search_and_ingest(
            api_key="dummy",
            query="qa",
            location="",
            radius_meters=1000,
            db_path=db_path,
        )
    finally:
        google_places.GooglePlacesClient = original_client  # type: ignore[assignment]


def main() -> int:
    parser = argparse.ArgumentParser(description="Integration no-live smoke")
    parser.add_argument("--db", default=None, help="Optional SQLite DB path")
    args = parser.parse_args()

    if args.db:
        db_path = Path(args.db)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = Path(tempfile.mkdtemp(prefix="empire-phase3-"))
        db_path = temp_dir / "integration-smoke.db"

    ensure_schema(db_path)

    hubspot_counts = run_hubspot(db_path)
    gmail_count = run_gmail(db_path)
    places_count = run_places(db_path)

    print(f"PASS hubspot contacts={hubspot_counts['contacts']} companies={hubspot_counts['companies']}")
    print(f"PASS gmail contacts={gmail_count}")
    print(f"PASS places records={places_count}")
    print(f"PASS db={db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
