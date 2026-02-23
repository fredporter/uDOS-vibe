"""Email receive scaffolding for Empire (IMAP)."""

from __future__ import annotations

import imaplib
import email
from email.header import decode_header, make_header
from typing import List, Dict, Optional


def _decode(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def receive_emails(
    *,
    host: str,
    username: str,
    password: str,
    mailbox: str = "INBOX",
    limit: int = 25,
) -> List[Dict[str, str]]:
    """Fetch recent emails via IMAP (scaffold)."""
    results: List[Dict[str, str]] = []
    with imaplib.IMAP4_SSL(host) as client:
        client.login(username, password)
        client.select(mailbox)
        status, data = client.search(None, "ALL")
        if status != "OK":
            return results
        ids = data[0].split()
        for msg_id in ids[-limit:]:
            status, msg_data = client.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            raw = msg_data[0][1]
            message = email.message_from_bytes(raw)
            subject = _decode(message.get("Subject"))
            sender = _decode(message.get("From"))
            date = _decode(message.get("Date"))
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain" and not part.get_filename():
                        try:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                        except Exception:
                            body = ""
                        break
            else:
                try:
                    body = message.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    body = ""

            results.append(
                {
                    "subject": subject,
                    "from": sender,
                    "date": date,
                    "body": body.strip(),
                }
            )
    return results
