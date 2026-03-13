#!/usr/bin/env python3
"""
BEA.exe Patch: Force IsCheatActive() TRUE (BROKEN)
==================================================
Makes `IsCheatActive()` return TRUE unconditionally.

WARNING: This patch is BROKEN - it causes goodies to LOCK instead of unlock due to
inverted logic in the g_bAllCheatsEnabled code path. Use save name cheats instead
(MALLOY, TURKEY work without any patch).

Technical Details:
  Virtual Address: 0x00465490 (IsCheatActive function start)
  File Offset:     0x65490

  Original (11 bytes):
    00465490: A1 F4 2D 66 00     MOV EAX,[0x00662df4]  ; Load g_bDevModeEnabled
    00465495: 81 EC 00 01 00 00  SUB ESP,0x100

  Patched (11 bytes):
    00465490: B8 01 00 00 00     MOV EAX,0x1           ; Return TRUE
    00465495: C2 04 00           RET 0x4               ; Return immediately
    00465498: 90 90 90           NOP NOP NOP           ; Padding

Effects (BROKEN due to inverted logic):
  - MALLOY (index 0): LOCKS goodies instead of unlocking (bug!)
  - TURKEY (index 1): All campaign levels accessible
  - V3R5IOF (index 2): Version display enabled (no call sites found yet, needs in-game confirmation)
  - Maladim (index 3): No visible effect
  - Aurore (index 4): Free camera debug toggle
  - lat\xEAte (index 5): Goodie UI override

NOTE: The PC port uses different cheat codes than the source:
  - Source "105770Y2" -> PC port "MALLOY"
  - Source "B4K42" -> PC port "Maladim"
  MALLOY and TURKEY work via save name WITHOUT any patch.

NOTE: There are 11 code locations that check g_bAllCheatsEnabled directly
without calling IsCheatActive(). These control additional behaviors (frontend
flow, music selection, etc.) and won't be affected by this patch. For FULL
dev mode behavior, a runtime trainer would be needed to set the BSS flag.

Usage:
  python3 patch_ischeatactive_always_true_BROKEN.py path/to/BEA.exe
  python3 patch_ischeatactive_always_true_BROKEN.py path/to/BEA.exe --restore

Discovered via Ghidra RE analysis, December 2025
"""

import sys
import shutil
from pathlib import Path

# Patch configuration
PATCH_NAME = "IsCheatActive() Always TRUE (BROKEN)"
VIRTUAL_ADDRESS = 0x00465490
FILE_OFFSET = 0x65490  # VA 0x465490 - ImageBase 0x400000 = RVA 0x65490, .text RVA=0x1000, Raw=0x1000 -> 0x65490

# Original bytes (11 bytes)
ORIGINAL_BYTES = bytes([
    0xA1, 0xF4, 0x2D, 0x66, 0x00,        # MOV EAX,[0x00662df4]
    0x81, 0xEC, 0x00, 0x01, 0x00, 0x00   # SUB ESP,0x100
])

# Patched bytes (11 bytes) - return TRUE immediately
PATCHED_BYTES = bytes([
    0xB8, 0x01, 0x00, 00, 0x00,  # MOV EAX,0x1
    0xC2, 0x04, 0x00,             # RET 0x4
    0x90, 0x90, 0x90              # NOP padding
])


def apply_patch(exe_path: Path) -> bool:
    """Apply the all-cheats patch to BEA.exe."""
    backup_path = exe_path.with_suffix('.exe.backup')

    print(f"Reading {exe_path}...")
    data = bytearray(exe_path.read_bytes())

    print(f"  Target: VA {hex(VIRTUAL_ADDRESS)} -> File offset {hex(FILE_OFFSET)}")

    # Verify bytes
    current_bytes = bytes(data[FILE_OFFSET:FILE_OFFSET + len(ORIGINAL_BYTES)])

    if current_bytes == PATCHED_BYTES:
        print(f"\n[OK] Patch already applied!")
        return True

    if current_bytes != ORIGINAL_BYTES:
        print(f"\n[ERROR] Unexpected bytes at offset {hex(FILE_OFFSET)}:")
        print(f"  Expected: {ORIGINAL_BYTES.hex(' ')}")
        print(f"  Found:    {current_bytes.hex(' ')}")
        print(f"\nPossible causes:")
        print(f"  - Wrong BEA.exe version (not Steam release)")
        print(f"  - v1 patch already applied (different location)")
        print(f"  - File corrupted")
        return False

    # Create backup
    if not backup_path.exists():
        print(f"\nCreating backup: {backup_path}")
        shutil.copy2(exe_path, backup_path)
    else:
        print(f"\nBackup already exists: {backup_path}")

    # Apply patch
    print(f"\nApplying patch '{PATCH_NAME}'...")
    print(f"  Before: {ORIGINAL_BYTES.hex(' ')}")
    print(f"  After:  {PATCHED_BYTES.hex(' ')}")

    data[FILE_OFFSET:FILE_OFFSET + len(PATCHED_BYTES)] = PATCHED_BYTES

    exe_path.write_bytes(data)
    print(f"\n" + "="*60)
    print(f"WARNING: THIS PATCH IS BROKEN!")
    print(f"="*60)
    print(f"\nIsCheatActive() now always returns TRUE, but due to inverted")
    print(f"logic in the g_bAllCheatsEnabled code path, goodies will LOCK.")
    print(f"\nRecommendation: Use save name cheats instead (MALLOY, TURKEY)")
    print(f"which work WITHOUT any patch.")
    print(f"\nTo restore original: python3 {Path(__file__).name} {exe_path} --restore")

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


STEAM_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe")


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
        print("\nUsage: python3 patch_ischeatactive_always_true_BROKEN.py [path/to/BEA.exe] [--restore]")
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
