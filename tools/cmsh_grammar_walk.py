#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Walk PC CMSH mesh streams with the loader grammar in
reverse-engineering/asset-formats/cmsh-fields.md and prove it accounts for every byte.

Each `.aya` mesh file is inflated (reverse-engineering/asset-formats/aya-container.md) and parsed in the loader's order:
every leaf payload must be consumed exactly and the stream must end where the grammar ends. The report counts the tag
seen in each grammar slot and pins the corpus with a manifest digest (SHA-256 over sorted "name sha256" lines). The
install is only read.

With --compose it also checks the animation lanes (reverse-engineering/asset-formats/cmsh-animation-keys.md): each
part's cached model-space frames (CPOS, CORI) must equal its parent-relative keys (VHFM, HORI, HPOS) composed down the
hierarchy, to within single-precision rounding.

Run:  python ./tools/cmsh_grammar_walk.py --game GAME_FOLDER    (or set BEA_GAME to the game folder)
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import os
import struct
import sys
import zlib
from pathlib import Path

MESH_RECORD, PART_RECORD, VB_RECORD = 372, 316, 296


class GrammarError(ValueError):
    pass


def inflate_aya(data: bytes) -> bytes:
    """Concatenated members of u32le stored length + zlib stream."""
    out, pos = bytearray(), 0
    while pos < len(data):
        if pos + 4 > len(data):
            raise GrammarError("truncated AYA member length")
        (length,) = struct.unpack_from("<I", data, pos)
        member = data[pos + 4:pos + 4 + length]
        if length == 0 or len(member) != length:
            raise GrammarError("bad AYA member length")
        out += zlib.decompress(member)
        pos += 4 + length
    return bytes(out)


class Stream:
    """The loader's reader: a header is read, then exactly the grammar's bytes of its payload."""

    def __init__(self, data: bytes, slots: dict[str, collections.Counter]):
        self.data, self.pos, self.size, self.used, self.slots = data, 0, 0, 0, slots
        self.meshes: list[list[dict]] = []  # each mesh's parts' animation lanes, in part order

    def header(self, slot: str) -> str:
        if self.pos + 8 > len(self.data):
            raise GrammarError(f"stream ends before the {slot} header")
        tag = self.data[self.pos:self.pos + 4].decode("latin-1")
        (self.size,) = struct.unpack_from("<I", self.data, self.pos + 4)
        self.pos += 8
        self.used = 0
        self.slots[slot][tag] += 1
        return tag

    def take(self, count: int) -> bytes:
        if count < 0 or self.used + count > self.size or self.pos + count > len(self.data):
            raise GrammarError(f"read of {count} bytes runs past the chunk at offset {self.pos}")
        self.used += count
        chunk = self.data[self.pos:self.pos + count]
        self.pos += count
        return chunk

    def skip(self) -> None:
        self.pos += self.size - self.used
        self.used = self.size


def i32(record: bytes, offset: int) -> int:
    return struct.unpack_from("<i", record, offset)[0]


def floats(data: bytes) -> list[float]:
    return list(struct.unpack(f"<{len(data) // 4}f", data))


def walk_mesh(s: Stream) -> None:
    s.meshes.append([])
    s.header("mesh")
    mesh = s.take(MESH_RECORD)
    textures, chained, sequences, modes, emitters, parts = (i32(mesh, o) for o in (0x04, 0x08, 0x0C, 0x14, 0x1C, 0x15C))
    s.header("mesh textures")
    records = s.take(36 * textures)
    for t in range(textures):
        frames = i32(records, 36 * t + 8)
        s.header("texture wrapper")
        s.header("texture lanes")
        s.take(4 * 5 * frames + 128)
    for _ in range(parts):
        walk_part(s)
    if sequences > 0:
        s.header("sequences")
        table = s.take(12 * sequences)
        for q in range(sequences):
            if i32(table, 12 * q):
                s.header("sequence camera")
                s.take(4)
    if modes > 0:
        s.header("animation modes")
        s.take(36 * modes)
    walk_box(s, "mesh")
    if emitters > 0:
        s.header("emitters")
        size = i32(s.take(4), 0)
        for _ in range(emitters):
            if i32(s.take(size), 0x40):
                s.take(4)
    if chained:
        s.header("chained mesh")
        walk_mesh(s)


