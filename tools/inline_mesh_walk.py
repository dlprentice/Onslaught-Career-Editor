#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The inline-mesh walker of the Onslaught CE mod loader, in Python (onslaught-ce, port/platform/common/mods.cpp: CheckInlineMesh, CheckMeshPart, CheckMeshGrid).

A level archive a mod ADDS (data/resources/NNN_res_PC.aya, NNN 850 to 899) may hold ONE MESH chunk whose reference carries no name: the mesh's data follows the chunk's 325
reference bytes, and the game reads it with CMesh::Deserialize. The loader walks that stream the way the readers take it, from the counts in the records they have just read and never
from a chunk's declared size (the grammar is onslaught-preservation/formats/cmsh-fields.md), and refuses it where they would read a count's worth of something that is not there.
One profile is admitted, the one the shipped rigid meshes have:
no cutscene sequences, no skeletal or camera parts, none of the older vertex and triangle arrays, 36-byte vertices in at most 12 pieces; meshes chained to it are admitted, up to 16 in all, each
framed as the game's own are. Every count, size and index is bounded, so a stream that passes cannot make the readers allocate, copy or index beyond what it holds. What the vertices, the matrices
or the texture names say is not looked at.

This module is a mirror of that walk for the stager, so that a mod folder is refused here, with the loader's own words, before the game is asked to refuse it. It must agree with the
loader's walk on every stream: the reason strings are the loader's, character for character, and tools/inline_mesh_walk_tests.py holds the cases of the loader's own tests. The loader is
the authority; a change of its profile is a change here in the same step. `check_inline_mesh(stream, first_id)` takes the bytes after the chunk's 325 reference bytes and the first mesh's runtime id and returns None
when the stream is a mesh or a chain of meshes of the profile, else the reason.
"""
from __future__ import annotations

import struct

MESH_MAX_BYTES = 16 << 20
MESH_MAX_TEXTURES = 16
MESH_MAX_PARTS = 512
MESH_MAX_ANIM_MODES = 8
MESH_MAX_EMITTERS = 512
MESH_MAX_VERTICES = 100000
MESH_MAX_INDICES = 600000
MESH_MAX_GROUPS = 1024
MESH_MAX_FRAMES = 65535
MESH_MAX_FRAME_SETS = 2
MESH_MAX_CELLS = 16384
MESH_MAX_GRID_TRIANGLES = 32767
MESH_MAX_GRID_INDICES = 1 << 20
MESH_MAX_GRID_VERTICES = 32767
MESH_MAX_CHAIN = 16


def _le32(b: bytes, at: int) -> int:
    return struct.unpack_from("<I", b, at)[0]


class _Cursor:
    """A run of chunk headers inside [at, end) of b: take() reads the next one, which must be `tag` and fit, and returns (payload offset, size), or None."""

    def __init__(self, b: bytes, at: int, end: int):
        self.b, self.at, self.end = b, at, end

    def take(self, tag: bytes):
        if self.end - self.at < 8 or self.b[self.at:self.at + 4] != tag:
            return None
        size = _le32(self.b, self.at + 4)
        if size > self.end - self.at - 8:
            return None
        payload = self.at + 8
        self.at += 8 + size
        return payload, size

    def done(self) -> bool:
        return self.at == self.end


def _take_box(m: _Cursor) -> bool:
    """The bounding box of a part or a mesh: a BBOX wrapper (48 bytes) around one 40-byte BBOX."""
    got = m.take(b"BBOX")
    if got is None or got[1] != 48:
        return False
    w = _Cursor(m.b, got[0], got[0] + got[1])
    inner = w.take(b"BBOX")
    return inner is not None and inner[1] == 40 and w.done()


def _check_grid(b: bytes, start: int, grid_size: int) -> str | None:
    """A part's collision grid, the payload of its PBKT: CPBT, SIZS, a PBCS for each cell, PLQT, a PBFK around a PBKE for each triangle, PBPN and a PBPP for each vertex."""
    g = _Cursor(b, start, start + grid_size)
    got = g.take(b"CPBT")
    if got is None or got[1] != 184:
        return "an inline mesh whose collision grid does not start with a 184-byte CPBT"
    p = got[0]
    width, height = _le32(b, p + 0x68), _le32(b, p + 0x6C)
    if not width or not height or width > MESH_MAX_CELLS or height > MESH_MAX_CELLS or width * height > MESH_MAX_CELLS:
        return "an inline mesh whose collision grid has a size out of bounds"
    got = g.take(b"SIZS")
    if got is None or got[1] != 8:
        return "an inline mesh whose collision grid has no 8-byte SIZS after its CPBT"
    lists, indices = _le32(b, got[0]), _le32(b, got[0] + 4)
    if lists > width * height or indices > MESH_MAX_GRID_INDICES:
        return "an inline mesh whose collision grid declares more lists or indices than it can hold"
    seen_lists = seen_indices = listed = 0
    used = bytearray(MESH_MAX_GRID_TRIANGLES)
    for _ in range(width * height):
        got = g.take(b"PBCS")
        if got is None or got[1] < 4:
            return "an inline mesh whose collision grid has fewer PBCS cells than its width and height"
        p, size = got
        present = _le32(b, p)
        if present > 1:
            return "an inline mesh whose collision grid has a cell that is neither present nor absent"
        if not present:
            if size != 4:
                return "an inline mesh whose collision grid has an absent cell with data"
            continue
        cell = _Cursor(b, p + 4, p + size)
        et = cell.take(b"PBET")
        if et is None or not cell.done():
            return "an inline mesh whose collision grid has a present cell that is not one PBET"
        lc = _Cursor(b, et[0], et[0] + et[1])
        sq = lc.take(b"PBSQ")
        if sq is None or not lc.done() or sq[1] < 4:
            return "an inline mesh whose collision grid has a PBET that is not one PBSQ"
        s, s_size = sq
        count = _le32(b, s)
        if count > MESH_MAX_GRID_INDICES or s_size != 4 + 2 * count:
            return "an inline mesh whose collision grid has a list whose size is not its count"
        for i in range(count):
            triangle = b[s + 4 + 2 * i] | b[s + 5 + 2 * i] << 8
            if triangle >= MESH_MAX_GRID_TRIANGLES:
                return "an inline mesh whose collision grid lists a triangle past 32767"
            used[triangle] = 1
            listed = max(listed, triangle + 1)
        seen_lists += 1
        seen_indices += count
        if seen_lists > lists or seen_indices > indices:
            return "an inline mesh whose collision grid holds more lists or indices than its SIZS declares"
    got = g.take(b"PLQT")
    if got is None or got[1] != 4:
        return "an inline mesh whose collision grid has no 4-byte PLQT after its cells"
    triangles = _le32(b, got[0])
    if triangles > MESH_MAX_GRID_TRIANGLES or listed > triangles:
        return "an inline mesh whose collision grid lists a triangle it does not have, or has more than 32767"
    got = g.take(b"PBFK")
    if got is None:
        return "an inline mesh whose collision grid has no PBFK"
    tri = _Cursor(b, got[0], got[0] + got[1])
    max_vertex = 0
    for i in range(triangles):
        k = tri.take(b"PBKE")
        if k is None or k[1] != 12:
            return "an inline mesh whose collision grid has fewer 12-byte PBKE triangles than its count"
        for v in range(3):
            if not used[i]:
                break
            max_vertex = max(max_vertex, (b[k[0] + 4 + 2 * v] | b[k[0] + 5 + 2 * v] << 8) + 1)
    if not tri.done():
        return "an inline mesh whose collision grid has bytes in its PBFK after its triangles"
    got = g.take(b"PBPN")
    if got is None or got[1] != 4:
        return "an inline mesh whose collision grid has no 4-byte PBPN"
    vertices = _le32(b, got[0])
    if vertices > MESH_MAX_GRID_VERTICES or max_vertex > vertices:
        return "an inline mesh whose collision grid has a listed triangle that names a vertex it does not have"
    for _ in range(vertices):
        got = g.take(b"PBPP")
        if got is None or got[1] != 6:
            return "an inline mesh whose collision grid has fewer 6-byte PBPP vertices than its count"
    return None if g.done() else "an inline mesh whose collision grid has bytes after its last vertex"


