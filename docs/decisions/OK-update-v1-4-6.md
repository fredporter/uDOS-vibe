uDOS — AGENTS.md Governance & OK Agent Standardisation Brief

Objective

Standardise AGENTS.md usage across the entire uDOS repository to:
	•	Prevent architectural drift
	•	Eliminate outdated helper guidance
	•	Ensure folder-level contextual accuracy
	•	Align OK helpers with current milestone state
	•	Integrate Binder-based project grouping
	•	Formalise milestone update workflows
	•	Enforce uDOS branding (no use of “AI” terminology)
	•	Define Mistral Vibe-CLI as the TUI integration bridge

This applies repo-wide.

⸻

0️⃣ Branding & Terminology Policy (Critical)

uDOS does not use the term “AI”.

Reason:
	•	Branding discipline
	•	User comfort
	•	Strategic positioning
	•	Avoid fear-based terminology

Approved Terms

Use:
	•	OK Assistant
	•	OK Agent
	•	OK Helper
	•	OK Model
	•	OK Provider
	•	Agent
	•	Helper
	•	Model
	•	Provider
	•	Assistant

Prohibited Term
	•	❌ AI

This rule applies to:
	•	AGENTS.md
	•	Documentation
	•	Code comments
	•	Commit messages
	•	CLI outputs
	•	User-facing interfaces
	•	Binder documentation

If refactoring legacy files:
	•	Replace “AI” with appropriate “OK” terminology.

⸻

1️⃣ Core Principles
	1.	AGENTS.md is the authoritative OK Agent behaviour file for its scope.
	2.	Each directory may define its own scoped AGENTS.md.
	3.	Deeper AGENTS.md files override higher-level ones.
	4.	AGENTS.md must only reflect:
	•	Current architecture
	•	Confirmed working patterns
	•	100% tested milestone state
	5.	AGENTS.md must never contain:
	•	Speculative ideas
	•	Deprecated architecture
	•	Historical notes
	•	TODO items
	•	Work-in-progress logic

All WIP belongs in tasks.md, not AGENTS.md.

⸻

2️⃣ Repo-Wide Structure

At minimum:

/AGENTS.md                  → Global uDOS architecture authority
/DEVLOG.md                  → Global dev log
/project.json               → High-level repo metadata
/tasks.md                   → Active global tasks
/completed.json             → Completed milestones

Root AGENTS.md defines:
	•	Core vs Wizard separation
	•	Runtime rules
	•	Logging model
	•	OK Agent interaction boundaries
	•	Vibe-CLI integration model

⸻

3️⃣ Binder-Level Structure

Each Binder directory must contain:

/binders/{binder-name}/
    AGENTS.md
    DEVLOG.md
    project.json
    tasks.md
    completed.json

Binder Rules
	•	Binder AGENTS.md refines global rules.
	•	Binder may NOT contradict root architecture.
	•	Binder may define:
	•	Runtime constraints
	•	Language rules
	•	Subsystem boundaries
	•	Testing requirements
	•	OK Agent scope limitations

⸻

4️⃣ Folder-Level AGENTS.md Rules

Any major subsystem may include:

core/
wizard/
dev/
vibe-cli/
runtime-ts/

Each may define:

/{subsystem}/AGENTS.md

These must:
	•	Be short (under 200 lines preferred)
	•	Define:
	•	Purpose
	•	Allowed dependencies
	•	Prohibited cross-imports
	•	Runtime model
	•	Logging rules
	•	Test expectations
	•	OK Agent constraints

⸻

5️⃣ Mistral Vibe-CLI — TUI Integration Layer (Mandatory Reference)

Mistral Vibe-CLI is the official uDOS TUI interface layer.

It provides:
	•	Terminal-based OK Agent interaction
	•	ucode command execution bridge
	•	Model/provider abstraction
	•	Multi-provider routing capability

Architectural Role

Vibe-CLI acts as:

User
  ↓