def walk_box(s: Stream, owner: str) -> None:
    s.header(f"{owner} box wrapper")
    s.header(f"{owner} box")
    s.take(40)


def walk_part(s: Stream) -> None:
    s.header("part wrapper")
    s.header("part")
    part = s.take(s.size)
    if len(part) < PART_RECORD:
        raise GrammarError(f"part record of {len(part)} bytes")
    f = lambda offset: i32(part, offset)
    dvertices, pvertices, triangles, aframes, vframes, hframes, bones = (f(o) for o in range(0xA8, 0xC4, 4))
    lanes = {"vframes": vframes, "cached": f(0x118), "parent": None}
    s.meshes[-1].append(lanes)
    if dvertices > 0:
        s.header("dvertices")
        s.take(i32(s.take(4), 0) * dvertices)
    if triangles > 0:
        s.header("triangles")
        s.take(12 * triangles)
    if pvertices > 0:
        s.header("pvertices")
        s.take(16 * pvertices * aframes)
    if f(0x90) > 0:
        s.header("children")
        s.take(4 * f(0x90))
    if f(0x98):
        s.header("parent")
        lanes["parent"] = i32(s.take(4), 0)
    if f(0x9C):
        s.header("chain next")
        s.take(4)
    walk_box(s, "part")
    if vframes > 0:
        s.header("virtual frame map")
        lanes["map"] = s.take(vframes)
    if hframes > 0:
        if f(0x10C):
            if s.header("frame orientations") != "HORI":
                raise GrammarError("the frame-orientation slot is not HORI")
            lanes["orientations"] = floats(s.take(48 * hframes))
        if f(0xC8):
            s.header("frame positions")
            lanes["positions"] = floats(s.take(16 * hframes))
        if f(0xCC):
            s.header("frame fields of view")
            s.take(4 * hframes)
    if bones > 0:
        s.header("bones")
        s.take(4 * bones)
        if f(0xD4):
            s.header("bone weights")
            s.take(4 * bones * pvertices)
        if f(0xD8):
            s.header("bone slots")
            s.take(12 * pvertices)
    if f(0x100):
        walk_grid(s)
    if f(0x104):
        s.header("cached positions")
        lanes["cached positions"] = floats(s.take(16 * f(0x118)))
    if f(0x108):
        if s.header("cached orientations") != "CORI":
            raise GrammarError("the cached-orientation slot is not CORI")
        lanes["cached orientations"] = floats(s.take(48 * f(0x118)))
    if f(0x124):
        s.header("reference")
        s.take(4)
    walk_vertex_buffer(s)


def walk_grid(s: Stream) -> None:
    s.header("grid wrapper")
    s.header("grid")
    grid = s.take(s.size)
    width, height = i32(grid, 0x68), i32(grid, 0x6C)
    s.header("grid sizes")
    s.take(8)
    for _ in range(width * height):
        s.header("grid cell")
        if i32(s.take(4), 0) == 1:
            s.header("grid list wrapper")
            s.header("grid list")
            s.take(2 * i32(s.take(4), 0))
    s.header("grid triangle count")
    triangles = i32(s.take(4), 0)
    s.header("grid triangles")
    for _ in range(triangles):
        s.header("grid triangle")
        s.take(12)
    s.header("grid vertex count")
    for _ in range(i32(s.take(4), 0)):
        s.header("grid vertex")
        s.take(6)


def walk_vertex_buffer(s: Stream) -> None:
    s.header("vertex buffer wrapper")
    s.header("vertex buffer")
    vb = s.take(VB_RECORD)
    pieces, stride = i32(vb, 0x108), i32(vb, 0x114)
    for piece in range(pieces):
        s.header("piece counts")
        counts = struct.unpack("<6i", s.take(24))
        s.header("piece indices")
        s.take(2 * counts[2])
        s.header("piece vertices")
        if piece == 0:
            s.take(stride * counts[3])
        else:
            s.skip()
        s.header("piece textures")
        s.take(24)


