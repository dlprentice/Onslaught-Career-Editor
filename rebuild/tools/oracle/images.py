# SPDX-License-Identifier: GPL-3.0-or-later
"""Object images for the oracle's adapters: byte blobs of real objects read from the player's installation (never
stored in the repository; they go to the private oracle data root)."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path


def inflate(b: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i + 4 <= len(b):
        n = struct.unpack_from("<i", b, i)[0]
        i += 4
        out += zlib.decompress(b[i:i + n])
        i += n
    return bytes(out)


def level_file(game: Path, name: str) -> bytes:
    for sub in ("data/resources", "data/Resources"):
        p = game / sub / name
        if p.exists():
            return inflate(p.read_bytes())
    raise FileNotFoundError(name)


def height_field(game: Path) -> bytes:
    """Level 100's CHeightField record (0x13dc bytes) followed by its 64 * 64 * 81 signed 16-bit heights."""
    d = level_file(game, "100_res_PC.aya")
    p = 0
    while True:
        tag, size = struct.unpack_from("<4sI", d, p)
        p += 8
        if tag == b"ERES":
            break
        p += size
    p += 8 + 4
    for _ in range(7):
        p += 16
        data, _, u8, _, ts, num = struct.unpack_from("<IIIiii", d, p)
        p += 0x4C
        if data:
            p += 8 + num * ts
        if u8:
            p += 8 + num * 1024
    p += 8 + 4 + 16
    rec = d[p:p + 0x13DC]
    p += 0x13DC + 8
    return rec + d[p:p + 64 * 64 * 81 * 2]


def make(game: Path, out: Path) -> None:
    (out / "hf.bin").write_bytes(height_field(game))