Vibe-CLI (TUI)
  ↓
OK Provider / OK Model
  ↓
ucode commands
  ↓
uDOS core / wizard / runtime

Rules
	•	All OK Agent interactions in terminal context must route through Vibe-CLI.
	•	OK helpers must generate ucode-compatible output when operating inside uDOS.
	•	No direct subsystem mutation outside ucode command boundaries.
	•	OK Agents integrate via command-level abstraction, not direct file mutation unless explicitly allowed.

⸻

6️⃣ ucode Command Integration Policy

OK Agents operating within uDOS must:
	•	Prefer emitting valid UCODE commands where applicable.
	•	Avoid raw script dumping when a ucode command exists.
	•	Respect core vs wizard separation.
	•	Avoid bypassing logging or runtime hooks.

Example:

Instead of:

Write Python file directly modifying logs

Prefer:

LOG WRITE "message"
RUN TASK build
SYNC NAS

ucode is the canonical automation interface.

⸻

7️⃣ Milestone Update Protocol (Critical)

When a milestone is:
	•	Fully implemented
	•	All tests passing (100%)
	•	Pushed to main
	•	Tagged (if applicable)

Required Actions
	1.	Update relevant AGENTS.md files
	•	Remove obsolete rules
	•	Add confirmed architectural truths
	•	Reflect current folder structure
	2.	Append summary to:
	•	DEVLOG.md
	3.	Move completed items:
	•	From tasks.md
	•	Into completed.json
	4.	Confirm:
	•	No stale OK Agent guidance remains
	•	No deprecated architecture persists
	•	No legacy terminology (“AI”) remains

⸻

8️⃣ AGENTS.md Content Template

Every AGENTS.md must follow:

# AGENTS.md — {Scope Name}

Last Updated: YYYY-MM-DD
Milestone: {Milestone Name}
Status: Stable / Experimental

## Purpose

## Architecture Rules

## Dependency Rules

## Runtime Model

## Logging Policy

## Testing Requirements

## OK Agent Behaviour Constraints
- Do not generate legacy patterns.
- Do not reintroduce deprecated architecture.
- Do not duplicate runtime logic.
- Respect ucode boundaries.
- Use approved terminology (no AI usage).

No narrative.
No brainstorming.
No speculative planning.

⸻

9️⃣ OK Agent Enforcement Policy

All OK Agents must:
	•	Read the nearest AGENTS.md before generating code.
	•	Defer to folder-level AGENTS.md over root.
	•	Never infer architecture outside defined rules.
	•	Avoid generating duplicate subsystems.
	•	Avoid resurrecting deprecated patterns.
	•	Respect Vibe-CLI integration model.
	•	Respect ucode command layer.

If instructions conflict:
→ Prefer deeper scoped AGENTS.md.

⸻

🔟 Drift Prevention Strategy
	•	Keep AGENTS.md short and authoritative.
	•	Refactor immediately after milestone completion.
	•	Never allow AGENTS.md to lag behind architecture.
	•	Run quarterly repo-wide AGENTS audit.
	•	Enforce terminology audit (no “AI” reintroduced).

⸻

1️⃣1️⃣ What Must NEVER Happen Again
	•	Root AGENTS.md describing old architecture.
	•	OK Agent referencing pre-refactor patterns.
	•	Duplicate logging systems.
	•	Old networking logic reappearing in core.
	•	Wizard/core boundary violations.
	•	TS runtime duplication in Python.
	•	Dead subsystems being re-generated.
	•	“AI” terminology reappearing in repo.

⸻

1️⃣2️⃣ Implementation Task for Copilot (OK Assistant)
	1.	Audit all existing AGENTS.md files.
	2.	Identify stale or conflicting architectural rules.
	3.	Remove legacy “AI” terminology.
	4.	Propose a standardised root AGENTS.md.
	5.	Generate missing Binder-level AGENTS.md files.
	6.	Scaffold subsystem AGENTS.md where needed.
	7.	Align with current uDOS architecture.
	8.	Validate Vibe-CLI integration references.
	9.	Commit changes under:

