# Empire Scripts

Private scripts live here (sync, ingest, enrichment, reporting).

Structure:
- `ingest/` raw intake and staging
- `process/` normalization and dedupe
- `export/` outbound snapshots and feeds
- `email/` email receive + process scaffolding
- `integrations/` Gmail + Places sync helpers
- `setup/` secret/token setup helpers
- `smoke/` repeatable local smoke checks

Quick start:
- `python scripts/ingest/run_ingest.py <input.csv> --out data/raw/records.jsonl`
- `python scripts/process/normalize_records.py --in data/raw/records.jsonl --out data/normalized/records.jsonl`
- `scripts/smoke/run_phase2_api_smoke.sh` (no-token mode)
- `EMPIRE_API_TOKEN=phase2token scripts/smoke/run_phase2_api_smoke.sh` (token/auth mode)
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_preflight.py --db data/empire.db` (Phase 3 no-live-data readiness)
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/integration_no_live_smoke.py` (Phase 3 mocked end-to-end sync smoke)
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/api_perf_baseline.py --base-url http://127.0.0.1:8991 --iterations 25` (Phase 4 API perf baseline)
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/db_backup_restore_sanity.py --db data/empire.db` (Phase 4 DB backup/restore sanity)
- `scripts/smoke/phase5_launch_gate.sh` (Phase 5 full launch gate)
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/ops/monitor_runtime.py --db data/empire.db --samples 30 --interval-s 2` (runtime monitoring check)
- `scripts/setup/ci_seed_mock_secrets.sh` (CI/local mock secret bootstrap)
- `PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/setup/set_google_places_api_key.py --api-key '<value>'` (configure Places key)