def _check_part(b: bytes, start: int, part_size: int, parts: int, textures: int, totals: list) -> str | None:
    """A part (the payload of an MESP): the chunks CMeshPart's reader takes, in its order, each there as the part record says. `totals` is [vertices, indices, groups] of the whole mesh so far."""
    m = _Cursor(b, start, start + part_size)
    got = m.take(b"CMSP")
    if got is None or got[1] != 316:
        return "an inline mesh part that does not start with a 316-byte CMSP record"
    p = got[0]
    kind, children, vframes, hframes, cached = _le32(b, p + 0x8C), _le32(b, p + 0x90), _le32(b, p + 0xB8), _le32(b, p + 0xBC), _le32(b, p + 0x118)
    if kind < 1 or kind > 6 or kind == 3 or kind == 4:
        return "an inline mesh part that is skeletal or a camera (a normal, null, emitter or reference part is admitted)"
    if any(_le32(b, p + off) for off in (0x9C, 0xA0, 0xA4, 0xA8, 0xAC, 0xB0, 0xC0, 0xCC, 0xD0, 0xD4, 0xD8)):
        return "an inline mesh part with a chain, older-format vertices or triangles, bones or a field of view (none is admitted)"
    if _le32(b, p + 0xB4) > MESH_MAX_FRAME_SETS:
        return "an inline mesh part with more position sets than the shipped parts have (its frame-set count)"
    if not vframes:
        return "an inline mesh part with no virtual frames (every shipped part has some; the reader would keep the record's pointer to their map)"
    if not hframes:
        return "an inline mesh part with no hand frames (every shipped part has some; the reader would keep the record's pointers to their tables)"
    if children > parts or vframes > MESH_MAX_FRAMES or hframes > MESH_MAX_FRAMES or cached > MESH_MAX_FRAMES:
        return "an inline mesh part with a child, frame or cache count out of bounds"
    parent, grid = _le32(b, p + 0x98) != 0, _le32(b, p + 0x100) != 0
    cached_positions, cached_orientations = _le32(b, p + 0x104) != 0, _le32(b, p + 0x108) != 0
    orientations, positions, reference = _le32(b, p + 0x10C) != 0, _le32(b, p + 0xC8) != 0, _le32(b, p + 0x124) != 0
    if children:
        got = m.take(b"CHLD")
        if got is None or got[1] != 4 * children:
            return "an inline mesh part whose CHLD is not its child count"
        for i in range(children):
            if _le32(b, got[0] + 4 * i) >= parts:
                return "an inline mesh part with a child that is not a part of the mesh"
    if parent:
        got = m.take(b"PRNT")
        if got is None or got[1] != 4 or _le32(b, got[0]) >= parts:
            return "an inline mesh part whose PRNT is not one part of the mesh"
    if not _take_box(m):
        return "an inline mesh part without its bounding box"
    if vframes:
        got = m.take(b"VHFM")
        if got is None or got[1] != vframes:
            return "an inline mesh part whose VHFM is not its virtual-frame count"
    if hframes:
        if orientations:
            got = m.take(b"HORI")
            if got is None or got[1] != 48 * hframes:
                return "an inline mesh part whose HORI is not its frame count of matrices"
        if positions:
            got = m.take(b"HPOS")
            if got is None or got[1] != 16 * hframes:
                return "an inline mesh part whose HPOS is not its frame count of vectors"
    if grid:
        got = m.take(b"PBKT")
        if got is None:
            return "an inline mesh part that has a collision grid but no PBKT"
        bad = _check_grid(b, got[0], got[1])
        if bad:
            return bad
    if cached_positions:
        got = m.take(b"CPOS")
        if got is None or got[1] != 16 * cached:
            return "an inline mesh part whose CPOS is not its cached frame count of vectors"
    if cached_orientations:
        got = m.take(b"CORI")
        if got is None or got[1] != 48 * cached:
            return "an inline mesh part whose CORI is not its cached frame count of matrices"
    if reference:
        got = m.take(b"REFR")
        if got is None or got[1] != 4 or _le32(b, got[0]) >= parts:
            return "an inline mesh part whose REFR is not one part of the mesh"
    got = m.take(b"PMVB")
    if got is None:
        return "an inline mesh part without its PMVB"
    v = _Cursor(b, got[0], got[0] + got[1])
    got = v.take(b"CMVB")
    if got is None or got[1] != 296:
        return "an inline mesh part whose PMVB does not start with a 296-byte CMVB"
    p = got[0]
    pieces = _le32(b, p + 0x108)
    if pieces > 12:
        return "an inline mesh part with more than 12 vertex-buffer pieces"
    if _le32(b, p + 0x110):
        return "an inline mesh part whose vertex buffer carries a shader pointer (the reader would keep it and call it)"
    for slot in range(pieces, 64):
        if _le32(b, p + 8 + 4 * slot):
            return "an inline mesh part whose vertex buffer carries a piece pointer beyond its pieces (the destructor would free it)"
    if pieces and (_le32(b, p + 0x114) != 36 or _le32(b, p + 0x118) != 0x152 or _le32(b, p + 0x11C) != 4):
        return "an inline mesh part whose vertices are not the 36-byte format drawn as a strip"
    vertex_count = vertex_bytes = 0
    for piece in range(pieces):
        got = v.take(b"MMPT")
        if got is None or got[1] != 24:
            return "an inline mesh piece without a 24-byte MMPT"
        p = got[0]
        vb, ib, ic, vc, prims, built = struct.unpack_from("<6I", b, p)
        if built != 1 or ic < 3 or ic > 65535 or ib != 2 * ic or prims != ic - 2:
            return "an inline mesh piece whose MMPT counts disagree (built, index count and bytes, primitive count)"
        if not piece:
            if not vc or vc > 65535 or vb != 36 * vc:
                return "an inline mesh piece whose vertex count is zero, over 65535, or not its vertex bytes"
            vertex_count, vertex_bytes = vc, vb
            totals[0] += vc
        elif vb != vertex_bytes or vc != vertex_count:
            return "an inline mesh piece that does not share the first piece's vertices"
        totals[1] += ic
        totals[2] += 1
        if totals[2] > MESH_MAX_GROUPS or totals[0] > MESH_MAX_VERTICES or totals[1] > MESH_MAX_INDICES:
            return "an inline mesh with more than 100000 vertices, 600000 indices or 1024 pieces"
        got = v.take(b"IBUF")
        if got is None or got[1] != ib:
            return "an inline mesh piece whose IBUF is not its index bytes"
        if max(struct.unpack_from(f"<{ic}H", b, got[0])) >= vertex_count:
            return "an inline mesh piece with an index past its vertices"
        got = v.take(b"VBUF")
        if got is None or got[1] != (0 if piece else vertex_bytes):
            return "an inline mesh piece whose VBUF is not its vertices (the first piece) or empty (the others)"
        got = v.take(b"TEXR")
        if got is None or got[1] != 24:
            return "an inline mesh piece without a 24-byte TEXR"
        for slot in range(6):
            value = _le32(b, got[0] + 4 * slot)
            if value != 0xFFFFFFFF and value >= textures:
                return "an inline mesh piece with a texture slot that is not -1 or one of the mesh's textures"
    if not v.done():
        return "an inline mesh part with bytes in its PMVB after its last piece"
    return None if m.done() else "an inline mesh part with bytes after its vertex buffer"


