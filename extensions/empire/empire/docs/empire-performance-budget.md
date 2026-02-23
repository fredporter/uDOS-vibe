# Empire Performance Budget (Phase 4)

Scope
- Local API baseline for alpha gate, measured via `scripts/smoke/api_perf_baseline.py`.
- Endpoint budget uses p95 and max response times.

Alpha gate thresholds
- `/health`: p95 <= 20 ms, max <= 50 ms
- `/records?limit=50`: p95 <= 40 ms, max <= 80 ms
- `/events?limit=50`: p95 <= 40 ms, max <= 80 ms
- `/tasks?limit=50`: p95 <= 40 ms, max <= 80 ms

Latest run (2026-02-15, token mode, n=25)
- `health`: avg=2.13 ms, p95=2.07 ms, max=15.25 ms
- `records`: avg=2.01 ms, p95=2.44 ms, max=2.52 ms
- `events`: avg=2.22 ms, p95=2.56 ms, max=2.63 ms
- `tasks`: avg=2.02 ms, p95=2.42 ms, max=2.63 ms

Gate result
- PASS: all measured endpoints are within threshold.
