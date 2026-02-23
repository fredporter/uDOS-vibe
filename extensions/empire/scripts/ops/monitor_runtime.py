#!/usr/bin/env python3
"""Runtime monitor for Empire API and DB event throughput."""

from __future__ import annotations

import argparse
import sqlite3
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional


def _request_health(base_url: str, token: Optional[str], timeout: float = 3.0) -> tuple[bool, float, int]:
    url = urllib.parse.urljoin(base_url.rstrip('/') + '/', 'health')
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            _ = resp.read()
            elapsed = (time.perf_counter() - started) * 1000.0
            return resp.status == 200, elapsed, resp.status
    except urllib.error.HTTPError as exc:
        elapsed = (time.perf_counter() - started) * 1000.0
        return False, elapsed, exc.code
    except Exception:
        elapsed = (time.perf_counter() - started) * 1000.0
        return False, elapsed, -1


def _event_count(db_path: Path) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        return conn.execute('SELECT count(*) FROM events').fetchone()[0]


def main() -> int:
    parser = argparse.ArgumentParser(description='Monitor Empire runtime health')
    parser.add_argument('--base-url', default='http://127.0.0.1:8991')
    parser.add_argument('--db', default='data/empire.db')
    parser.add_argument('--token', default=None)
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--interval-s', type=float, default=2.0)
    parser.add_argument('--fail-threshold', type=int, default=1)
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f'FAIL db missing: {db_path}')
        return 1

    before = _event_count(db_path)
    latencies: list[float] = []
    failures = 0

    for i in range(args.samples):
        ok, elapsed_ms, status = _request_health(args.base_url, args.token)
        latencies.append(elapsed_ms)
        marker = 'PASS' if ok else 'FAIL'
        if not ok:
            failures += 1
        print(f'{marker} sample={i+1} status={status} latency_ms={elapsed_ms:.2f}')
        if i < args.samples - 1:
            time.sleep(args.interval_s)

    after = _event_count(db_path)
    avg_ms = statistics.mean(latencies) if latencies else 0.0
    p95_idx = int(round(0.95 * (len(latencies) - 1))) if latencies else 0
    p95_ms = sorted(latencies)[p95_idx] if latencies else 0.0

    print(f'SUMMARY samples={args.samples} failures={failures} avg_ms={avg_ms:.2f} p95_ms={p95_ms:.2f}')
    print(f'SUMMARY events_before={before} events_after={after} delta={after-before}')

    if failures > args.fail_threshold:
        print('FAIL runtime monitor threshold exceeded')
        return 1

    print('PASS runtime monitor')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