chore(agents): standardise AGENTS governance and OK terminology


⸻

Outcome

After implementation:
	•	OK helpers operate deterministically.
	•	Architecture remains stable.
	•	Milestones define truth.
	•	Binder logic is respected.
	•	Vibe-CLI remains the official integration bridge.
	•	Branding remains consistent.
	•	No more architectural drift from outdated agent guidance.

⸻

# AGENTS.md — uDOS Root Governance

Last Updated: 2026-02-24
Milestone: Architecture Stabilisation Phase
Status: Stable

---

## 1. Purpose

This file defines the authoritative behavioural and architectural rules for all OK Agents, OK Assistants, OK Helpers, OK Models, and OK Providers operating within the uDOS repository.

This document governs:

- Architecture boundaries
- Runtime separation
- OK Agent integration rules
- Vibe-CLI interaction model
- ucode command enforcement
- Branding terminology policy

Deeper scoped AGENTS.md files override this document within their folder scope.

---

## 2. Branding & Terminology Policy (Mandatory)

uDOS does NOT use the term “AI”.

Approved terms:
- OK Assistant
- OK Agent
- OK Helper
- OK Model
- OK Provider
- Agent / Helper / Model / Provider / Assistant

Prohibited:
- AI (in documentation, code comments, commit messages, CLI output, or user interfaces)

If legacy terminology exists, it must be refactored.

---

## 3. Core Architecture Model

uDOS consists of clearly separated layers:

### Core (Minimal / Deterministic)
- Stdlib Python only
- No external networking logic
- No web responsibilities
- Deterministic execution
- Logging centralised
- No hidden runtime side-effects

### Wizard (Extended / Networked)
- Full venv
- Networking + web responsibilities
- OK Provider integrations
- Extended automation
- External service interaction

### TypeScript Runtime (If Enabled)
- Lightweight execution partner
- No duplication of Python core logic
- Works alongside core, not replacing it

Cross-boundary violations are prohibited.

---

## 4. Vibe-CLI Integration Model

Mistral Vibe-CLI is the official TUI interaction layer.

All terminal-based OK Agent interactions must route through:

User  
↓  
Vibe-CLI  
↓  
OK Provider / OK Model  
↓  
ucode commands  
↓  
uDOS subsystems  

Rules:
- No direct mutation of subsystems outside command boundary.
- OK Agents must emit ucode-compatible instructions where possible.
- Raw script dumping is discouraged if a ucode command exists.

Vibe-CLI is the canonical interaction bridge.

---

## 5. ucode Command Enforcement

ucode is the automation interface for uDOS.

OK Agents must:

- Prefer emitting valid UCODE commands.
- Avoid bypassing logging hooks.
- Avoid direct file manipulation unless explicitly required.
- Respect core vs wizard boundaries.

If a subsystem exposes a command, use it.

---

## 6. Logging Model

All logs are centralised:

~/memory/logs/

Rules:
- No shadow logging systems.
- No duplicate logging frameworks.
- Dev verbosity must be suppressible in production mode.
- Logging API must be respected.

---

## 7. Binder System

Binders group related projects.

Each Binder must contain:

- AGENTS.md
- DEVLOG.md
- project.json
- tasks.md
- completed.json

Binder AGENTS.md may refine behaviour but cannot contradict root architecture.

---

## 8. Milestone Governance

AGENTS.md must reflect:

- Confirmed architecture
- Fully tested systems (100% passing)
- Pushed milestone state

AGENTS.md must NOT contain:
- Speculation
- Roadmaps
- TODO items
- Historical commentary

Milestone completion requires:
1. Update relevant AGENTS.md files
2. Update DEVLOG.md
3. Move tasks to completed.json
4. Remove stale architectural guidance

---

## 9. OK Agent Behaviour Constraints

OK Agents operating within uDOS must:

