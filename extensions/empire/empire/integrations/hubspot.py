"""HubSpot CRM integration for Empire."""

from __future__ import annotations

import time
from typing import Dict, List, Optional

import requests

from empire.services.normalization_service import normalize_payload
from empire.services.secret_store import get_secret
from empire.services.storage import DEFAULT_DB_PATH, record_event, record_source, upsert_record
from empire.services.ingestion_service import _utc_now


HUBSPOT_CONTACTS = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_COMPANIES = "https://api.hubapi.com/crm/v3/objects/companies"
HUBSPOT_CONTACTS_SEARCH = "https://api.hubapi.com/crm/v3/objects/contacts/search"
HUBSPOT_COMPANIES_SEARCH = "https://api.hubapi.com/crm/v3/objects/companies/search"


DEFAULT_CONTACT_PROPERTIES = [
    "email",
    "firstname",
    "lastname",
    "phone",
    "mobilephone",
    "jobtitle",
    "company",
    "website",
    "address",
    "city",
    "state",
    "zip",
    "country",
    "lifecyclestage",
]

DEFAULT_COMPANY_PROPERTIES = [
    "name",
    "domain",
    "website",
    "phone",
    "address",
    "city",
    "state",
    "zip",
    "country",
    "industry",
    "annualrevenue",
    "numberofemployees",
    "hubspot_owner_id",
]


def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _request_with_retry(url: str, params: Dict[str, str], token: str, retries: int = 3) -> requests.Response:
    delay = 1.0
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=_headers(token), timeout=15)
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def _post_with_retry(url: str, payload: Dict, token: str, retries: int = 3, method: str = "POST") -> requests.Response:
    delay = 1.0
    for attempt in range(retries):
        try:
            if method == "PATCH":
                resp = requests.patch(url, json=payload, headers=_headers(token), timeout=15)
            else:
                resp = requests.post(url, json=payload, headers=_headers(token), timeout=15)
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def fetch_contacts(
    *,
    token: Optional[str],
    limit: int = 100,
    max_pages: int = 5,
    properties: Optional[List[str]] = None,
) -> List[Dict]:
    resolved_token = token or get_secret("hubspot_private_app_token")
    if not resolved_token:
        raise ValueError("Missing HubSpot token")

    props = properties or DEFAULT_CONTACT_PROPERTIES
    results: List[Dict] = []
    after: Optional[str] = None
    for _ in range(max_pages):
        params = {"limit": str(limit), "properties": ",".join(props)}
        if after:
            params["after"] = after
        resp = _request_with_retry(HUBSPOT_CONTACTS, params, resolved_token)
        data = resp.json()
        batch = data.get("results", [])
        results.extend(batch)
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.2)
    return results


def fetch_companies(
    *,
    token: Optional[str],
    limit: int = 100,
    max_pages: int = 5,
    properties: Optional[List[str]] = None,
) -> List[Dict]:
    resolved_token = token or get_secret("hubspot_private_app_token")
    if not resolved_token:
        raise ValueError("Missing HubSpot token")

    props = properties or DEFAULT_COMPANY_PROPERTIES
    results: List[Dict] = []
    after: Optional[str] = None
    for _ in range(max_pages):
        params = {"limit": str(limit), "properties": ",".join(props)}
        if after:
            params["after"] = after
        resp = _request_with_retry(HUBSPOT_COMPANIES, params, resolved_token)
        data = resp.json()
        batch = data.get("results", [])
        results.extend(batch)
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.2)
    return results


def sync_contacts(
    *,
    token: Optional[str],
    db_path=DEFAULT_DB_PATH,
    limit: int = 100,
    max_pages: int = 5,
) -> int:
    contacts = fetch_contacts(token=token, limit=limit, max_pages=max_pages)
    record_source("hubspot", label="HubSpot", created_at=None, db_path=db_path)
    count = 0
    for item in contacts:
        props = item.get("properties", {})
        raw = {
            "name": f"{props.get('firstname','')} {props.get('lastname','')}".strip(),
            "email": props.get("email"),
            "phone": props.get("phone") or props.get("mobilephone"),
            "title": props.get("jobtitle"),
            "company": props.get("company"),
            "address": props.get("address"),
            "city": props.get("city"),
            "state": props.get("state"),
            "zip": props.get("zip"),
            "country": props.get("country"),
            "website": props.get("website"),
        }
        record = normalize_payload("hubspot", raw)
        if record.email or record.name:
            upsert_record(record, db_path=db_path)
            count += 1
    record_event(
        record_id=None,
        event_type="hubspot.sync",
        occurred_at=_utc_now(),
        subject=f"HubSpot synced {count} contacts",
        notes=f"limit={limit} pages={max_pages}",
        db_path=db_path,
    )
    return count


