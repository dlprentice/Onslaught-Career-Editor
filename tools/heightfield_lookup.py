#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The terrain's height under a position, as the game computes it (pure functions over bytes; no retail bytes kept).

A level archive's ERES chunk holds the terrain: a 64 x 64 grid of tiles of 9 x 9 signed 16-bit height samples (one sample
per world unit; the ninth row and column of a tile repeat its neighbour's first) and a height scale. The game's lookup is
CHeightField::Collide (0x0047eb80) and the bilinear read it calls (0x0047eb00), cited by function as the decompilation
(onslaught-decomp) describes them; this module is written from that description and copies no source. It adds a bias to each
coordinate and a large constant, reads the float's bits as 8.8 fixed point, answers 0.0 for a position outside 0 to 512 on
either axis (a check of those bits), and interpolates the four samples around the position with 8-bit fractions (arithmetic
shifts, so a step down rounds down) before multiplying by the height scale. Each float operation is rounded to 32 bits, as
the game's single-precision floating point does, so the Companion's C# port (companion/OnslaughtToolkit.Godot/Levels/
Heightfield.cs) is checked against this module on generated vectors (tools/level_editor_vectors.py) and, locally, on every
retail terrain. Heights are in world units with Z pointing down: the ground under the player's start in level 100 is about
-10. A position that is not finite answers 0.0 here and in the port (the game's own answer for one is whatever its bit
tricks make of it).

    python tools/heightfield_lookup.py ARCHIVE.aya X Y      the height under (X, Y) in a level archive's terrain
"""
from __future__ import annotations

import hashlib
import math
import struct
import sys
from pathlib import Path
from typing import NamedTuple

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import world_resources_decode as wrd  # noqa: E402

DecodeError = wrd.DecodeError
TILES, TILE_SAMPLES = wrd.HF_TILES, wrd.HF_SAMPLES  # 64 tiles a side, 9 x 9 samples each
SAMPLE_COUNT = TILES * TILES * TILE_SAMPLES * TILE_SAMPLES
SIZE = 512.0  # the square, in world units, that the lookup answers for
SCALE_AT, WATER_AT = 0x102C, 0x1034  # the height scale and the water level in the heightfield record (CHeightField::Load)
BASE = 49152.0  # 1.5 x 2^15: adding it leaves the float's low 8 mantissa bits holding the fixed-point fraction


def f32(value: float) -> float:
    """The value rounded to 32 bits (an overflow is an infinity, as in single-precision arithmetic)."""
    try:
        return struct.unpack("<f", struct.pack("<f", value))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


BIAS = f32(f32(0.49999) / 256)  # the game's constant 0x3afffeb0: it turns round-to-nearest into round-down
assert struct.unpack("<I", struct.pack("<f", BIAS))[0] == 0x3AFFFEB0


class Heightfield(NamedTuple):
    samples: tuple[int, ...]  # ((tile_x * 64 + tile_y) * 9 + row) * 9 + column
    scale: float  # a float32
    water: float  # a float32

    def samples_sha256(self) -> str:
        return hashlib.sha256(struct.pack(f"<{SAMPLE_COUNT}h", *self.samples)).hexdigest()


def read_heightfield(eres: bytes) -> Heightfield:
    """The heightfield of an ERES payload (CEngine::Deserialize's order, as world_resources_decode.parse_eres reads it)."""
    r = wrd.Reader(eres)
    tag, _size = r.chunk_header()
    if tag != "ENGN":
        raise DecodeError(f"ERES starts with {tag!r}, CEngine::Deserialize asserts ENGN")
    count = r.i32()
    if count != 7:
        raise DecodeError(f"{count} mixer mips (N_MAPMIPS is 7)")
    for _ in range(count):
        r.chunk_header()
        r.chunk_header()
        fields = struct.unpack(wrd.MAPTEX_FMT, r.take(0x4C))
        data_ptr, extra_ptr, tex_size, num = fields[0], fields[2], fields[4], fields[5]
        if data_ptr:
            r.chunk_header()
            r.take(num * tex_size)
        if extra_ptr:
            r.chunk_header()
            r.take(num * 1024)
    r.chunk_header()
    r.i32()  # the map number
    r.chunk_header()
    r.chunk_header()
    record = r.take(wrd.HEIGHTFIELD_SIZE)
    r.chunk_header()
    raw = r.take(SAMPLE_COUNT * 2)
    r.chunk_header()
    for _ in range(wrd.MIXER_MAP_SLOTS):
        r.chunk_header()
        r.chunk_header()
        slot = r.take(wrd.MIXER_SLOT_SIZE)
        n, data_ptr = struct.unpack_from("<iI", slot, 0)
        if data_ptr:
            r.chunk_header()
            r.take(n * 81)
    r.chunk_header()
    r.take(wrd.MIXER_MAP_SIZE)
    if r.pos != len(eres):
        raise DecodeError(f"ERES has {len(eres) - r.pos} unread bytes")
    return Heightfield(struct.unpack(f"<{SAMPLE_COUNT}h", raw), struct.unpack_from("<f", record, SCALE_AT)[0],
                       struct.unpack_from("<f", record, WATER_AT)[0])


def packed(value: float) -> int:
    """value - bias + 49152 in 32-bit floats, as the float's own 32 bits: 8.8 fixed point of the position."""
    shifted = f32(f32(value) - BIAS)
    return struct.unpack("<i", struct.pack("<f", f32(shifted + BASE)))[0]


def interpolate(samples: tuple[int, ...], px: int, py: int) -> int:
    """The bilinear read (@0x0047eb00): px and py are the packed positions; the sample units are the file's."""
    fx, fy = px & 255, py & 255
    at = ((((px >> 11) & 63) * 64 + ((py >> 11) & 63)) * 9 + ((py >> 8) & 7)) * 9 + ((px >> 8) & 7)
    top = samples[at] + (((samples[at + 1] - samples[at]) * fx) >> 8)
    bottom = samples[at + 9] + (((samples[at + 10] - samples[at + 9]) * fx) >> 8)
    return top + (((bottom - top) * fy) >> 8)


def height_at(field: Heightfield, x: float, y: float) -> float:
    """The height under (x, y) in world units (Z down), 0.0 outside the 0 to 512 square or for a position that is not finite."""
    if not (math.isfinite(f32(x)) and math.isfinite(f32(y))):
        return 0.0
    px, py = packed(x), packed(y)
    if (px | py) & 0x3E0000:
        return 0.0
    return f32(f32(float(interpolate(field.samples, px, py))) * field.scale)


def height_bits(field: Heightfield, x: float, y: float) -> int:
    """The 32 bits of height_at, for comparing a port exactly (a negative zero is not a zero)."""
    return struct.unpack("<I", struct.pack("<f", height_at(field, x, y)))[0]


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    members = wrd_archive_members(Path(argv[1]).read_bytes())
    chunk = next((payload for tag, payload in members if tag == "ERES"), None)
    if chunk is None:
        print("no ERES chunk in that archive", file=sys.stderr)
        return 1
    print(f"{height_at(read_heightfield(chunk), float(argv[2]), float(argv[3])):.6f}")
    return 0


def wrd_archive_members(source: bytes) -> list[tuple[str, bytes]]:
    import world_resources_encode as enc  # imported here: the lookup itself needs only the decoder

    stream = b"".join(enc.inflate(enc.read_members(source)))
    return [(tag, stream[at:at + size]) for tag, at, size in enc.chunks(stream)]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
