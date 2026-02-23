# Dry Run

Use dry-run to validate device selection and manifest values before any destructive action.

```bash
python3 core/sonic_cli.py plan --usb-device /dev/sdb --dry-run --layout-file config/sonic-layout.json
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --dry-run

# Native partitioning payload-only dry-run
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --payloads-only --dry-run

# Native payloads dir override dry-run
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --payloads-dir /path/to/payloads --payloads-only --dry-run

# Native payloads without validation (dry-run)
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --no-validate-payloads --payloads-only --dry-run
```
