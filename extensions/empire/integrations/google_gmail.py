"""Gmail API integration for Empire."""

from __future__ import annotations

import base64
import time
from email.utils import parseaddr
from pathlib import Path
from typing import Dict, List, Optional

from empire.services.normalization_service import normalize_payload
from empire.services.storage import DEFAULT_DB_PATH, record_event, record_source, upsert_record
from empire.services.secret_store import get_secret
from empire.services.ingestion_service import _utc_now
from empire.services.email_process import process_emails


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _resolve_paths(
    credentials_path: Optional[Path],
    token_path: Optional[Path],
) -> tuple[Path, Path]:
    cred = credentials_path or (Path(get_secret("google_gmail_credentials_path")) if get_secret("google_gmail_credentials_path") else None)
    tok = token_path or (Path(get_secret("google_gmail_token_path")) if get_secret("google_gmail_token_path") else None)
    if not cred or not tok:
        raise ValueError("Missing Gmail credentials/token paths")
    return cred, tok


def _load_gmail_service(credentials_path: Path, token_path: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except Exception as exc:
        raise RuntimeError(
            "Missing Google API dependencies. Install google-api-python-client, "
            "google-auth, google-auth-oauthlib."
        ) from exc

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def _decode_body(payload: Dict) -> str:
    body = ""
    if "body" in payload and payload["body"].get("data"):
        body = payload["body"]["data"]
    elif "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                body = part["body"]["data"]
                break
    if not body:
        return ""
    try:
        return base64.urlsafe_b64decode(body.encode("utf-8")).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _with_retry(func, *, retries: int = 3, base_delay: float = 1.0):
    for attempt in range(retries):
        try:
            return func()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))


def list_messages(
    *,
    credentials_path: Path,
    token_path: Path,
    query: str = "",
    max_results: int = 25,
    page_size: int = 50,
    rate_limit_s: float = 0.2,
) -> List[Dict[str, str]]:
    service = _load_gmail_service(credentials_path, token_path)
    messages: List[Dict[str, str]] = []
    page_token = None
    remaining = max_results
    while remaining > 0:
        batch = min(page_size, remaining)
        def _call():
            return (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=batch, pageToken=page_token)
                .execute()
            )
        response = _with_retry(_call)
        page = response.get("messages", [])
        messages.extend(page)
        remaining -= len(page)
        page_token = response.get("nextPageToken")
        if not page_token or not page:
            break
        time.sleep(rate_limit_s)
    return [{"id": msg["id"]} for msg in messages]


def get_message(
    *,
    credentials_path: Path,
    token_path: Path,
    message_id: str,
) -> Dict[str, str]:
    service = _load_gmail_service(credentials_path, token_path)
    def _call():
        return service.users().messages().get(userId="me", id=message_id, format="full").execute()
    message = _with_retry(_call)
    headers = {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}
    subject = headers.get("subject", "")
    sender = headers.get("from", "")
    date = headers.get("date", "")
    message_id = headers.get("message-id", "")
    body = _decode_body(message.get("payload", {}))
    return {
        "subject": subject,
        "from": sender,
        "date": date,
        "body": body,
        "message_id": message_id,
        "id": message.get("id", ""),
    }


def fetch_and_ingest(
    *,
    credentials_path: Optional[Path],
    token_path: Optional[Path],
    query: str = "",
    max_results: int = 25,
    rate_limit_s: float = 0.2,
    db_path: Optional[Path] = None,
) -> int:
    resolved_db_path = db_path or DEFAULT_DB_PATH
    cred_path, tok_path = _resolve_paths(credentials_path, token_path)
    record_source("gmail", label="Gmail", created_at=None, db_path=resolved_db_path)
    messages = list_messages(
        credentials_path=cred_path,
        token_path=tok_path,
        query=query,
        max_results=max_results,
        rate_limit_s=rate_limit_s,
    )
    count = 0
    email_payloads: List[Dict[str, str]] = []
    for item in messages:
        msg = get_message(
            credentials_path=cred_path,
            token_path=tok_path,
            message_id=item["id"],
        )
        email_payloads.append(msg)
        name, email_addr = parseaddr(msg.get("from", ""))
        raw = {
            "name": name,
            "email": email_addr,
            "title": None,
            "company": None,
        }
        record = normalize_payload("gmail", raw)
        if record.email or record.name:
            upsert_record(record, db_path=resolved_db_path)
            count += 1
    if email_payloads:
        process_emails(email_payloads, db_path=resolved_db_path)
    record_event(
        record_id=None,
        event_type="gmail.fetch",
        occurred_at=_utc_now(),
        subject=f"Gmail fetched {count} records",
        notes=query,
        db_path=resolved_db_path,
    )
    return count
