#!/usr/bin/env python3
"""Decode BEA.exe cheat table (XOR with key "HELP ME!!").

Usage:
  python3 tools/cheat_table_decode.py
  python3 tools/cheat_table_decode.py --exe game/BEA.exe --count 6
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Decode BEA.exe cheat table")
    p.add_argument("--exe", default="game/BEA.exe", help="Path to BEA.exe")
    p.add_argument("--count", type=int, default=6, help="Number of entries to decode (default: 6)")
    return p.parse_args()


def pe_sections(blob: bytes):
    pe_off = struct.unpack_from("<I", blob, 0x3C)[0]
    if blob[pe_off:pe_off + 4] != b"PE\x00\x00":
        raise ValueError("PE header not found")
    num_sections = struct.unpack_from("<H", blob, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", blob, pe_off + 20)[0]
    image_base = struct.unpack_from("<I", blob, pe_off + 24 + 28)[0]
    sect_off = pe_off + 24 + opt_size
    sections = []
    for i in range(num_sections):
        off = sect_off + i * 40
        name = blob[off:off + 8].split(b"\x00")[0].decode("ascii", "ignore")
        vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", blob, off + 8)
        sections.append((name, vaddr, vsize, rptr, rsize))
    return image_base, sections


def va_to_file(va: int, image_base: int, sections):
    rva = va - image_base
    for name, vaddr, vsize, rptr, rsize in sections:
        span = max(vsize, rsize)
        if vaddr <= rva < vaddr + span:
            return rptr + (rva - vaddr)
    return None


def escape_bytes(b: bytes) -> str:
    out = []
    for c in b:
        if 32 <= c < 127 and c not in (0x5C,):
            out.append(chr(c))
        elif c == 0x5C:
            out.append("\\\\")
        else:
            out.append(f"\\x{c:02x}")
    return "".join(out)


def main() -> int:
    args = parse_args()
    exe_path = Path(args.exe)
    if not exe_path.exists():
        # fallback to repo root
        fallback = Path("BEA.exe")
        if fallback.exists():
            exe_path = fallback
        else:
            print(f"ERROR: BEA.exe not found at {args.exe} or ./BEA.exe")
            return 1

    blob = exe_path.read_bytes()
    image_base, sections = pe_sections(blob)

    cheat_va = 0x00629464
    key_va = 0x00629A64
    cheat_off = va_to_file(cheat_va, image_base, sections)
    key_off = va_to_file(key_va, image_base, sections)
    if cheat_off is None or key_off is None:
        print("ERROR: Failed to map cheat/key addresses to file offsets")
        return 1

    key = blob[key_off:key_off + 16].split(b"\x00")[0]
    if not key:
        print("ERROR: XOR key not found")
        return 1

    entry_size = 0x100
    print(f"Key: {escape_bytes(key)} (len={len(key)})")
    for idx in range(args.count):
        enc = blob[cheat_off + idx * entry_size: cheat_off + idx * entry_size + len(key)]
        dec = bytes(enc[i] ^ key[i] for i in range(len(key)))
        dec = dec.split(b"\x00")[0]
        print(f"{idx:02d}: {escape_bytes(dec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
