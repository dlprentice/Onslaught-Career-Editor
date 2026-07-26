# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only linear x86-32 disassembly of a PE image at a virtual address.

Usage:
  py -3 tools/disasm_va.py <image> <va> [--count N] [--bytes]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import capstone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pe_read_va import PeImage  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("va", type=lambda s: int(s, 0))
    ap.add_argument("--count", type=int, default=40)
    ap.add_argument("--bytes", action="store_true")
    args = ap.parse_args()

    img = PeImage(args.image)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    off = img.to_offset(args.va)
    code = img.data[off : off + args.count * 16 + 32]
    for insn in md.disasm(code, args.va, args.count):
        raw = insn.bytes.hex(" ") if args.bytes else ""
        print(f"{insn.address:08x}  {raw:<26} {insn.mnemonic:<9} {insn.op_str}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
