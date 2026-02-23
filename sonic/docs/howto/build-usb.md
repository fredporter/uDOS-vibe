# Build USB (Linux)

1) Generate manifest (adjust layout via config/sonic-layout.json):
```bash
python3 core/sonic_cli.py plan --usb-device /dev/sdb --layout-file config/sonic-layout.json
```

2) Run launcher:
```bash
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json
```

Native UEFI partitioning:
```bash
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json
```

Payload-only (skip partitioning):
```bash
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --payloads-only
```

Skip payloads (partition only):
```bash
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --skip-payloads
```

Override payloads directory:
```bash
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --payloads-dir /path/to/payloads
```

Disable payload validation (escape hatch):
```bash
bash scripts/sonic-stick.sh --manifest config/sonic-manifest.json --no-validate-payloads
```

3) Add payloads (optional):
- Place uDOS squashfs at `payloads/udos/udos.squashfs`
- Add files to `payloads/windows`, `payloads/media`, `payloads/wizard`, etc.

4) Follow prompts and confirm destructive steps.
