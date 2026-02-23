# thin-gui

Thin GUI contract package for Wizard launch flows.

Scope:
- Emits `LaunchIntent` payloads to Wizard routes
- Consumes launch session streams
- No OS-specific launch logic

This package is transport-only. Platform decisions stay in Wizard launcher adapters.