def _check_mesh(c: _Cursor, totals: list) -> str | None:
    """One mesh of the stream, from its CMSH to its last chunk (the box, or the emitters after it); the cursor is left after it. `totals` is [vertices, indices, groups, chained]: the first three are the
    whole stream's, so the meshes of a chain share them, and the last is set from the record's next-in-chain word (a pointer, which the loader tests only for zero)."""
    b = c.b
    got = c.take(b"CMSH")
    if got is None or got[1] != 372:
        return "an inline mesh that does not start with a 372-byte CMSH record"
    p = got[0]
    textures, chain, sequences, anim_modes, emitters, parts = _le32(b, p + 4), _le32(b, p + 8), _le32(b, p + 0xC), _le32(b, p + 0x14), _le32(b, p + 0x1C), _le32(b, p + 0x15C)
    if b.find(b"\0", p + 0x24, p + 0x24 + 300) < 0:
        return "an inline mesh whose name is not terminated"
    if sequences:
        return "an inline mesh with cutscene sequences (not admitted)"
    totals[3] = 1 if chain else 0
    if textures > MESH_MAX_TEXTURES or anim_modes > MESH_MAX_ANIM_MODES or emitters > MESH_MAX_EMITTERS or not parts or parts > MESH_MAX_PARTS:
        return "an inline mesh with a texture, animation-mode, emitter or part count out of bounds"
    got = c.take(b"CMST")
    if got is None or got[1] != 36 * textures:
        return "an inline mesh whose CMST is not its texture count of 36-byte records"
    frames = []
    for i in range(textures):
        frames.append(_le32(b, got[0] + 36 * i + 8))
        if not frames[i] or frames[i] > 16:
            return "an inline mesh texture with no frames or more than 16"
    for i in range(textures):
        got = c.take(b"MSHT")
        if got is None:
            return "an inline mesh with fewer MSHT texture lists than its texture count"
        w = _Cursor(b, got[0], got[0] + got[1])
        t = w.take(b"TEXB")
        if t is None or not w.done() or t[1] != 20 * frames[i] + 128:
            return "an inline mesh whose MSHT is not one TEXB of five lanes for each frame and a 128-byte name"
        name = t[0] + 20 * frames[i]
        end = b.find(b"\0", name, name + 128)
        if end < 0 or end == name:
            return "an inline mesh texture whose name is empty or not terminated"
        if any(ch < 0x20 or ch >= 0x7F for ch in b[name:end]):
            return "an inline mesh texture whose name is not printable ASCII"
    for _ in range(parts):
        got = c.take(b"MESP")
        if got is None:
            return "an inline mesh with fewer MESP parts than its part count"
        bad = _check_part(b, got[0], got[1], parts, textures, totals)
        if bad:
            return bad
    if anim_modes:
        got = c.take(b"CAMD")
        if got is None or got[1] != 36 * anim_modes:
            return "an inline mesh whose CAMD is not its animation-mode count of 36-byte records"
    if not _take_box(c):
        return "an inline mesh without its bounding box"
    if emitters:
        got = c.take(b"CEMT")
        if got is None or got[1] < 4 or _le32(b, got[0]) != 336:
            return "an inline mesh whose CEMT does not start with the 336-byte emitter record size"
        p, size = got
        at = 4
        for _ in range(emitters):
            if size - at < 336:
                return "an inline mesh whose CEMT holds fewer emitters than its count"
            indexed = _le32(b, p + at + 0x40) != 0
            at += 336
            if indexed:
                if size - at < 4 or _le32(b, p + at) >= parts:
                    return "an inline mesh emitter whose part index is missing or not a part of the mesh"
                at += 4
        if at != size:
            return "an inline mesh whose CEMT has bytes after its last emitter"
    return None


