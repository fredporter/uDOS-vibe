# Beacon Portal (Overview)

**Version:** v1.4.3
**Last Updated:** 2026-02-19
**Status:** Concept / Deferred in v1.4.3 release scope
**Owner:** uDOS Engineering

> This is the single Beacon summary page. It is intentionally concise; detailed design references live in `docs/specs/` and `docs/decisions/`.

---

## Purpose

A **Beacon** is a minimal Wi‑Fi node that announces presence and routes nearby devices to a **Wizard** gateway when available. It is intentionally dumb, replaceable, and local‑first.

**Motto:** Beacon announces; Wizard decides.

---

## Principles

- **Presence over capacity** — be discoverable, not data‑heavy
- **Single responsibility** — Beacon connects; Wizard computes
- **Local‑first** — no WAN required
- **Graceful degradation** — Beacon still signals intent when Wizard is offline

---

## Connectivity Model

```
Device → Beacon (Wi‑Fi) → Wizard (optional)
```

All layers are optional:
- ✅ Device only (offline)
- ✅ Device + Beacon (local Wi‑Fi)
- ✅ Device + Beacon + Wizard (gateway features)

---

## Operating Modes (High‑Level)

- **Private‑Home** — trusted devices, familiar Wi‑Fi, optional sharing
- **Public‑Secure** — isolated clients, captive portal, rate limits

---

## Status

Beacon is **not part of the current baseline** by default. It remains a design‑level concept and may be activated in later milestones.
