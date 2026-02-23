#!/usr/bin/env python3
"""Phase 4 API performance baseline (local)."""

from __future__ import annotations

import argparse
import statistics
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple


def _request(base_url: str, path: str, token: Optional[str]) -> Tuple[int, float]:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    headers: Dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    started = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        _ = resp.read()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return resp.status, elapsed_ms


def _p95(values: List[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round(0.95 * (len(ordered) - 1)))
    return ordered[idx]


def main() -> int:
    parser = argparse.ArgumentParser(description="API performance baseline")
    parser.add_argument("--base-url", default="http://127.0.0.1:8991")
    parser.add_argument("--token", default=None)
    parser.add_argument("--iterations", type=int, default=25)
    args = parser.parse_args()

    endpoints = [
        ("health", "/health"),
        ("records", "/records?limit=50"),
        ("events", "/events?limit=50"),
        ("tasks", "/tasks?limit=50"),
    ]

    for label, path in endpoints:
        timings: List[float] = []
        for _ in range(args.iterations):
            status, elapsed = _request(args.base_url, path, args.token)
            if status != 200:
                print(f"FAIL {label} expected=200 got={status}")
                return 1
            timings.append(elapsed)
        avg_ms = statistics.mean(timings)
        p95_ms = _p95(timings)
        max_ms = max(timings)
        print(
            f"PASS {label} n={args.iterations} avg_ms={avg_ms:.2f} "
            f"p95_ms={p95_ms:.2f} max_ms={max_ms:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