- Read nearest AGENTS.md before generating code
- Prefer deeper scoped AGENTS.md over root
- Not reintroduce deprecated patterns
- Not duplicate subsystems
- Not bypass ucode
- Not violate core/wizard separation
- Not generate legacy architecture
- Not use prohibited terminology

If instructions conflict:
→ Prefer deeper scoped AGENTS.md.

---

## 10. Drift Prevention

- Keep AGENTS.md concise and authoritative
- Audit quarterly
- Update immediately after milestone completion
- Remove obsolete patterns immediately

Architecture truth lives here.
Speculation lives elsewhere.

---

End of AGENTS.md

---

Excellent.
Below are two deliverables:

1️⃣ Draft Root AGENTS.md (Production-ready)
2️⃣ Outline Brief — OK Provider Abstraction Contract

Both aligned to uDOS governance, branding (no “AI”), Vibe-CLI, and ucode-first execution.

⸻

1️⃣ Root /AGENTS.md — uDOS

# AGENTS.md — uDOS Root Governance

Last Updated: 2026-02-24
Milestone: Architecture Stabilisation Phase
Status: Stable

---

## 1. Purpose

This file defines the authoritative behavioural and architectural rules for all OK Agents, OK Assistants, OK Helpers, OK Models, and OK Providers operating within the uDOS repository.

This document governs:

- Architecture boundaries
- Runtime separation
- OK Agent integration rules
- Vibe-CLI interaction model
- ucode command enforcement
- Branding terminology policy

Deeper scoped AGENTS.md files override this document within their folder scope.

---

## 2. Branding & Terminology Policy (Mandatory)

uDOS does NOT use the term “AI”.

Approved terms:
- OK Assistant
- OK Agent
- OK Helper
- OK Model
- OK Provider
- Agent / Helper / Model / Provider / Assistant

Prohibited:
- AI (in documentation, code comments, commit messages, CLI output, or user interfaces)

If legacy terminology exists, it must be refactored.

---

## 3. Core Architecture Model

uDOS consists of clearly separated layers:

### Core (Minimal / Deterministic)
- Stdlib Python only
- No external networking logic
- No web responsibilities
- Deterministic execution
- Logging centralised
- No hidden runtime side-effects

### Wizard (Extended / Networked)
- Full venv
- Networking + web responsibilities
- OK Provider integrations
- Extended automation
- External service interaction

### TypeScript Runtime (If Enabled)
- Lightweight execution partner
- No duplication of Python core logic
- Works alongside core, not replacing it

Cross-boundary violations are prohibited.

---

## 4. Vibe-CLI Integration Model

Mistral Vibe-CLI is the official TUI interaction layer.

All terminal-based OK Agent interactions must route through:

User  
↓  
Vibe-CLI  
↓  
OK Provider / OK Model  
↓  
ucode commands  
↓  
uDOS subsystems  

Rules:
- No direct mutation of subsystems outside command boundary.
- OK Agents must emit ucode-compatible instructions where possible.
- Raw script dumping is discouraged if a ucode command exists.

Vibe-CLI is the canonical interaction bridge.

---

## 5. ucode Command Enforcement

ucode is the automation interface for uDOS.

OK Agents must:

- Prefer emitting valid UCODE commands.
- Avoid bypassing logging hooks.
- Avoid direct file manipulation unless explicitly required.
- Respect core vs wizard boundaries.

If a subsystem exposes a command, use it.

---

## 6. Logging Model

All logs are centralised:

~/memory/logs/

Rules:
- No shadow logging systems.
- No duplicate logging frameworks.
- Dev verbosity must be suppressible in production mode.
- Logging API must be respected.

---

## 7. Binder System

Binders group related projects.

Each Binder must contain:

- AGENTS.md
- DEVLOG.md
- project.json
- tasks.md
- completed.json

Binder AGENTS.md may refine behaviour but cannot contradict root architecture.

---

## 8. Milestone Governance

