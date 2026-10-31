#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""PS2 meshes as the PC game's mesh stream, converted on the player's machine from their own PS2 copy.

A PS2 level archive carries its meshes inline: a `MESH` chunk is a `PMSH` wrapper (a 304-byte prefix that starts with the mesh's file name) followed by a chunk
stream with the PC grammar (tools/world_resources_encode.py and the preservation repository's cmsh-fields.md describe it): `CMSH`, `CMST`, one `MSHT` (holding a `TEXB`)
for each texture, one `MESP` for each part, then `CAMD`, `BBOX` and `CEMT` when present. The streams differ in three places:

- a part ends in `P2VB` where the PC has `PMVB`. `P2VB` = `MSVB` (u32 group count, u32 96) + one `MMPV` for each material group; `MMPV` = u32 1, `TEXR` (the PC group's six words),
  `NVRT` (u32 record count, u32 count of records that draw, f32) and `VRTS`: 112-byte records, each a vertex as it appears in a strip (normal at words 0 to 2, UV at 9 and 10,
  colour at 11, position at 24 to 26, and at word 27 a flag that is non-zero when the record does not draw a triangle);
- the PS2 `TEXB` holds the index of the texture's `TEXT` chunk in the archive where the PC holds the 128-byte name;
- the words that the loader replaces (pointers, padding) differ.

`convert` rewrites a PS2 stream as a PC stream: every chunk is copied except the `MSHT`s (the names come from the archive's `TEXT` chunks) and the `P2VB`s, which become `PMVB`s: one
shared vertex pool for the part (the distinct records of all its groups) and, for each group, the strip of triangles that the PS2 records draw, stitched into one PC index
strip with degenerate joins and the winding kept. The rules were measured on the player's own copy of the disc against the PC game's own meshes; none of that data is in this repository.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import world_resources_encode as enc  # noqa: E402

MAX_STREAM = 64 << 20
MAX_PARTS = 1024
MAX_GROUPS = 12                      # the PC's CMVB holds at most 12 pieces
MAX_RECORDS = 400_000
MAX_POOL = 0xFFFF                    # a PC index is a u16
PREFIX = 304                         # the PMSH payload before the CMSH stream
RECORD = 112
NAME_FIELD = 128
CMVB_BYTES = 296
PC_VERTEX = 36
PC_FVF = 0x152                       # position, normal, diffuse, one UV set (cmsh-fields.md, "Vertex-buffer record")
PC_TOPOLOGY = 4
TAG = re.compile(rb"[A-Za-z0-9_ ]{4}\Z")


class Ps2MeshError(ValueError):
    """The PS2 mesh is not in the layout this converter reads, or cannot be written as a PC mesh; the message says where."""


@dataclass(frozen=True)
class Group:
    texr: bytes          # the 24 bytes of the group's TEXR
    vertices: tuple      # the PC vertex (36 bytes) of each record, in order
    draws: tuple         # False where the record's flag word is non-zero


@dataclass(frozen=True)
class Part:
    children: tuple      # (tag, payload) of every child of the MESP in order; the P2VB is (b"P2VB", None)
    groups: tuple        # of Group


@dataclass(frozen=True)
class Mesh:
    top: tuple           # ("MESP", Part) or (tag, payload) in file order; an MSHT is ("MSHT", (prefix20, texture index))


def _tile(buf, start: int, end: int, what: str) -> list:
    """[(tag, payload start, payload end)] for the chunks that fill [start, end) exactly."""
    out, at = [], start
    while at < end:
        if at + 8 > end:
            raise Ps2MeshError(f"{what}: a chunk header runs past the end at offset {at}")
        tag = bytes(buf[at:at + 4])
        if not TAG.match(tag):
            raise Ps2MeshError(f"{what}: not a chunk tag at offset {at}")
        size = struct.unpack_from("<I", buf, at + 4)[0]
        if at + 8 + size > end:
            raise Ps2MeshError(f"{what}: chunk {tag.decode('ascii')} at offset {at} runs past the end")
        out.append((tag.decode("ascii"), at + 8, at + 8 + size))
        at += 8 + size
    return out


def _chunk(tag: str, payload: bytes) -> bytes:
    return tag.encode("ascii") + struct.pack("<I", len(payload)) + payload


def _group(buf, start: int, end: int, where: str) -> Group:
    body = bytes(buf[start:end])
    if len(body) < 4 + 8 + 24 + 8 + 12 + 8 or struct.unpack_from("<I", body, 0)[0] != 1:
        raise Ps2MeshError(f"{where}: not the usual MMPV layout")
    kids = _tile(body, 4, len(body), where)
    if [k[0] for k in kids] != ["TEXR", "NVRT", "VRTS"] or kids[0][2] - kids[0][1] != 24 or kids[1][2] - kids[1][1] != 12:
        raise Ps2MeshError(f"{where}: the chunks of an MMPV are TEXR (24 bytes), NVRT (12) and VRTS")
    texr = body[kids[0][1]:kids[0][2]]
    count, kicks, _scale = struct.unpack_from("<IIf", body, kids[1][1])
    vrts = body[kids[2][1]:kids[2][2]]
    if count > MAX_RECORDS or len(vrts) != RECORD * count:
        raise Ps2MeshError(f"{where}: VRTS holds {len(vrts)} bytes for {count} records of {RECORD}")
    vertices, draws = [], []
    for n in range(count):
        w = struct.unpack_from("<28I", vrts, n * RECORD)
        vertices.append(struct.pack("<3I3II2I", w[24], w[25], w[26], w[0], w[1], w[2], w[11], w[9], w[10]))
        draws.append(w[27] == 0)
    if sum(draws) != kicks:
        raise Ps2MeshError(f"{where}: NVRT says {kicks} records draw, the flags say {sum(draws)}")
    return Group(texr, tuple(vertices), tuple(draws))


def _part(buf, start: int, end: int, where: str) -> Part:
    children, groups, seen = [], (), False
    for tag, a, b in _tile(buf, start, end, where):
        if tag != "P2VB":
            children.append((tag, bytes(buf[a:b])))
            continue
        if seen:
            raise Ps2MeshError(f"{where}: two P2VB chunks")
        seen = True
        children.append((tag, None))
        kids = _tile(buf, a, b, where + " P2VB")
        if not kids or kids[0][0] != "MSVB" or kids[0][2] - kids[0][1] != 8:
            raise Ps2MeshError(f"{where}: a P2VB starts with its 8-byte MSVB")
        count, marker = struct.unpack_from("<II", buf, kids[0][1])
        if marker != 96 or count > MAX_GROUPS or [k[0] for k in kids[1:]] != ["MMPV"] * count:
            raise Ps2MeshError(f"{where}: the MSVB names {count} groups and the P2VB holds {len(kids) - 1} MMPV chunks")
        groups = tuple(_group(buf, k[1], k[2], f"{where} group {i}") for i, k in enumerate(kids[1:]))
    if not seen:
        raise Ps2MeshError(f"{where}: no P2VB")
    return Part(tuple(children), groups)


def mesh_stream(pmsh_payload: bytes) -> bytes:
    """The CMSH stream of a `PMSH` payload (the prefix holds the mesh's name)."""
    if len(pmsh_payload) <= PREFIX + 8 or pmsh_payload[PREFIX:PREFIX + 4] != b"CMSH":
        raise Ps2MeshError("the PMSH payload does not hold a CMSH stream after its 304-byte prefix")
    return pmsh_payload[PREFIX:]


def parse(stream: bytes) -> Mesh:
    if len(stream) > MAX_STREAM:
        raise Ps2MeshError(f"the mesh is {len(stream)} bytes, more than the {MAX_STREAM}-byte ceiling")
    top, parts = [], 0
    for tag, a, b in _tile(stream, 0, len(stream), "mesh"):
        if tag == "MESP":
            parts += 1
            if parts > MAX_PARTS:
                raise Ps2MeshError(f"more than {MAX_PARTS} parts")
            top.append(("MESP", _part(stream, a, b, f"part {parts - 1}")))
        elif tag == "MSHT":
            kids = _tile(stream, a, b, "MSHT")
            if [k[0] for k in kids] != ["TEXB"] or kids[0][2] - kids[0][1] != 24:
                raise Ps2MeshError("an MSHT of a PS2 mesh holds one 24-byte TEXB")
            texb = stream[kids[0][1]:kids[0][2]]
            top.append(("MSHT", (texb[:20], struct.unpack_from("<I", texb, 20)[0])))
        else:
            top.append((tag, bytes(stream[a:b])))
    if not top or top[0][0] != "CMSH":
        raise Ps2MeshError("a mesh stream starts with CMSH")
    return Mesh(tuple(top))


# ---- the PC side ----------------------------------------------------------------------------------------------------------
def cmvb(groups: int) -> bytes:
    """The 296-byte vertex-buffer record of a rigid part with `groups` pieces: the saving tool's pointers are filled with non-zero stand-ins for the pieces in use (the loader
    tests them only for zero and replaces them), the part word holds the marker every PC file has, and stride, vertex format and primitive type are set when there is a piece."""
    if not 0 <= groups <= MAX_GROUPS:
        raise Ps2MeshError(f"{groups} groups")
    b = bytearray(CMVB_BYTES)
    for g in range(groups):
        struct.pack_into("<I", b, 8 + 4 * g, 0x01000000 + 0x100 * g)
    struct.pack_into("<i", b, 0x108, groups)
    struct.pack_into("<I", b, 0x10C, 0xDEAD)
    if groups:
        struct.pack_into("<III", b, 0x114, PC_VERTEX, PC_FVF, PC_TOPOLOGY)
    return bytes(b)


def strip(vertex_ids: Sequence[int], draws: Sequence[bool]) -> list:
    """The PC index strip for one group: its records as indices into the part's pool, the triangles that draw kept in order with their winding, runs of consecutive triangles
    sharing their indices and the runs joined by degenerate pairs. A triangle at record i is (i-2, i-1, i), wound by the parity of i, and does not draw when the record's flag is
    set or two of its vertices are one."""
    n = len(vertex_ids)

    def draws_at(i: int) -> bool:
        return draws[i] and len({vertex_ids[i - 2], vertex_ids[i - 1], vertex_ids[i]}) == 3

    out, i = [], 2
    while i < n:
        if not draws_at(i):
            i += 1
            continue
        a = i
        while i + 1 < n and draws_at(i + 1):
            i += 1
        run = list(vertex_ids[a - 2:i + 1])
        if out:
            out += [out[-1], run[0]]                 # the join: ... L, L, F, F, ...: every triangle that spans it has a repeated vertex
        if (len(out) & 1) != (a & 1):                # the run's first index goes to position len(out): its first triangle must be wound as the PS2 winds it
            out.append(run[0])
        out += run
        i += 1
    return out


def pmvb(groups: Sequence[Group]) -> bytes:
    """The PC `PMVB` payload for a part: CMVB, then for each group MMPT, IBUF, VBUF (the pool, in the first group only) and TEXR."""
    if not groups:
        return _chunk("CMVB", cmvb(0))
    pool, index = [], {}
    for g in groups:
        for v in g.vertices:
            if v not in index:
                index[v] = len(pool)
                pool.append(v)
    if len(pool) > MAX_POOL:
        raise Ps2MeshError(f"a part's vertex pool holds {len(pool)} vertices, more than a PC index can name")
    pool_bytes = b"".join(pool)
    out = [_chunk("CMVB", cmvb(len(groups)))]
    for n, g in enumerate(groups):
        s = strip([index[v] for v in g.vertices], g.draws)
        if len(s) < 3:
            raise Ps2MeshError(f"group {n}: no triangle draws")
        out.append(_chunk("MMPT", struct.pack("<6I", len(pool_bytes), 2 * len(s), len(s), len(pool), len(s) - 2, 1)))
        out.append(_chunk("IBUF", struct.pack(f"<{len(s)}H", *s)))
        out.append(_chunk("VBUF", pool_bytes if n == 0 else b""))
        out.append(_chunk("TEXR", g.texr))
    return b"".join(out)


def convert(stream: bytes, texture_names: Sequence[str]) -> bytes:
    """A PS2 mesh stream as the PC mesh stream. `texture_names` are the names of the archive's TEXT chunks, in archive order."""
    mesh = parse(stream)
    out = []
    for tag, value in mesh.top:
        if tag == "MESP":
            out.append(_chunk("MESP", b"".join(_chunk("PMVB", pmvb(value.groups)) if ctag == "P2VB" else _chunk(ctag, payload) for ctag, payload in value.children)))
        elif tag == "MSHT":
            prefix, at = value
            if at >= len(texture_names):
                raise Ps2MeshError(f"a texture binding names TEXT chunk {at}, and the archive has {len(texture_names)}")
            name = texture_names[at].encode("latin-1")
            if len(name) >= NAME_FIELD:
                raise Ps2MeshError(f"texture name of {len(name)} bytes does not fit the {NAME_FIELD}-byte field")
            out.append(_chunk("MSHT", _chunk("TEXB", prefix + name.ljust(NAME_FIELD, b"\0"))))
        else:
            out.append(_chunk(tag, value))
    return b"".join(out)


# ---- the PC mesh read back, and the comparison used by the tests and the census --------------------------------------------
def pc_parts(stream: bytes) -> list:
    """For each part of a PC mesh stream: None (no geometry) or (pool of 36-byte vertices, [strip of indices], [TEXR payload]) for rigid parts."""
    out = []
    for tag, a, b in _tile(stream, 0, len(stream), "PC mesh"):
        if tag != "MESP":
            continue
        pm = [k for k in _tile(stream, a, b, "part") if k[0] == "PMVB"]
        if len(pm) != 1:
            raise Ps2MeshError("a PC part has one PMVB")
        kids = _tile(stream, pm[0][1], pm[0][2], "PMVB")
        head = stream[kids[0][1]:kids[0][2]]
        groups = head[0x108] if len(head) == CMVB_BYTES else -1
        if kids[0][0] != "CMVB" or groups < 0:
            raise Ps2MeshError("a PMVB starts with its 296-byte CMVB")
        if groups == 0:
            out.append(None)
            continue
        if struct.unpack_from("<I", head, 0x114)[0] != PC_VERTEX:
            raise Ps2MeshError("only the rigid 36-byte vertex is read")
        pool, strips, texrs = b"", [], []
        for tg, x, y in kids[1:]:
            if tg == "IBUF":
                strips.append(list(struct.unpack_from(f"<{(y - x) // 2}H", stream, x)))
            elif tg == "VBUF" and y > x and not pool:
                pool = stream[x:y]
            elif tg == "TEXR":
                texrs.append(stream[x:y])
        out.append(([pool[i:i + PC_VERTEX] for i in range(0, len(pool), PC_VERTEX)], strips, texrs))
    return out


QUANTUM = 1e4


def vertex_key(vertex: bytes) -> tuple:
    """A PC vertex as a comparable value: its floats rounded to 1e-4 (the PS2 and PC exports of one model differ in the last bits), a non-finite float by its bits."""
    words, floats = struct.unpack("<9I", vertex), struct.unpack("<9f", vertex)
    return tuple(words[i] if i == 6 else round(floats[i] * QUANTUM) if math.isfinite(floats[i]) else ("raw", words[i]) for i in range(9))


def triangles(vertices: Sequence, strip_indices: Sequence[int]) -> collections.Counter:
    """The oriented triangles of a PC strip (consecutive triples, every other one flipped, degenerate ones dropped), as a count of canonical rotations of vertex keys. A triangle is
    degenerate when two of its vertices are the same by key: a pool may hold one vertex twice, and a strip may name either."""
    out = collections.Counter()
    keys = [vertex_key(v) for v in vertices]
    for i in range(len(strip_indices) - 2):
        a, b, c = keys[strip_indices[i]], keys[strip_indices[i + 1]], keys[strip_indices[i + 2]]
        if len({a, b, c}) < 3:
            continue
        if i & 1:
            b, c = c, b
        t = (a, b, c)
        m = min(range(3), key=lambda k: repr(t[k]))
        out[t[m:] + t[:m]] += 1
    return out


# ---- the archive side -------------------------------------------------------------------------------------------------------
def archive_texture_names(member: bytes) -> list:
    """The names of the TEXT chunks of a level archive, in archive order (a PS2 mesh names its textures by this index)."""
    names = []
    for tag, at, _size in enc.chunks(member):
        if tag == "TEXT":
            payload = member[at + 8:at + 8 + struct.unpack_from("<I", member, at + 4)[0]]
            names.append(payload[8:8 + 160].split(b"\0")[0].decode("latin-1"))
    return names


def archive_meshes(member: bytes):
    """(name, PMSH payload) of each MESH chunk of a level archive."""
    for tag, at, _size in enc.chunks(member):
        if tag == "MESH":
            size = struct.unpack_from("<I", member, at + 4)[0]
            payload = member[at + 8:at + 8 + size]
            if b"\0" not in payload[:PREFIX]:
                continue
            yield payload[:payload.index(b"\0")].decode("latin-1"), payload


def convert_member_mesh(member: bytes, name: str) -> bytes:
    """The PC mesh stream of the mesh called `name` in a PS2 level archive."""
    for found, payload in archive_meshes(member):
        if found.lower() == name.lower():
            return convert(mesh_stream(payload), archive_texture_names(member))
    raise Ps2MeshError("the archive has no mesh of that name")


def compare(ps2_stream: bytes, texture_names: Sequence[str], pc_stream: bytes) -> dict:
    """Counts of how the converted PS2 mesh agrees with a PC mesh of the same name: parts, parts with geometry, parts whose distinct vertices are the PC part's, groups whose oriented
    triangle set is the PC group's, and the triangles in the groups that differ."""
    mine, theirs = pc_parts(convert(ps2_stream, texture_names)), pc_parts(pc_stream)
    r = collections.Counter(parts=len(mine))
    if len(mine) != len(theirs):
        r["part count differs"] = 1
        return dict(r)
    for a, b in zip(mine, theirs):
        if a is None or b is None:
            if (a is None) != (b is None):
                r["geometry on one side only"] += 1
            continue
        r["geometry parts"] += 1
        r["vertex sets equal"] += {vertex_key(v) for v in a[0]} == {vertex_key(v) for v in b[0]}
        if len(a[1]) != len(b[1]):
            r["group count differs"] += 1
            continue
        for sa, sb in zip(a[1], b[1]):
            r["groups"] += 1
            ta, tb = triangles(a[0], sa), triangles(b[0], sb)
            if ta == tb:
                r["groups equal"] += 1
            else:
                r["triangles in differing groups"] += sum(((ta - tb) + (tb - ta)).values())
    return dict(r)


# ---- command line -----------------------------------------------------------------------------------------------------------
def _member(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:4] != b"LVLR":
        raise Ps2MeshError(f"{path.name} is not an extracted level archive (LVLR)")
    return data


def cmd_convert(args) -> int:
    stream = convert_member_mesh(_member(args.member), args.name)
    if args.out.exists() or args.out.is_symlink():
        raise Ps2MeshError(f"{args.out} exists already")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "xb") as handle:
        handle.write(stream)
    print(f"wrote {len(stream)} bytes, sha256 {hashlib.sha256(stream).hexdigest()}")
    return 0


def cmd_census(args) -> int:
    """Convert every mesh of the given members that has a loose PC twin and compare: counts only (the rule of this repository: nothing from the disc is printed)."""
    import zlib
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rebuild" / "tools"))
    import cmsh_static_preview as cs
    loose = {p.name.lower(): p for p in (args.game / "data" / "resources" / "meshes").glob("*.aya")}
    total, seen, bad = collections.Counter(), set(), []
    for member_path in args.members:
        member = _member(member_path)
        names = archive_texture_names(member)
        for name, payload in archive_meshes(member):
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            twin = loose.get(f"m_{name}.aya".lower())
            if twin is None:
                total["meshes without a loose PC twin"] += 1
                continue
            try:
                result = compare(mesh_stream(payload), names, cs.inflate_aya(twin.read_bytes()))
            except (Ps2MeshError, cs.CmshProfileError, zlib.error, struct.error, ValueError) as error:
                total["meshes that could not be converted or read"] += 1
                bad.append((hashlib.sha1(name.encode()).hexdigest()[:6], str(error)[:60]))
                continue
            total["meshes compared"] += 1
            for k, v in result.items():
                total[k] += v
    print(json.dumps(dict(sorted(total.items())), indent=1))
    if bad:
        print("not converted or not readable (name hash, reason):", bad[:12])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("convert", help="write the PC mesh stream of one mesh of an extracted PS2 level archive")
    c.add_argument("member", type=Path)
    c.add_argument("name")
    c.add_argument("--out", type=Path, required=True)
    k = sub.add_parser("census", help="convert every mesh that has a loose PC twin and print how many agree (counts only)")
    k.add_argument("members", type=Path, nargs="+")
    k.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ)
    args = parser.parse_args(argv)
    if args.command == "census":
        args.game = Path(args.game)
    return {"convert": cmd_convert, "census": cmd_census}[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Ps2MeshError, enc.EncodeError) as error:
        print(f"ps2 mesh: {error}", file=sys.stderr)
        sys.exit(2)
