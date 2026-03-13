#!/usr/bin/env python3
"""
BEA.exe Patch: IsCheatActive() Return-Path Bypass (Legacy)
=========================================================
STATUS: PARTIAL - Only enables TURKEY effect (all campaign levels).

This patch modifies a conditional jump in IsCheatActive() to unconditional,
but only affects the final return path - not the early-exit checks.
Use patch_devmode_goodies_logic_fix.py for dev mode exploration instead.

NOTE: MALLOY and TURKEY work via save name WITHOUT any patch.

Technical Details:
  Virtual Address: 0x004654a0
  File Offset:     0x654a0
  Original Bytes:  75 7A (JNZ +0x7A)
  Patched Bytes:   EB 7A (JMP +0x7A)

Usage:
  python3 patch_ischeatactive_return_path_bypass.py path/to/BEA.exe
  python3 patch_ischeatactive_return_path_bypass.py path/to/BEA.exe --restore  # Restore backup

Discovered via Ghidra RE analysis, December 2025
"""

import sys
import struct
import shutil
from pathlib import Path

# Patch configuration
PATCH_NAME = "Partial Cheats (Legacy - TURKEY only)"
VIRTUAL_ADDRESS = 0x004654a0
ORIGINAL_BYTES = bytes([0x75, 0x7A])  # JNZ +0x7A
PATCHED_BYTES = bytes([0xEB, 0x7A])   # JMP +0x7A


def read_pe_headers(data: bytes) -> dict:
    """Parse PE headers to get section information."""
    # DOS header
    if data[:2] != b'MZ':
        raise ValueError("Not a valid PE file (missing MZ signature)")

    pe_offset = struct.unpack_from('<I', data, 0x3C)[0]

    # PE signature
    if data[pe_offset:pe_offset+4] != b'PE\x00\x00':
        raise ValueError("Not a valid PE file (missing PE signature)")

    # COFF header
    coff_offset = pe_offset + 4
    num_sections = struct.unpack_from('<H', data, coff_offset + 2)[0]
    optional_header_size = struct.unpack_from('<H', data, coff_offset + 16)[0]

    # Optional header
    optional_offset = coff_offset + 20
    magic = struct.unpack_from('<H', data, optional_offset)[0]

    if magic == 0x10b:  # PE32
        image_base = struct.unpack_from('<I', data, optional_offset + 28)[0]
    elif magic == 0x20b:  # PE32+
        image_base = struct.unpack_from('<Q', data, optional_offset + 24)[0]
    else:
        raise ValueError(f"Unknown PE magic: {hex(magic)}")

    # Section headers
    section_offset = optional_offset + optional_header_size
    sections = []

    for i in range(num_sections):
        sect_start = section_offset + (i * 40)
        name = data[sect_start:sect_start+8].rstrip(b'\x00').decode('ascii', errors='replace')
        virtual_size = struct.unpack_from('<I', data, sect_start + 8)[0]
        virtual_addr = struct.unpack_from('<I', data, sect_start + 12)[0]
        raw_size = struct.unpack_from('<I', data, sect_start + 16)[0]
        raw_offset = struct.unpack_from('<I', data, sect_start + 20)[0]

        sections.append({
            'name': name,
            'virtual_address': virtual_addr,
            'virtual_size': virtual_size,
            'raw_offset': raw_offset,
            'raw_size': raw_size
        })

    return {
        'image_base': image_base,
        'sections': sections
    }


def va_to_file_offset(va: int, pe_info: dict) -> int:
    """Convert virtual address to file offset."""
    rva = va - pe_info['image_base']

    for section in pe_info['sections']:
        sect_start = section['virtual_address']
        sect_end = sect_start + section['virtual_size']

        if sect_start <= rva < sect_end:
            offset_in_section = rva - sect_start
            return section['raw_offset'] + offset_in_section

    raise ValueError(f"Virtual address {hex(va)} not found in any section")


def apply_patch(exe_path: Path) -> bool:
    """Apply the all-cheats patch to BEA.exe."""
    backup_path = exe_path.with_suffix('.exe.backup')

    # Read the executable
    print(f"Reading {exe_path}...")
    data = bytearray(exe_path.read_bytes())

    # Parse PE headers
    pe_info = read_pe_headers(data)
    print(f"  Image base: {hex(pe_info['image_base'])}")

    # Calculate file offset
    file_offset = va_to_file_offset(VIRTUAL_ADDRESS, pe_info)
    print(f"  VA {hex(VIRTUAL_ADDRESS)} -> File offset {hex(file_offset)}")

    # Verify original bytes
    current_bytes = bytes(data[file_offset:file_offset + len(ORIGINAL_BYTES)])

    if current_bytes == PATCHED_BYTES:
        print(f"\n[!] Patch already applied!")
        return True

    if current_bytes != ORIGINAL_BYTES:
        print(f"\n[ERROR] Unexpected bytes at offset {hex(file_offset)}:")
        print(f"  Expected: {ORIGINAL_BYTES.hex(' ')}")
        print(f"  Found:    {current_bytes.hex(' ')}")
        print(f"\nThis may not be the correct version of BEA.exe.")
        return False

    # Create backup
    if not backup_path.exists():
        print(f"\nCreating backup: {backup_path}")
        shutil.copy2(exe_path, backup_path)
    else:
        print(f"\nBackup already exists: {backup_path}")

    # Apply patch
    print(f"\nApplying patch '{PATCH_NAME}'...")
    print(f"  Offset {hex(file_offset)}: {ORIGINAL_BYTES.hex(' ')} -> {PATCHED_BYTES.hex(' ')}")

    data[file_offset:file_offset + len(PATCHED_BYTES)] = PATCHED_BYTES

    # Write patched file
    exe_path.write_bytes(data)
    print(f"\nPatch applied successfully!")
    print(f"\nEffects:")
    print(f"  - Partial: TURKEY-like effect only (levels unlocked)")
    print(f"  - MALLOY and Maladim are NOT enabled by this patch")

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
        print("\nUsage: python3 patch_ischeatactive_return_path_bypass.py [path/to/BEA.exe] [--restore]")
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
