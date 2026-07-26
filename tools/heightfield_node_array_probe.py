"""Corpus probe: is the CHeightField per-node array (field +0x20) populated in
any shipped heightfield header?

Read-only. Inflates every ``.aya`` under a retail ``data/resources`` tree, finds
every ``CHFD`` record (the 0x13dc-byte serialized ``CHeightField`` that
``CHeightField__Load`` @ 0x0047f750 blits over ``this`` at offset 0), and reports
the two pointer-shaped dwords at payload offsets ``+0x20`` and ``+0x24`` together
with the grid dimensions at ``+0x10bc`` / ``+0x10c0``.

``CDXEngine__GenerateLandscapeCacheTileChunk`` @ 0x00541f50 reads a per-node
array through ``heightfield+0x20`` at stride 0x18 and bilinearly interpolates a
packed RGB dword at node ``+8``. This probe answers whether that array's base
pointer ships as anything other than zero.

Usage:
    py -3 tools/heightfield_node_array_probe.py --resources <path/to/data/resources>
"""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

CHFD_PAYLOAD_SIZE = 0x13DC
FIELD_NODE_ARRAY = 0x20
FIELD_NODE_ARRAY_2 = 0x24
FIELD_GRID_W = 0x10BC
FIELD_GRID_H = 0x10C0

MAX_SOURCE = 64 * 1024 * 1024
MAX_INFLATED = 256 * 1024 * 1024
MAX_MEMBERS = 4096


def inflate_aya(source: bytes) -> bytes:
    if len(source) > MAX_SOURCE:
        raise ValueError("source limit")
    out = bytearray()
    pos = 0
    members = 0
    while pos < len(source):
        if members >= MAX_MEMBERS:
            raise ValueError("member limit")
        if len(source) - pos < 4:
            raise ValueError("truncated member header")
        length = struct.unpack_from("<I", source, pos)[0]
        pos += 4
        if length == 0 or length > len(source) - pos:
            raise ValueError("bad member length")
        out.extend(zlib.decompress(source[pos : pos + length]))
        if len(out) > MAX_INFLATED:
            raise ValueError("inflated limit")
        pos += length
        members += 1
    return bytes(out)


def find_chfd(blob: bytes):
    """Yield (offset_of_payload,) for every CHFD record of the expected size."""
    pos = 0
    while True:
        pos = blob.find(b"CHFD", pos)
        if pos < 0:
            return
        if pos + 8 <= len(blob):
            size = struct.unpack_from("<I", blob, pos + 4)[0]
            if size == CHFD_PAYLOAD_SIZE and pos + 8 + size <= len(blob):
                yield pos + 8
        pos += 4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resources", required=True)
    ap.add_argument("--extra", action="append", default=[],
                    help="additional already-inflated chunk files to probe")
    args = ap.parse_args()

    total = 0
    nonzero = 0
    for path in sorted(Path(args.resources).rglob("*.aya")):
        try:
            blob = inflate_aya(path.read_bytes())
        except (ValueError, zlib.error) as exc:
            print(f"{path.name}: SKIP ({exc})")
            continue
        for base in find_chfd(blob):
            total += 1
            a, b = struct.unpack_from("<II", blob, base + FIELD_NODE_ARRAY)
            w = struct.unpack_from("<I", blob, base + FIELD_GRID_W)[0]
            h = struct.unpack_from("<I", blob, base + FIELD_GRID_H)[0]
            flag = "NONZERO" if (a or b) else "zero"
            if a or b:
                nonzero += 1
                print(f"{path.name}: +0x20={a:#010x} +0x24={b:#010x} grid={w}x{h} {flag}")

    for extra in args.extra:
        blob = Path(extra).read_bytes()
        for base in find_chfd(blob):
            total += 1
            a, b = struct.unpack_from("<II", blob, base + FIELD_NODE_ARRAY)
            w = struct.unpack_from("<I", blob, base + FIELD_GRID_W)[0]
            h = struct.unpack_from("<I", blob, base + FIELD_GRID_H)[0]
            print(f"{Path(extra).name}: +0x20={a:#010x} +0x24={b:#010x} grid={w}x{h}")
            if a or b:
                nonzero += 1

    print(f"CHFD records probed: {total}; with a non-zero node-array pointer: {nonzero}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
