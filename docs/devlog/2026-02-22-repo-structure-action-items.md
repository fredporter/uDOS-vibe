# Repo Structure Action Items (Working Notes)

## ✅ KEEP - Our Custom Code (~500KB)

```
.vibe/
├── config.toml                    ← Custom config
├── tools → ../vibe/core/tools/ucode  ← Symlink
└── skills → ../vibe/core/skills/ucode ← Symlink

vibe/core/tools/ucode/            ← 42 CUSTOM tools
├── _base.py
├── system.py
├── spatial.py
├── data.py
├── workspace.py
├── content.py
└── specialized.py

vibe/core/skills/ucode/           ← 5 CUSTOM skills
├── ucode-help/
├── ucode-setup/
├── ucode-story/
├── ucode-dev/
└── ucode-logs/

wizard/mcp/                        ← MCP Server Integration
├── mcp_server.py
├── gateway.py
├── vibe_mcp_integration.py
└── tools/
    ├── ucode_registry.py
    ├── ucode_tools.py
    └── ucode_proxies.py
```

## Candidate Cleanup (Evaluate Before Deleting)

DON'T NEED locally since we have globally-installed Vibe CLI:

```
vibe/                             ← Most of this (except vibe/core/tools/ucode and vibe/core/skills/ucode)
├── cli/                          ← Not needed
├── acp/                          ← Not needed
├── core/
│   ├── tools/
│   │   └── (everything except ucode/) ← Delete this
│   ├── skills/
│   │   └── (everything except ucode/) ← Delete this
│   ├── config.py                ← Not needed (vibe CLI has it)
│   └── ...                      ← Delete
├── ui/                           ← Not needed
└── ...

wizard/                           ← Most of this (except wizard/mcp)
├── dashboard/                   ← DELETE (95MB!)
├── services/                    ← Can delete (vibe CLI provides via imports)
├── routes/                      ← DELETE
├── tests/                       ← DELETE
├── web/                         ← DELETE
├── docs/                        ← DELETE
├── mcp/                         ← KEEP
└── ...                          ← DELETE
```

## Why?

The **globally-installed Vibe CLI** (`~/.local/bin/vibe` or wherever it's installed) provides:
- Base Vibe functionality
- All standard services (core.services.*)
- All configuration loading
- All CLI infrastructure

This repo only needs to provide:
- **Our custom tools** (vibe/core/tools/ucode/)
- **Our custom skills** (vibe/core/skills/ucode/)
- **Our MCP integration** (wizard/mcp/)
- **Our config** (.vibe/config.toml)

Everything else can come from the installed package.

## Suggested Next Actions

If you want to clean up, you can:

```bash
# Keep a safe backup
git branch backup-full-repo

# Then delete unnecessary folders
rm -rf vibe/cli/
rm -rf vibe/acp/
rm -rf vibe/ui/
rm -rf vibe/core/auth/
# ... etc

# Keep only:
# - vibe/core/tools/ucode/
# - vibe/core/skills/ucode/
# - wizard/mcp/
```

This would reduce repo size from ~120MB to ~10-15MB.

## Current Status

If you want to leave it alone, that's fine too. The symlinks are fixed, and Vibe CLI will discover your tools/skills correctly.

The repo functions perfectly as-is—it's just carrying extra weight from the initial clone.
