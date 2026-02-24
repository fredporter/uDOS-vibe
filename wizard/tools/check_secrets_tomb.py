#!/usr/bin/env python3
"""Quick diagnostic tool to check secrets.tomb status."""

from __future__ import annotations

from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wizard.services.secret_store import SecretStoreError, get_secret_store
from wizard.services.setup_profiles import load_install_profile, load_user_profile


def main():
    print("\n🔍 SECRETS TOMB DIAGNOSTIC\n")

    # Check WIZARD_KEY
    wizard_key = get_config("WIZARD_KEY", "")
    if wizard_key:
        print(f"✅ WIZARD_KEY is set (length: {len(wizard_key)})")
    else:
        print("❌ WIZARD_KEY is NOT set")
        print("\n💡 Set it with: export WIZARD_KEY=<your-key>")
        print("   Or ensure .env file exists in repo root\n")
        return 1

    # Check tomb file
    tomb_path = Path(__file__).parent.parent / "secrets.tomb"
    if tomb_path.exists():
        size = tomb_path.stat().st_size
        print(f"✅ secrets.tomb exists ({size} bytes)")
    else:
        print("❌ secrets.tomb does NOT exist")
        print("\n💡 It will be created when you submit the setup story\n")
        return 0

    # Try to unlock
    print("\n🔓 Attempting to unlock secret store...")
    try:
        store = get_secret_store()
        store.unlock()
        print("✅ Secret store unlocked successfully!")

        # Count entries
        entries = store.list()
        print(f"   Found {len(entries)} entries:")
        for entry in entries:
            print(f"   • {entry.key_id} (provider: {entry.provider})")

    except SecretStoreError as e:
        print(f"❌ Failed to unlock: {e}")
        print("\n💡 This means:")
        print("   • The WIZARD_KEY doesn't match the key used to encrypt the tomb")
        print("   • Or the tomb file is corrupted")
        print("\n💡 To fix:")
        print("   1. Check if .env has the correct WIZARD_KEY")
        print("   2. If you changed the key, delete secrets.tomb and re-run setup")
        print("   3. Command: rm wizard/secrets.tomb")
        return 1

    # Try to load profiles
    print("\n👤 Checking user profile...")
    user_result = load_user_profile()
    if user_result.data:
        print(f"✅ User profile found: {user_result.data.get('username', 'N/A')}")
    elif user_result.locked:
        print(f"❌ User profile locked: {user_result.error}")
    else:
        print("⚠️  No user profile stored yet (run TUI setup story)")

    print("\n💾 Checking installation profile...")
    install_result = load_install_profile()
    if install_result.data:
        print(
            f"✅ Install profile found: {install_result.data.get('installation_id', 'N/A')}"
        )
    elif install_result.locked:
        print(f"❌ Install profile locked: {install_result.error}")
    else:
        print("⚠️  No installation profile stored yet (run TUI setup story)")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
