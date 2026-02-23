# TypeScript Runtime (uCode)

Version: v1.4.3
Last Updated: 2026-02-19

uDOS uses a TS runtime layer for deterministic script execution and selected command backends.

## Runtime-backed command surfaces

### DRAW PAT

Pattern operations are TS-backed behind `DRAW PAT ...`.

```bash
DRAW PAT LIST
DRAW PAT CYCLE
DRAW PAT TEXT "status"
DRAW PAT <pattern-name>
```

### RUN --ts DATA

Dataset operations are TS-backed behind `RUN --ts DATA ...`.

```bash
RUN --ts DATA LIST
RUN --ts DATA VALIDATE <id>
RUN --ts DATA BUILD <id> [output_id]
RUN --ts DATA REGEN <id> [output_id]
```

### READ --ts / RUN --ts PARSE

Markdown runtime parsing is TS-backed:

```bash
READ --ts <file>
RUN --ts PARSE <file>
```

## Runtime shakedown

Use `VERIFY` for TS runtime checks:

```bash
VERIFY
```

`VERIFY` validates Node/toolchain presence and runtime smoke execution.