AGENTS.md must reflect:

- Confirmed architecture
- Fully tested systems (100% passing)
- Pushed milestone state

AGENTS.md must NOT contain:
- Speculation
- Roadmaps
- TODO items
- Historical commentary

Milestone completion requires:
1. Update relevant AGENTS.md files
2. Update DEVLOG.md
3. Move tasks to completed.json
4. Remove stale architectural guidance

---

## 9. OK Agent Behaviour Constraints

OK Agents operating within uDOS must:

- Read nearest AGENTS.md before generating code
- Prefer deeper scoped AGENTS.md over root
- Not reintroduce deprecated patterns
- Not duplicate subsystems
- Not bypass ucode
- Not violate core/wizard separation
- Not generate legacy architecture
- Not use prohibited terminology

If instructions conflict:
→ Prefer deeper scoped AGENTS.md.

---

## 10. Drift Prevention

- Keep AGENTS.md concise and authoritative
- Audit quarterly
- Update immediately after milestone completion
- Remove obsolete patterns immediately

Architecture truth lives here.
Speculation lives elsewhere.

---

End of File


⸻

OK Provider Abstraction Contract (Outline)

Objective

Define a strict abstraction layer that allows:
	•	Multiple OK Providers (OpenAI, Mistral, local models, etc.)
	•	Interchangeable OK Models
	•	Unified behaviour through Vibe-CLI
	•	ucode-compliant output
	•	Deterministic system interaction

Without coupling business logic to a specific provider.

⸻

1️⃣ Core Philosophy

Providers are interchangeable.
Models are replaceable.
ucode is authoritative.
Vibe-CLI is the bridge.

The system must not depend on:
	•	Provider-specific response formats
	•	Provider-specific system prompts
	•	Hidden behaviour in external models

All outputs must normalise before entering uDOS execution layer.

⸻

2️⃣ Architectural Layers

User
↓
Vibe-CLI
↓
OK Provider Adapter
↓
Response Normaliser
↓
ucode Command Layer
↓
uDOS Subsystems


⸻

3️⃣ Provider Adapter Requirements

Each OK Provider must implement:
	•	Standardised request format
	•	Standardised response format
	•	Streaming compatibility (optional)
	•	Deterministic temperature defaults
	•	Explicit role handling (system/user/helper)

No provider may directly access filesystem or network outside Wizard scope.

⸻

4️⃣ Response Normalisation

Before execution:
	•	Strip markdown wrappers
	•	Extract valid ucode commands
	•	Validate syntax
	•	Reject unsafe patterns
	•	Prevent direct shell injection
	•	Enforce boundary rules

If invalid → return structured error, not partial execution.

⸻

5️⃣ Model Tiering

Support:
	•	Local models
	•	Cloud providers
	•	Lightweight models for TUI quick ops
	•	Heavy models for architectural planning

Routing logic lives in Vibe-CLI.

⸻

6️⃣ Determinism Rules

Default settings:
	•	Low temperature for execution mode
	•	Structured output mode where possible
	•	Strict command parsing

Exploration mode allowed only in dev context.

⸻

7️⃣ Security Boundary

Core:
	•	No external provider access.

Wizard:
	•	Provider access allowed.
	•	Must route through abstraction contract.

No provider may bypass:
	•	Logging
	•	ucode
	•	Runtime constraints

⸻

8️⃣ Branding Compliance

Providers must not self-identify using prohibited terminology.
All user-facing output must comply with OK terminology policy.

⸻

9️⃣ Future Expansion

Contract must support:
	•	Offline-first model fallback
	•	Multi-provider routing
	•	Failover logic
	•	Performance telemetry
	•	Capability-based routing

⸻

Strategic Impact

Once implemented:
	•	You can swap providers without refactoring logic.
	•	You prevent architectural corruption from model drift.
	•	You gain deterministic command-layer execution.
	•	You separate “thinking” from “doing”.

That separation is critical.
