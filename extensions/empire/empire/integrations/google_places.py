"""Google Places API integration for Empire."""

from __future__ import annotations

from typing import List, Dict, Optional

import requests
import time

from empire.services.normalization_service import normalize_payload
from empire.services.storage import DEFAULT_DB_PATH, record_event, record_source, upsert_record
from empire.services.secret_store import get_secret
from empire.services.ingestion_service import _utc_now


PLACES_TEXT_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS = "https://maps.googleapis.com/maps/api/place/details/json"


class GooglePlacesClient:
    """Google Places API client."""

    def __init__(self, *, api_key: str):
        self.api_key = api_key

    def search(
        self,
        query: str,
        location: str = "",
        radius_meters: int = 5000,
    ) -> List[Dict[str, str]]:
        params = {"query": query, "key": self.api_key}
        if location:
            params["location"] = location
            params["radius"] = radius_meters

        results: List[Dict[str, str]] = []
        page_token = None
        for _ in range(3):
            if page_token:
                params["pagetoken"] = page_token
                time.sleep(2.0)  # Google requires short delay before pagetoken is valid
            resp = _request_with_retry(PLACES_TEXT_SEARCH, params)
            data = resp.json()
            results.extend(data.get("results", []))
            page_token = data.get("next_page_token")
            if not page_token:
                break
        return results

    def details(self, place_id: str) -> Dict[str, str]:
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,international_phone_number,website",
            "key": self.api_key,
        }
        resp = _request_with_retry(PLACES_DETAILS, params)
        data = resp.json()
        return data.get("result", {})


def _request_with_retry(url: str, params: Dict[str, str], retries: int = 3) -> requests.Response:
    delay = 1.0
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def search_and_ingest(
    *,
    api_key: Optional[str],
    query: str,
    location: str = "",
    radius_meters: int = 5000,
    db_path: Optional[str] = None,
) -> int:
    resolved_key = api_key or get_secret("google_places_api_key")
    if not resolved_key:
        raise ValueError("Missing Google Places API key")
    client = GooglePlacesClient(api_key=resolved_key)
    record_source("google_places", label="Google Places", created_at=None, db_path=db_path or DEFAULT_DB_PATH)
    results = client.search(query=query, location=location, radius_meters=radius_meters)
    count = 0
    for result in results:
        place_id = result.get("place_id")
        details = client.details(place_id) if place_id else {}
        raw = {
            "name": details.get("name") or result.get("name"),
            "company": details.get("name") or result.get("name"),
            "phone": details.get("international_phone_number"),
            "address": details.get("formatted_address") or result.get("formatted_address"),
            "website": details.get("website"),
        }
        record = normalize_payload("google_places", raw)
        if record.name or record.organization:
            upsert_record(record, db_path=db_path or DEFAULT_DB_PATH)
            count += 1
    record_event(
        record_id=None,
        event_type="places.fetch",
        occurred_at=_utc_now(),
        subject=f"Places fetched {count} records",
        notes=query,
        db_path=db_path or DEFAULT_DB_PATH,
    )
    return count
