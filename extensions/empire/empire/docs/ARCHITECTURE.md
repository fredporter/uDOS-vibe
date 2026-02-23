# Empire Architecture (Private)

Empire is a private business extension for uDOS. It depends on Core + Wizard.

High-level spine:
- `src/` package root
- `services/` business domain services
- `integrations/` external systems + connectors
- `scripts/` ingest/process/export utilities
- `config/` templates and defaults
- `tests/` validation and regression suites

Runtime expectations:
- Runs only when the private submodule is present.
- Missing module should soft-fail with a friendly message.

Initial functional spine:
- Ingestion: raw CSV/JSON/JSONL intake → JSONL staging.
- Normalization: shape raw records to a canonical schema for business workflows.
- Storage: SQLite schema for records, sources, and events (HubSpot-aligned fields).
- API: FastAPI surface for health, records, and events.
- API auth: `EMPIRE_API_TOKEN` bearer auth (private-only).
- Integrations: Gmail API + Google Places (scaffolded).
- Email pipeline: receive → categorize → tasks + record updates.
- API ops: `EMPIRE API START|STOP` runs FastAPI on `127.0.0.1:8991`.
- Email validation: rejects malformed/bot addresses, keeps role-based inboxes.
