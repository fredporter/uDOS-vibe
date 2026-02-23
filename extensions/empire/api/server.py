"""Empire API server (FastAPI)."""

from __future__ import annotations

import sqlite3
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.middleware.cors import CORSMiddleware

from empire.services.storage import DEFAULT_DB_PATH, ensure_schema, record_event
from empire.services.secret_store import get_secret, set_secret


def _connect(db_path: Path) -> sqlite3.Connection:
    ensure_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _check_token(authorization: Optional[str], required_token: Optional[str]) -> None:
    if not required_token:
        return
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ", 1)[1].strip()
    if token != required_token:
        raise HTTPException(status_code=403, detail="Invalid token")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_access(db_path: Path, request: Request) -> None:
    record_event(
        record_id=None,
        event_type="api.access",
        occurred_at=_utc_now(),
        subject=f"{request.method} {request.url.path}",
        notes=f"client={request.client.host if request.client else 'unknown'}",
        db_path=db_path,
    )


def create_app(db_path: Path = DEFAULT_DB_PATH) -> FastAPI:
    app = FastAPI(title="Empire API", version="0.1.0")
    api_token = os.getenv("EMPIRE_API_TOKEN") or get_secret("empire_api_token")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health(request: Request, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _check_token(authorization, api_token)
        _log_access(db_path, request)
        return {"status": "ok"}

    @app.get("/records")
    def list_records(
        request: Request,
        limit: int = Query(100, ge=1, le=500),
        authorization: Optional[str] = Header(default=None),
    ) -> List[Dict[str, Any]]:
        _check_token(authorization, api_token)
        _log_access(db_path, request)
        try:
            with _connect(db_path) as conn:
                rows = conn.execute(
                    """
                    SELECT record_id, email, firstname, lastname, company, jobtitle,
                           phone, city, state, country, lifecyclestage, lastmodifieddate
                    FROM records
                    ORDER BY lastmodifieddate DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/events")
    def list_events(
        request: Request,
        limit: int = Query(50, ge=1, le=200),
        authorization: Optional[str] = Header(default=None),
    ) -> List[Dict[str, Any]]:
        _check_token(authorization, api_token)
        _log_access(db_path, request)
        try:
            with _connect(db_path) as conn:
                rows = conn.execute(
                    """
                    SELECT event_id, record_id, event_type, occurred_at, subject, notes
                    FROM events
                    ORDER BY occurred_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/tasks")
    def list_tasks(
        request: Request,
        limit: int = Query(50, ge=1, le=200),
        status: Optional[str] = Query(default=None),
        authorization: Optional[str] = Header(default=None),
    ) -> List[Dict[str, Any]]:
        _check_token(authorization, api_token)
        _log_access(db_path, request)
        try:
            with _connect(db_path) as conn:
                if status:
                    rows = conn.execute(
                        """
                        SELECT t.task_id, t.title, t.category, t.source, t.source_ref, t.created_at,
                               t.status, t.notes, t.record_id, c.company_id, c.name AS company_name
                        FROM tasks t
                        LEFT JOIN contact_companies cc ON cc.record_id = t.record_id
                        LEFT JOIN companies c ON c.company_id = cc.company_id
                        WHERE t.status = ?
                        GROUP BY t.task_id
                        ORDER BY t.created_at DESC
                        LIMIT ?
                        """,
                        (status, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT t.task_id, t.title, t.category, t.source, t.source_ref, t.created_at,
                               t.status, t.notes, t.record_id, c.company_id, c.name AS company_name
                        FROM tasks t
                        LEFT JOIN contact_companies cc ON cc.record_id = t.record_id
                        LEFT JOIN companies c ON c.company_id = cc.company_id
                        GROUP BY t.task_id
                        ORDER BY t.created_at DESC
                        LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
            return [dict(row) for row in rows]
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/tasks/{task_id}/status")
    def update_task_status(
        request: Request,
        task_id: str,
        status: str = Query(..., pattern="^(open|in_progress|done)$"),
        authorization: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _check_token(authorization, api_token)
        _log_access(db_path, request)
        try:
            with _connect(db_path) as conn:
                conn.execute(
                    "UPDATE tasks SET status = ? WHERE task_id = ?",
                    (status, task_id),
                )
            return {"task_id": task_id, "status": status}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/auth/rotate")
    def rotate_token(
        request: Request,
        authorization: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        nonlocal api_token
        _check_token(authorization, api_token)
        new_token = secrets.token_urlsafe(32)
        set_secret("empire_api_token", new_token)
        api_token = new_token
        record_event(
            record_id=None,
            event_type="api.token.rotate",
            occurred_at=_utc_now(),
            subject="API token rotated",
            notes=f"client={request.client.host if request.client else 'unknown'}",
            db_path=db_path,
        )
        return {"token": new_token}

    return app


app = create_app()
