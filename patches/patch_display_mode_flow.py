#!/usr/bin/env python3
"""
BEA.exe Patch: Display Mode Flow (Resolution + Windowed)
=======================================================

This utility applies reversible, byte-verified patches across two tracks:

- Stable track: primary display/windowed behavior patches.
- Experimental track: optional startup-flow tweak for edge-case setups.

Stable patches:

1) Resolution gate bypass in mode enumeration
   - Allows non-4:3 mode candidates even when `g_AllowWidescreenModes` is false.
   - Source location: BuildDeviceList path near VA 0x00529696.
   - File offset: 0x129696
   - Patch: 0xCC -> 0x00

2) Force windowed startup (without relying on CLI `-forcewindowed`)
   - Forces the startup windowed decision to TRUE (when device supports windowed).
   - Source location: Initialize3DEnvironment path near VA 0x0052A644.
   - File offset: 0x12A644
   - Patch: A1 F0 2D 66 00 -> B8 01 00 00 00

3) Unlock extra graphics features by default
   - Changes the GEFORCE_FX_POWER tweak registration default from 0 to 1.
   - Source location near VA 0x004CDD40.
   - File offset: 0x0CDD40
   - Patch: 6A 00 -> 6A 01

4) Ignore cardid.txt vendor/device tweak overrides
   - Bypasses startup call into cardid parser/override application path.
   - Source location near VA 0x0052AF3F.
   - File offset: 0x12AF3F
   - Patch: E8 9C D7 FF FF -> 90 90 90 90 90

5) Version overlay pointer redirect
   - Redirects bottom-left version overlay format pointer to patched-format cave string.
   - Source location near VA 0x0046316F.
   - File offset: 0x06416F
   - Patch: 54 94 62 00 -> 44 A4 5A 00

6) Version overlay cave string payload
   - Installs format string: `V%1d.%02d - PATCHED`.
   - Source location near VA 0x005AA444.
   - File offset: 0x1AA444
   - Patch: 20xCC bytes -> ASCII payload bytes

Experimental optional patch:
7) Skip auto fullscreen toggle in startup/device-flow helper
   - Source location near VA 0x0052BB97.
   - File offset: 0x12BB97
   - Patch: 75 20 -> EB 20
   - This is intentionally optional because behavior can vary by environment.

Usage:
  python3 patches/patch_display_mode_flow.py --verify
  python3 patches/patch_display_mode_flow.py --apply
  python3 patches/patch_display_mode_flow.py --apply --resolution-only
  python3 patches/patch_display_mode_flow.py --apply --windowed-only
  python3 patches/patch_display_mode_flow.py --apply --skip-auto-toggle
  python3 patches/patch_display_mode_flow.py --restore
  python3 patches/patch_display_mode_flow.py --path "C:\\path\\to\\BEA.exe" --apply
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe")
BACKUP_SUFFIX = ".original.backup"


@dataclass(frozen=True)
class PatchSpec:
    name: str
    file_offset: int
    original: bytes
    patched: bytes
    optional: bool = False


BASE_PATCHES = [
    PatchSpec(
        name="BuildDeviceList non-4:3 rejection bypass",
        file_offset=0x129696,
        original=bytes([0xCC]),
        patched=bytes([0x00]),
    ),
    PatchSpec(
        name="Force windowed startup flag in Initialize3DEnvironment",
        file_offset=0x12A644,
        original=bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
        patched=bytes([0xB8, 0x01, 0x00, 0x00, 0x00]),
    ),
    PatchSpec(
        name="Unlock extra graphics features default gate (GEFORCE_FX_POWER=1)",
        file_offset=0x0CDD40,
        original=bytes([0x6A, 0x00]),
        patched=bytes([0x6A, 0x01]),
    ),
    PatchSpec(
        name="Ignore cardid.txt vendor/device tweak overrides",
        file_offset=0x12AF3F,
        original=bytes([0xE8, 0x9C, 0xD7, 0xFF, 0xFF]),
        patched=bytes([0x90, 0x90, 0x90, 0x90, 0x90]),
    ),
    PatchSpec(
        name="Version overlay pointer -> patched format cave",
        file_offset=0x6416F,
        original=bytes([0x54, 0x94, 0x62, 0x00]),
        patched=bytes([0x44, 0xA4, 0x5A, 0x00]),
    ),
    PatchSpec(
        name="Version overlay cave format payload (V%1d.%02d - PATCHED)",
        file_offset=0x1AA444,
        original=bytes([0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC]),
        patched=bytes([0x56, 0x25, 0x31, 0x64, 0x2E, 0x25, 0x30, 0x32, 0x64, 0x20, 0x2D, 0x20, 0x50, 0x41, 0x54, 0x43, 0x48, 0x45, 0x44, 0x00]),
    ),
]

OPTIONAL_PATCH = PatchSpec(
    name="Skip auto ToggleFullscreen call gate",
    file_offset=0x12BB97,
    original=bytes([0x75, 0x20]),
    patched=bytes([0xEB, 0x20]),
    optional=True,
)


def active_patches(
    include_optional: bool, resolution_only: bool, windowed_only: bool
) -> list[PatchSpec]:
    if resolution_only and windowed_only:
        raise ValueError("Cannot combine --resolution-only and --windowed-only")

    # Core selectable display-flow patches.
    if resolution_only:
        patches = [BASE_PATCHES[0]]
    elif windowed_only:
        patches = [BASE_PATCHES[1]]
    else:
        patches = list(BASE_PATCHES[:4])

    # Auto companion: if any patch is selected, watermark overlay as patched.
    patches.extend(BASE_PATCHES[4:6])

    if include_optional:
        patches.append(OPTIONAL_PATCH)
    return patches


def read_bytes(data: bytearray, offset: int, length: int) -> bytes:
    return bytes(data[offset : offset + length])


def check_specs(data: bytearray, specs: Iterable[PatchSpec]) -> tuple[bool, bool]:
    """
    Returns:
      (all_known_state, all_already_patched)
    """
    all_known_state = True
    all_already_patched = True

    for spec in specs:
        cur = read_bytes(data, spec.file_offset, len(spec.original))
        if cur == spec.patched:
            print(f"[OK] {spec.name}: already patched")
        elif cur == spec.original:
            print(f"[OK] {spec.name}: ready to patch")
            all_already_patched = False
        else:
            print(f"[ERR] {spec.name}: unexpected bytes at 0x{spec.file_offset:X}")
            print(f"      expected original: {spec.original.hex(' ')}")
            print(f"      expected patched : {spec.patched.hex(' ')}")
            print(f"      found           : {cur.hex(' ')}")
            all_known_state = False
            all_already_patched = False

    return all_known_state, all_already_patched


def apply(exe_path: Path, specs: list[PatchSpec]) -> bool:
    data = bytearray(exe_path.read_bytes())
    all_known_state, all_already_patched = check_specs(data, specs)
    if not all_known_state:
        print("\nAborting due to unexpected bytes.")
        return False
    if all_already_patched:
        print("\nNo changes needed.")
        return True

    backup_path = Path(str(exe_path) + BACKUP_SUFFIX)
    if not backup_path.exists():
        shutil.copy2(exe_path, backup_path)
        print(f"\nCreated backup: {backup_path}")
    else:
        print(f"\nBackup exists: {backup_path}")

    for spec in specs:
        cur = read_bytes(data, spec.file_offset, len(spec.original))
        if cur == spec.original:
            data[spec.file_offset : spec.file_offset + len(spec.patched)] = spec.patched
            print(
                f"patched 0x{spec.file_offset:X}: "
                f"{spec.original.hex(' ')} -> {spec.patched.hex(' ')}  ({spec.name})"
            )

    exe_path.write_bytes(data)
    print("\nPatch apply complete.")
    return True


def restore(exe_path: Path) -> bool:
    backup_path = Path(str(exe_path) + BACKUP_SUFFIX)
    if not backup_path.exists():
        print(f"[ERR] Backup not found: {backup_path}")
        return False
    shutil.copy2(backup_path, exe_path)
    print(f"Restored from backup: {backup_path}")
    return True


def verify(exe_path: Path, specs: list[PatchSpec]) -> bool:
    data = bytearray(exe_path.read_bytes())
    all_known_state, all_already_patched = check_specs(data, specs)
    if not all_known_state:
        return False
    print(f"\nState: {'patched' if all_already_patched else 'mixed/original'}")
    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Patch BEA.exe display mode behavior")
    p.add_argument("--path", type=Path, default=DEFAULT_EXE, help="Target BEA.exe path")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true", help="Apply selected patches")
    mode.add_argument("--restore", action="store_true", help="Restore backup")
    mode.add_argument("--verify", action="store_true", help="Verify patch state only")
    p.add_argument(
        "--skip-auto-toggle",
        action="store_true",
        help="Include optional patch to skip startup ToggleFullscreen gate",
    )
    p.add_argument(
        "--resolution-only",
        action="store_true",
        help="Select only the non-4:3 resolution gate bypass patch",
    )
    p.add_argument(
        "--windowed-only",
        action="store_true",
        help="Select only the forced windowed startup patch",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    exe_path: Path = args.path
    if not exe_path.exists():
        print(f"[ERR] File not found: {exe_path}")
        return 1

    try:
        specs = active_patches(
            include_optional=args.skip_auto_toggle,
            resolution_only=args.resolution_only,
            windowed_only=args.windowed_only,
        )
    except ValueError as e:
        print(f"[ERR] {e}")
        return 1
    print(f"Target: {exe_path}")
    print(f"Patches selected: {len(specs)}")

    if args.verify:
        ok = verify(exe_path, specs)
    elif args.restore:
        ok = restore(exe_path)
    else:
        ok = apply(exe_path, specs)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
