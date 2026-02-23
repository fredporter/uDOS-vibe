#!/usr/bin/env python3
"""Empire API smoke check for Phase 2 stabilization."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional


def _request(base_url: str, path: str, token: Optional[str]) -> tuple[int, str]:
    url = urllib.parse.urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        return exc.code, body


def _assert_json(body: str, label: str) -> None:
    try:
        json.loads(body)
    except json.JSONDecodeError as exc:
        raise AssertionError(f'{label} did not return valid JSON') from exc


def main() -> int:
    parser = argparse.ArgumentParser(description='Empire API smoke check')
    parser.add_argument('--base-url', default='http://127.0.0.1:8991', help='Empire API base URL')
    parser.add_argument('--token', default=None, help='Bearer token for protected API mode')
    parser.add_argument('--expect-auth', action='store_true', help='Require auth behavior checks')
    args = parser.parse_args()

    checks: list[tuple[str, str, int]] = [
        ('health', '/health', 200),
        ('records', '/records?limit=5', 200),
        ('events', '/events?limit=5', 200),
        ('tasks', '/tasks?limit=5', 200),
    ]

    failures: list[str] = []

    for label, path, expected in checks:
        status, body = _request(args.base_url, path, args.token)
        if status != expected:
            failures.append(f'{label}: expected {expected}, got {status}')
            continue
        _assert_json(body, label)
        print(f'PASS {label} ({status})')

    if args.expect_auth:
        if not args.token:
            failures.append('auth: --expect-auth requires --token')
        else:
            status, _ = _request(args.base_url, '/health', None)
            if status != 401:
                failures.append(f'auth missing token: expected 401, got {status}')
            else:
                print('PASS auth missing token (401)')

            status, _ = _request(args.base_url, '/health', 'wrong-token')
            if status != 403:
                failures.append(f'auth wrong token: expected 403, got {status}')
            else:
                print('PASS auth wrong token (403)')

            status, body = _request(args.base_url, '/health', args.token)
            if status != 200:
                failures.append(f'auth correct token: expected 200, got {status}')
            else:
                _assert_json(body, 'auth correct token')
                print('PASS auth correct token (200)')

    if failures:
        for failure in failures:
            print(f'FAIL {failure}', file=sys.stderr)
        return 1

    print('Smoke check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