def sync_companies(
    *,
    token: Optional[str],
    db_path=DEFAULT_DB_PATH,
    limit: int = 100,
    max_pages: int = 5,
) -> int:
    from empire.services.storage import upsert_company

    companies = fetch_companies(token=token, limit=limit, max_pages=max_pages)
    record_source("hubspot_companies", label="HubSpot Companies", created_at=None, db_path=db_path)
    count = 0
    for item in companies:
        props = item.get("properties", {})
        upsert_company(
            company_id=item.get("id"),
            hs_object_id=item.get("id"),
            name=props.get("name"),
            domain=props.get("domain"),
            website=props.get("website"),
            phone=props.get("phone"),
            address=props.get("address"),
            city=props.get("city"),
            state=props.get("state"),
            zip_code=props.get("zip"),
            country=props.get("country"),
            industry=props.get("industry"),
            annual_revenue=props.get("annualrevenue"),
            num_employees=props.get("numberofemployees"),
            owner_id=props.get("hubspot_owner_id"),
            createdate=props.get("createdate"),
            lastmodifieddate=props.get("lastmodifieddate"),
            raw_json=str(props),
            db_path=db_path,
        )
        count += 1
    record_event(
        record_id=None,
        event_type="hubspot.companies.sync",
        occurred_at=_utc_now(),
        subject=f"HubSpot synced {count} companies",
        notes=f"limit={limit} pages={max_pages}",
        db_path=db_path,
    )
    return count


def sync_all(
    *,
    token: Optional[str],
    db_path=DEFAULT_DB_PATH,
    limit: int = 100,
    max_pages: int = 5,
) -> Dict[str, int]:
    return {
        "contacts": sync_contacts(token=token, db_path=db_path, limit=limit, max_pages=max_pages),
        "companies": sync_companies(token=token, db_path=db_path, limit=limit, max_pages=max_pages),
    }


def _find_contact_by_email(token: str, email: str) -> Optional[str]:
    payload = {
        "filterGroups": [
            {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
        ],
        "properties": ["email"],
        "limit": 1,
    }
    resp = _post_with_retry(HUBSPOT_CONTACTS_SEARCH, payload, token)
    results = resp.json().get("results", [])
    if results:
        return results[0].get("id")
    return None


def _find_company_by_domain(token: str, domain: str) -> Optional[str]:
    payload = {
        "filterGroups": [
            {"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}
        ],
        "properties": ["domain"],
        "limit": 1,
    }
    resp = _post_with_retry(HUBSPOT_COMPANIES_SEARCH, payload, token)
    results = resp.json().get("results", [])
    if results:
        return results[0].get("id")
    return None


def push_contacts(
    *,
    token: Optional[str],
    db_path=DEFAULT_DB_PATH,
    limit: int = 500,
) -> int:
    from empire.services.storage import list_records

    resolved_token = token or get_secret("hubspot_private_app_token")
    if not resolved_token:
        raise ValueError("Missing HubSpot token")

    records = list_records(db_path=db_path, limit=limit)
    pushed = 0
    for record in records:
        email = record.get("email")
        if not email:
            continue
        existing_id = _find_contact_by_email(resolved_token, email)
        properties = {k: v for k, v in record.items() if k not in {"record_id", "hs_object_id"} and v}
        if existing_id:
            _post_with_retry(
                f"{HUBSPOT_CONTACTS}/{existing_id}",
                {"properties": properties},
                resolved_token,
                method="PATCH",
            )
        else:
            _post_with_retry(HUBSPOT_CONTACTS, {"properties": properties}, resolved_token)
        pushed += 1
    record_event(
        record_id=None,
        event_type="hubspot.contacts.push",
        occurred_at=_utc_now(),
        subject=f"HubSpot pushed {pushed} contacts",
        notes=f"limit={limit}",
        db_path=db_path,
    )
    return pushed


def push_companies(
    *,
    token: Optional[str],
    db_path=DEFAULT_DB_PATH,
    limit: int = 500,
) -> int:
    from empire.services.storage import list_companies

    resolved_token = token or get_secret("hubspot_private_app_token")
    if not resolved_token:
        raise ValueError("Missing HubSpot token")

    companies = list_companies(db_path=db_path, limit=limit)
    pushed = 0
    for company in companies:
        domain = company.get("domain")
        if not domain:
            continue
        existing_id = _find_company_by_domain(resolved_token, domain)
        properties = {k: v for k, v in company.items() if k not in {"company_id", "hs_object_id"} and v}
        if existing_id:
            _post_with_retry(
                f"{HUBSPOT_COMPANIES}/{existing_id}",
                {"properties": properties},
                resolved_token,
                method="PATCH",
            )
        else:
            _post_with_retry(HUBSPOT_COMPANIES, {"properties": properties}, resolved_token)
        pushed += 1
    record_event(
        record_id=None,
        event_type="hubspot.companies.push",
        occurred_at=_utc_now(),
        subject=f"HubSpot pushed {pushed} companies",
        notes=f"limit={limit}",
        db_path=db_path,
    )
    return pushed
