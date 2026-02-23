# Self‑Healing (Housekeeping)

**Version:** v1.4.4+
**Last Updated:** 2026-02-22
**Status:** Maintenance Utility

Self‑healing is a housekeeping tool that checks common issues and can apply safe fixes. It is not a feature surface; it keeps the system stable.

---

## Purpose

- Detect missing deps, port conflicts, and config drift
- Provide a safe repair path before running TUI or Wizard
- Keep developer environments consistent

---

## Use

```bash
./bin/udos-self-heal.sh
./bin/udos-self-heal.sh wizard
./bin/udos-self-heal.sh --no-repair
```

> If scripts or paths differ in your build, use `HELP` or check `/bin/` for the current entrypoint.

---

## Where It Lives

- CLI wrapper: `bin/udos-self-heal.sh`
- Service logic: `core/services/self_healer.py` (if present)

---

## Notes

Self‑healing should be **safe by default** and **transparent** about changes it makes. Treat it as a maintenance routine, not a user‑facing feature.