def walk_stream(data: bytes, slots: dict[str, collections.Counter]) -> list[list[dict]]:
    s = Stream(data, slots)
    walk_mesh(s)
    if s.pos != len(data):
        raise GrammarError(f"the grammar ends at byte {s.pos} of {len(data)}")
    return s.meshes


def key(part: dict, frame: int) -> tuple[list[list[float]], list[float]]:
    """A part's parent-relative key at a virtual frame: the frame is clamped, then mapped through VHFM."""
    k = part["map"][min(frame, part["vframes"] - 1)]
    o = part["orientations"][12 * k:12 * k + 12]
    return [o[0:3], o[4:7], o[8:11]], part["positions"][4 * k:4 * k + 3]


def model_space(parts: list[dict], index: int, frame: int) -> tuple[list[list[float]], list[float]]:
    """Composes keys from the root: position = Pp + Op p, orientation = Op O (column vectors, rows as stored)."""
    part = parts[index]
    if part["parent"] is None:
        po, pp = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], [0.0, 0.0, 0.0]
    else:
        po, pp = model_space(parts, part["parent"], frame)
    o, p = key(part, frame)
    position = [pp[r] + sum(po[r][c] * p[c] for c in range(3)) for r in range(3)]
    orientation = [[sum(po[r][k] * o[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
    return orientation, position


def check_caches(meshes: list[list[dict]], totals: collections.Counter, worst: list[float]) -> None:
    for parts in meshes:
        for index, part in enumerate(parts):
            for frame in range(part["cached"]):
                orientation, position = model_space(parts, index, frame)
                if "cached positions" in part:
                    stored = part["cached positions"][4 * frame:4 * frame + 3]
                    scale = 1.0 + max(abs(v) for v in position)
                    error = max(abs(a - b) for a, b in zip(stored, position)) / scale
                    worst[0] = max(worst[0], error)
                    totals["position frames" if error <= 1e-5 else "position mismatches"] += 1
                if "cached orientations" in part:
                    stored = part["cached orientations"][12 * frame:12 * frame + 12]
                    error = max(abs(stored[4 * r + c] - orientation[r][c]) for r in range(3) for c in range(3))
                    worst[1] = max(worst[1], error)
                    totals["orientation frames" if error <= 1e-5 else "orientation mismatches"] += 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"),
                        help="the game folder, which is only read (default: $BEA_GAME)")
    parser.add_argument("--compose", action="store_true",
                        help="also check every cached frame against the composed parent-relative keys")
    args = parser.parse_args(argv)
    if args.game is None:
        parser.error("name the game folder with --game or BEA_GAME")
    args.game = Path(args.game)
    files = sorted((args.game / "data/resources/meshes").glob("*.aya"))
    if not files:
        print(f"no mesh files under {args.game}", file=sys.stderr)
        return 2
    slots: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    digest, failures = hashlib.sha256(), []
    totals: collections.Counter = collections.Counter()
    worst = [0.0, 0.0]
    for path in files:
        raw = path.read_bytes()
        digest.update(f"{path.name} {hashlib.sha256(raw).hexdigest()}\n".encode())
        try:
            meshes = walk_stream(inflate_aya(raw), slots)
            if args.compose:
                check_caches(meshes, totals, worst)
        except (GrammarError, zlib.error, struct.error) as error:
            failures.append(f"{path.name}: {error}")
    print(f"CMSH_WALK: {len(files) - len(failures)} of {len(files)} streams parse to their exact end; "
          f"manifest {digest.hexdigest()}")
    for slot, tags in slots.items():
        print(f"  {slot:22} " + ", ".join(f"{tag} {count}" for tag, count in tags.most_common()))
    if args.compose:
        print(f"CMSH_COMPOSE: {totals['position frames']} cached positions and {totals['orientation frames']} cached "
              f"orientations equal the composed keys; {totals['position mismatches']} and "
              f"{totals['orientation mismatches']} differ; worst relative position error {worst[0]:.2e}, worst "
              f"orientation element error {worst[1]:.2e}")
    for failure in failures:
        print("FAIL " + failure)
    mismatched = totals["position mismatches"] + totals["orientation mismatches"]
    return 1 if failures or mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