def check_inline_mesh(stream: bytes, first_id: int = 0) -> str | None:
    """None when `stream` (the bytes after an unnamed MESH chunk's 325 reference bytes) is a mesh of the profile above, or a chain of them, else the reason (the loader's CheckInlineMesh). A mesh whose
    next-in-chain word is set is followed by the mesh it names, framed as the game's own chained inline meshes are (the 12 shipped chains hold 5 meshes each): a PMSH header and a PMS2 header, each around
    the rest of the stream, the 309-byte reference (an all-zero name, a runtime id of 20000 to 29999 that no other mesh of the chain has, no optional word, a kept flag of 0 or 1) and the mesh at its CMSH.
    The last mesh ends the stream; a chain is at most 16 meshes. `first_id` is the first mesh's runtime id (its reference is the archive's), 0 when there is none."""
    b = bytes(stream)
    n = len(b)
    if n > MESH_MAX_BYTES:
        return "an inline mesh over 16 MiB"
    c = _Cursor(b, 0, n)
    totals = [0, 0, 0, 0]
    ids = [first_id]
    while True:
        bad = _check_mesh(c, totals)
        if bad:
            return bad
        if not totals[3]:
            return None if c.done() else "an inline mesh with bytes after its last chunk"
        if len(ids) == MESH_MAX_CHAIN:
            return "an inline mesh with a chain of more than 16 meshes"
        rest = n - c.at
        if rest < 16 + 309 + 8:
            return "an inline mesh whose chain word is set and no chained mesh follows"
        h = c.at
        if b[h:h + 4] != b"PMSH" or _le32(b, h + 4) != rest - 8 or b[h + 8:h + 12] != b"PMS2" or _le32(b, h + 12) != rest - 16:
            return "an inline mesh whose chained mesh is not framed by PMSH and PMS2 headers that fill the rest of the stream"
        reference = h + 16
        if any(b[reference:reference + 300]):
            return "an inline mesh whose chained mesh has a reference name that is not all zero"
        runtime_id = _le32(b, reference + 300)
        if not 20000 <= runtime_id <= 29999 or runtime_id in ids:
            return "an inline mesh whose chained mesh has a runtime id outside 20000 to 29999 or one that another mesh of the chain has"
        if _le32(b, reference + 304) or b[reference + 308] > 1:
            return "an inline mesh whose chained mesh has an optional word set or a kept flag that is not 0 or 1"
        ids.append(runtime_id)
        c.at += 16 + 309
