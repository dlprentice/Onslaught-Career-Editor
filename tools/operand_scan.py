# SPDX-License-Identifier: GPL-3.0-or-later
"""Whole-image little-endian operand scan with disassembly context.

Read-only. Scans every byte of a PE image for the 4-byte little-endian encoding
of each supplied virtual address, then disassembles a window ending at each hit
so the containing instruction can be classified as a load, a store, or a push.

Usage:
  py -3 tools/operand_scan.py <image> <va> [<va> ...] [--window N]
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

import capstone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pe_read_va import PeImage  # noqa: E402


def va_of_offset(img: PeImage, off: int) -> int | None:
    for _name, vaddr, vsize, rawptr, rawsize in img.sections:
        if rawptr <= off < rawptr + rawsize:
            return img.image_base + vaddr + (off - rawptr)
    return None


def section_of_offset(img: PeImage, off: int) -> str:
    for name, _vaddr, _vsize, rawptr, rawsize in img.sections:
        if rawptr <= off < rawptr + rawsize:
            return name
    return "?"


def decode_at(img: PeImage, md: capstone.Cs, hit_off: int, window: int):
    """Return the instruction whose encoding contains hit_off, found by trying
    every start offset in a backwards window and keeping decodings that align."""
    results = []
    for back in range(1, window + 1):
        start = hit_off - back
        start_va = va_of_offset(img, start)
        if start_va is None:
            continue
        code = img.data[start : start + 20]
        try:
            insn = next(md.disasm(code, start_va, 1))
        except StopIteration:
            continue
        if insn.address + insn.size > (va_of_offset(img, hit_off) or 0) >= insn.address:
            results.append((back, insn))
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("vas", nargs="+", type=lambda s: int(s, 0))
    ap.add_argument("--window", type=int, default=8)
    args = ap.parse_args()

    img = PeImage(args.image)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

    for va in args.vas:
        needle = struct.pack("<I", va)
        print(f"\n=== 0x{va:08x}  needle {needle.hex(' ')} ===")
        hits = []
        start = 0
        while True:
            i = img.data.find(needle, start)
            if i < 0:
                break
            hits.append(i)
            start = i + 1
        print(f"occurrences: {len(hits)}")
        for off in hits:
            sec = section_of_offset(img, off)
            hva = va_of_offset(img, off)
            print(f"  file 0x{off:08x}  section {sec}  va 0x{hva:08x}" if hva else f"  file 0x{off:08x}  {sec}")
            if sec not in (".text", "CODE", ".code"):
                continue
            for back, insn in decode_at(img, md, off, args.window):
                print(f"      -{back}: 0x{insn.address:08x}  {insn.mnemonic:<8} {insn.op_str}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
