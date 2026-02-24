# AGENTS.md — Development Workspace

Last Updated: 2026-02-24
Milestone: v1.4.6 Architecture Stabilisation Phase
Status: Stable

---

## Purpose

The `dev` subsystem contains development roadmaps, tasks, and planning documentation.

This is a clean workspace for:
- Development planning
- Roadmap tracking
- Task management
- Milestone coordination
- Extension/template creation

---

## Structure

```
dev/
├── AGENTS.md           (this file)
├── DEVLOG.md           (development log)
├── project.json        (dev workspace config)
├── tasks.md            (active development tasks)
├── completed.json      (completed milestones)
└── docs/               (planning docs)
```

---

## Content Policy

dev/ must contain ONLY:
- Planning documents
- Roadmaps
- Task tracking
- Extension templates
- Development guides

dev/ must NOT contain:
- Production code
- Tests
- Runtime logic
- Third-party libraries
- User-facing features

---

## Governance Templates

All governance files in dev/ are templates.

Users may:
- Copy templates to their own projects
- Adapt governance structure
- Define custom workflows

Users must NOT:
- Modify dev/ templates for their projects
- Use dev/ as a workspace
- Store project data in dev/

---

## OK Agent Behaviour Constraints

When working in dev:

- Do not generate production code
- Do not create runtime logic
- Keep templates generic
- Avoid implementation details
- Focus on process and structure

If code is needed → implement in core or wizard.
If documentation is needed → docs/ or wiki/.

---

End of File
