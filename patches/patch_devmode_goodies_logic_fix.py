#!/usr/bin/env python3
"""
BEA.exe Patch: Dev-Mode Goodies UI Logic Fix
===========================================
Fixes a dev-mode edge-case where `g_bAllCheatsEnabled` makes *all* cheat indices return TRUE,
including the goodies-only cheat at index 5 (`lat\xEAte`). When both `MALLOY` (index 0) and
`lat\xEAte` (index 5) are treated as active, the goodies UI gating logic can effectively hide
or block goodies actions.

This patch forces `g_Cheat_LATETE` to remain 0 in the goodies UI, so `g_bAllCheatsEnabled`
behaves like "MALLOY only" for the gallery.

NOTE: The MALLOY cheat works WITHOUT this patch when using a save name
containing "MALLOY". This patch is only needed for dev mode exploration.

This patch changes one instruction so the `g_Cheat_LATETE` flag is always written as 0.

Technical Details:
  Patch 1: VA 0x0045D819, File offset 0x5D819
    Before: F7 D8 (NEG EAX)
    After:  33 C0 (XOR EAX,EAX)

Effects (DEV MODE ONLY - normal save name cheats work without this patch):
  - Prevents `g_bAllCheatsEnabled` from activating the `lat\xEAte` goodies-only flag inside the gallery

Cheat Codes (enter as save game name):
  - MALLOY   : All goodies (index 0) - works WITHOUT patch
  - TURKEY   : All levels (index 1) - works WITHOUT patch
  - V3R5IOF  : Version display (index 2; no call sites found yet, needs in-game confirmation)
  - Maladim  : God mode (index 3) - no visible effect, needs investigation
  - Aurore   : Free camera debug toggle (index 4)
  - lat\xEAte: Goodie UI override (index 5)

NOTE: MALLOY works WITHOUT this patch via save name. This patch is for dev mode
exploration of the g_bAllCheatsEnabled code path only.

Usage:
  python3 patch_devmode_goodies_logic_fix.py              # Apply to Steam installation
  python3 patch_devmode_goodies_logic_fix.py --restore    # Restore from backup
  python3 patch_devmode_goodies_logic_fix.py <path>       # Custom path

Discovered via Ghidra RE analysis, December 2025
"""

import sys
import shutil
from pathlib import Path

STEAM_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe")

# Patch configuration
PATCHES = [
    {
        "name": "Disable g_Cheat_LATETE in goodies UI",
        "file_offset": 0x5D819,
        "original": bytes([0xF7, 0xD8]),  # NEG EAX
        "patched": bytes([0x33, 0xC0]),   # XOR EAX,EAX
    },
]


def apply_patch(exe_path: Path) -> bool:
    """Apply the goodies logic fix patches to BEA.exe."""
    backup_path = exe_path.with_suffix('.exe.backup')

    print(f"Reading {exe_path}...")
    data = bytearray(exe_path.read_bytes())

    # Verify all patches first
    all_ok = True
    for patch in PATCHES:
        offset = patch["file_offset"]
        current = bytes(data[offset:offset + len(patch["original"])])

        if current == patch["patched"]:
            print(f"  [{patch['name']}] Already patched")
        elif current == patch["original"]:
            print(f"  [{patch['name']}] Ready to patch at 0x{offset:X}")
        else:
            print(f"  [{patch['name']}] ERROR: Unexpected bytes at 0x{offset:X}")
            print(f"    Expected: {patch['original'].hex(' ')}")
            print(f"    Found:    {current.hex(' ')}")
            all_ok = False

    if not all_ok:
        print("\nAborting - unexpected bytes found. Wrong BEA.exe version?")
        return False

    # Check if already fully patched
    already_patched = all(
        bytes(data[p["file_offset"]:p["file_offset"] + len(p["original"])]) == p["patched"]
        for p in PATCHES
    )
    if already_patched:
        print("\n[OK] All patches already applied!")
        return True

    # Create backup
    if not backup_path.exists():
        print(f"\nCreating backup: {backup_path}")
        shutil.copy2(exe_path, backup_path)
    else:
        print(f"\nBackup exists: {backup_path}")

    # Apply patches
    print("\nApplying patches...")
    for patch in PATCHES:
        offset = patch["file_offset"]
        current = bytes(data[offset:offset + len(patch["original"])])
        if current == patch["original"]:
            data[offset:offset + len(patch["patched"])] = patch["patched"]
            print(f"  [{patch['name']}] {patch['original'].hex(' ')} -> {patch['patched'].hex(' ')}")

    exe_path.write_bytes(data)

    print("\n" + "=" * 60)
    print("PATCH APPLIED SUCCESSFULLY!")
    print("=" * 60)
    print("\nThe goodies cheat logic is now FIXED.")
    print("\nTo test: Create a save with 'MALLOY' in the name.")
    print("         Go to Goodies menu - all items should be visible.")
    print("\nCheat codes (include in save name - work WITHOUT this patch):")
    print("  MALLOY  - All goodies")
    print("  TURKEY  - All levels")
    print("  Maladim - No visible effect (needs investigation)")

    return True


def restore_backup(exe_path: Path) -> bool:
    """Restore the original BEA.exe from backup."""
    backup_path = exe_path.with_suffix('.exe.backup')

    if not backup_path.exists():
        print(f"[ERROR] No backup found at {backup_path}")
        return False

    print(f"Restoring {exe_path} from backup...")
    shutil.copy2(backup_path, exe_path)
    print("Restore complete!")
    return True


def main():
    # Parse arguments
    restore_mode = '--restore' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--restore']

    if args:
        exe_path = Path(args[0])
    elif STEAM_PATH.exists():
        exe_path = STEAM_PATH
        print(f"No path specified, using Steam installation:\n  {exe_path}\n")
    else:
        print(__doc__)
        print(f"\nDefault Steam path not found: {STEAM_PATH}")
        sys.exit(1)

    if not exe_path.exists():
        print(f"[ERROR] File not found: {exe_path}")
        sys.exit(1)

    if restore_mode:
        success = restore_backup(exe_path)
    else:
        success = apply_patch(exe_path)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
