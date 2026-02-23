# Sonic Screwdriver Device Database

This dataset is the public, portable device catalog used by Sonic Screwdriver.
It is designed to be human-editable and easy to redistribute.

## Files

- `sonic-devices.table.md` — Primary Markdown table (human-editable)
- `sonic-devices.schema.json` — JSON Schema for validation
- `sonic-devices.sql` — SQLite schema + seed data
- `version.json` — Dataset version metadata

## Workflow

1) Edit `sonic-devices.table.md`
2) Validate against `sonic-devices.schema.json`
3) Compile SQLite:

```bash
sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql
```

## Notes

- Keep rows factual and reproducible.
- Use `unknown` for fields that are not yet verified.
- `windows10_boot`, `media_mode`, and `udos_launcher` are required capability fields.
  Use `unknown` when capability data is not yet verified.
- `wizard_profile` and `media_launcher` are optional planning fields used by
  Wizard/Sonic integration surfaces.
