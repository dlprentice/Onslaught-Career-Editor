#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Tests of inline_mesh_walk.py on authored streams (no game bytes): the cases of the CE mod loader's own tests (onslaught-ce port/tools/mods_tests.py:
test_one_inline_mesh_of_the_profile_is_admitted and test_an_inline_mesh_the_loaders_readers_would_misread_is_refused) run through the Python restatement, so that the
stager refuses what the loader refuses, and says why in the loader's words. The cases that concern the chunk around the stream (the reference name, the runtime id, the optional word,
the kept flag, a second inline mesh) are in world_mod_stage_tests.py's structure table, which runs the whole archive walk.

The builders are shared: world_mod_stage_tests.py and level888_build_tests.py make inline meshes with them."""
from __future__ import annotations

import ast
import struct
import unittest
from pathlib import Path

import inline_mesh_walk as walk

STALE = 0x41414141   # a pointer value for a field the reader must not leave to the file
NAME_AT = 325        # the stream of an unnamed MESH chunk starts after the 16 bytes of its PMSH and PMS2 headers and the 309-byte reference


def chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload


def inline_part(index=0, parts=1, textures=1, words=None, children=(), parent=None, vframes=1, hframes=1, orientations=True, positions=True,
                grid=None, reference=None, pieces=None, cmvb=None, vbuf_extra=0, box=True, after=b"", cmsp_delta=0, cmvb_delta=0, tail=b"", cached=None, no_pmvb=False):
    """The MESP chunk of a part of an inline mesh (cmsh-fields.md): CMSP, then each chunk the part record says is there, then PMVB. `words` patches the CMSP record
    ({offset: u32}); `pieces` is a list of dicts for the vertex buffer's pieces (vertices, indices, texr, ...)."""
    cmsp = bytearray(316)
    struct.pack_into("<IIIII", cmsp, 0x88, index, 1, len(children), 0, 0)
    struct.pack_into("<I", cmsp, 0x98, 0 if parent is None else 0xDEAD)
    struct.pack_into("<I", cmsp, 0xB8, vframes)
    struct.pack_into("<I", cmsp, 0xBC, hframes)
    struct.pack_into("<I", cmsp, 0xC8, 1 if positions else 0)
    struct.pack_into("<I", cmsp, 0x100, 1 if grid is not None else 0)
    struct.pack_into("<I", cmsp, 0x10C, 1 if orientations else 0)
    struct.pack_into("<I", cmsp, 0x124, 0 if reference is None else 1)
    if cached is not None:
        struct.pack_into("<II", cmsp, 0x104, 1, 1)
        struct.pack_into("<I", cmsp, 0x118, cached[0])
    for offset, value in (words or {}).items():
        struct.pack_into("<I", cmsp, offset, value)
    out = chunk(b"CMSP", (bytes(cmsp) + bytes(max(cmsp_delta, 0)))[:316 + cmsp_delta])
    if children:
        out += chunk(b"CHLD", b"".join(struct.pack("<I", c) for c in children))
    if parent is not None:
        out += chunk(b"PRNT", struct.pack("<I", parent))
    if box:
        out += chunk(b"BBOX", chunk(b"BBOX", bytes(40)))
    if vframes:
        out += chunk(b"VHFM", bytes(vframes))
    if hframes and orientations:
        out += chunk(b"HORI", bytes(48 * hframes))
    if hframes and positions:
        out += chunk(b"HPOS", bytes(16 * hframes))
    if grid is not None:
        out += chunk(b"PBKT", grid)
    if cached is not None:
        out += chunk(b"CPOS", bytes(cached[1])) + chunk(b"CORI", bytes(cached[2]))
    if reference is not None:
        out += chunk(b"REFR", struct.pack("<I", reference))
    if no_pmvb:
        return chunk(b"MESP", out + tail)
    pieces = [dict()] if pieces is None else pieces
    head = bytearray(296)
    struct.pack_into("<i", head, 0x108, len(pieces))
    if pieces:
        struct.pack_into("<III", head, 0x114, 36, 0x152, 4)
    for offset, value in (cmvb or {}).items():
        struct.pack_into("<I", head, offset, value)
    vb = chunk(b"CMVB", (bytes(head) + bytes(max(cmvb_delta, 0)))[:296 + cmvb_delta])
    first = pieces[0] if pieces else {}
    vcount = first.get("vertices", 4)
    for n, piece in enumerate(pieces):
        indices = piece.get("indices", [0, 1, 2, 3])
        vc = piece.get("vertex_count", vcount)
        texr = piece.get("texr", [0, -1, -1, -1, -1, -1])
        mmpt = struct.pack("<6I", piece.get("vbytes", 36 * vc), piece.get("ibytes", 2 * len(indices)), len(indices) if "icount" not in piece else piece["icount"],
                           vc, piece.get("prims", len(indices) - 2), piece.get("built", 1))
        vb += chunk(b"MMPT", mmpt[:len(mmpt) - piece.get("mmpt_cut", 0)] + bytes(piece.get("mmpt_extra", 0)))
        vb += chunk(b"IBUF", struct.pack(f"<{len(indices)}H", *indices) + bytes(piece.get("ibuf_extra", 0)))
        vb += chunk(b"VBUF", bytes(36 * vc + vbuf_extra) if n == 0 else bytes(piece.get("vbuf2", 0)))
        vb += chunk(b"TEXR", struct.pack("<6i", *texr) + bytes(piece.get("texr_extra", 0)))
    out += chunk(b"PMVB", vb + after)
    return chunk(b"MESP", out + tail)


def inline_stream(textures=1, frames=None, tex_name=b"tex.tga", tex_names=None, parts=1, cmsh=None, cmst=None, texb_delta=0, part=None, anim=0, emitters=0, cemt=None,
                  tail=b"", name=b"inline.msh", part_list=None, second_texb=False):
    """The mesh stream (cmsh-fields.md) of an inline mesh of the profile the walk admits: one texture, one part with one four-vertex piece, unless the arguments say otherwise.
    `cmsh` patches the 372-byte record ({offset: u32}); `tex_names` gives each texture its own name."""
    frames = frames or [1] * textures
    head = bytearray(372)
    struct.pack_into("<i", head, 4, textures)
    struct.pack_into("<i", head, 0x14, anim)
    struct.pack_into("<i", head, 0x1C, emitters)
    head[0x24:0x24 + len(name) + 1] = name + b"\0"
    struct.pack_into("<i", head, 0x15C, parts)
    for offset, value in (cmsh or {}).items():
        struct.pack_into("<I", head, offset, value)
    out = chunk(b"CMSH", bytes(head))
    table = bytearray(36 * textures)
    for i, f in enumerate(frames):
        struct.pack_into("<i", table, 36 * i + 8, f)
    out += chunk(b"CMST", bytes(table) if cmst is None else cmst)
    for i in range(textures):
        texb = bytes(20 * frames[i]) + (tex_names[i] if tex_names else tex_name).ljust(128, b"\0")
        texb = texb[:len(texb) + texb_delta] if texb_delta <= 0 else texb + bytes(texb_delta)
        out += chunk(b"MSHT", chunk(b"TEXB", texb) + (chunk(b"TEXB", texb) if second_texb else b""))
    for i in range(parts):
        out += part_list[i] if part_list else inline_part(i, parts, textures, **(part or {}))
    if anim:
        out += chunk(b"CAMD", bytes(36 * anim))
    out += chunk(b"BBOX", chunk(b"BBOX", bytes(40)))
    if emitters:
        out += cemt if cemt is not None else chunk(b"CEMT", struct.pack("<i", 336) + bytes(336) * emitters)
    return out + tail


def inline_mesh(stream=None, runtime_id=20000, name=b"", optional=0, kept=0, **kw):
    """A MESH payload whose mesh is unnamed: PMSH around a PMS2 that holds the 309-byte reference and then the mesh's stream."""
    stream = inline_stream(**kw) if stream is None else stream
    reference = bytearray(309)
    reference[:len(name)] = name
    struct.pack_into("<ii", reference, 300, runtime_id, optional)
    reference[308] = kept
    body = bytes(reference) + stream
    return b"PMSH" + struct.pack("<I", len(body) + 8) + b"PMS2" + struct.pack("<I", len(body)) + body


def chain_link(stream, runtime_id=20001, name=b"", optional=0, kept=1, pmsh_delta=0, pms2_delta=0, pmsh_tag=b"PMSH", pms2_tag=b"PMS2"):
    """The framing of a chained inline mesh (all 12 shipped chains): a PMSH header and a PMS2 header, each around the rest of the stream, the 309-byte reference, then the mesh's stream."""
    reference = bytearray(309)
    reference[:len(name)] = name
    struct.pack_into("<ii", reference, 300, runtime_id, optional)
    reference[308] = kept
    body = bytes(reference) + stream
    return pmsh_tag + struct.pack("<I", len(body) + 8 + pmsh_delta) + pms2_tag + struct.pack("<I", len(body) + pms2_delta) + body


def inline_chain(count=2, ids=None, links=None, last=None, **kw):
    """The stream of a chain of `count` meshes, each built by inline_stream(**kw): every mesh but the last has its chain word set and is followed by chain_link of the rest; `ids` are the runtime ids
    of the second, third ... mesh (20001, 20002, ...), `links` maps the number of a link (1 is the one before the second mesh) to chain_link's own arguments, `last` is the last mesh's stream."""
    ids = ids or [20001 + i for i in range(count - 1)]
    rest = inline_stream(**kw) if last is None else last
    for i in range(count - 2, -1, -1):
        rest = inline_stream(cmsh={8: 1}, **kw) + chain_link(rest, ids[i], **(links or {}).get(i + 1, {}))
    return rest


def grid_cells(width, height, lists):
    """The PBCS chunks of a collision grid: `lists` maps a cell number to its list of triangle indices."""
    out = b""
    for cell in range(width * height):
        if cell in lists:
            idx = lists[cell]
            out += chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"PBSQ", struct.pack("<i", len(idx)) + struct.pack(f"<{len(idx)}h", *idx))))
        else:
            out += chunk(b"PBCS", struct.pack("<i", 0))
    return out


def inline_grid(width=2, height=1, lists=None, triangles=2, vertices=4, tri_vertices=None, sizs=None, plqt=None, cpbt=None, cells=None, pbke_size=12,
                cpbt_raw=None, sizs_raw=None, plqt_raw=None, no_pbfk=False, pbpn_raw=None, pbpp_size=6, pbpp_count=None, tail=b"", spare=0):
    """The payload of a PBKT: CPBT, SIZS, the cells, PLQT, PBFK around the PBKEs, PBPN and the PBPPs. The `*_raw` arguments replace a fixed-size record's payload, `spare` is the half-word after a
    triangle's three vertices and `tail` follows the last vertex (this copy of the loader's builder adds them, for the rules the loader's own cases do not reach)."""
    lists = {0: [0, 1]} if lists is None else lists
    record = bytearray(184)
    struct.pack_into("<ii", record, 0x68, width, height)
    for offset, value in (cpbt or {}).items():
        struct.pack_into("<I", record, offset, value)
    n_lists, n_indices = len(lists), sum(len(v) for v in lists.values())
    out = chunk(b"CPBT", bytes(record) if cpbt_raw is None else cpbt_raw)
    out += chunk(b"SIZS", (struct.pack("<ii", n_lists, n_indices) if sizs is None else struct.pack("<ii", *sizs)) if sizs_raw is None else sizs_raw)
    out += grid_cells(width, height, lists) if cells is None else cells
    out += chunk(b"PLQT", struct.pack("<i", triangles if plqt is None else plqt) if plqt_raw is None else plqt_raw)
    tri_vertices = tri_vertices or [(i % vertices, (i + 1) % vertices, (i + 2) % vertices) for i in range(triangles)]
    if not no_pbfk:
        out += chunk(b"PBFK", b"".join(chunk(b"PBKE", (struct.pack("<IHHHH", 0x1FFFE000, *v, spare) + bytes(max(pbke_size - 12, 0)))[:pbke_size]) for v in tri_vertices))
    out += chunk(b"PBPN", struct.pack("<i", vertices) if pbpn_raw is None else pbpn_raw)
    out += b"".join(chunk(b"PBPP", bytes(pbpp_size)) for _ in range(vertices if pbpp_count is None else pbpp_count))
    return out + tail


def stream_of(mesh_payload: bytes) -> bytes:
    """The stream of an inline MESH payload (what check_inline_mesh takes)."""
    return mesh_payload[NAME_AT:]


def first_id_of(mesh_payload: bytes) -> int:
    """The first mesh's runtime id, which the chunk's reference holds (the archive hands it to the walk)."""
    return struct.unpack_from("<I", mesh_payload, 316)[0]


def check(mesh_payload: bytes):
    """The walk's answer for an inline MESH payload."""
    return walk.check_inline_mesh(stream_of(mesh_payload), first_id_of(mesh_payload))


def at_the_limits() -> dict:
    """Meshes exactly at each limit of the walk, and shapes the loader's own cases do not reach (this module's cases; the loader's walk admits them all, as stager_diff against it showed). A refusal one past
    each limit is in past_the_limits(). The words that a mutant of the walk would misread by a byte are set to 1 and to 1 << 24, so a read one byte early or late sees one of them as zero."""
    emitter = bytearray(336)
    struct.pack_into("<I", emitter, 0x40, 1)
    cases = {
        "8 animation modes": inline_mesh(anim=8),
        "512 emitters": inline_mesh(emitters=512),
        "an emitter whose part index is the last four bytes of the CEMT": inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(emitter) + struct.pack("<I", 0))),
        "a mesh name of 299 characters": inline_mesh(name=b"", stream=inline_stream(name=b"x" * 299)),
        "a texture name of 127 characters": inline_mesh(tex_name=b"a" * 127),
        "a texture name of every printable character": inline_mesh(tex_name=bytes(range(0x20, 0x7F))),
        "65535 virtual frames": inline_mesh(part=dict(vframes=65535)),
        "65535 hand frames": inline_mesh(part=dict(hframes=65535)),
        "65535 cached frames": inline_mesh(part=dict(cached=(65535, 16 * 65535, 48 * 65535))),
        "no cached frames but their chunks": inline_mesh(part=dict(cached=(0, 0, 0))),
        "hand frames and neither HORI nor HPOS": inline_mesh(part=dict(orientations=False, positions=False)),
        "a part that is its own child and its sibling's": inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, children=[0, 1]), inline_part(1, 2, 1)]),
        "a piece of 3 indices": inline_mesh(part=dict(pieces=[dict(indices=[0, 1, 2])])),
        "a piece of 65535 vertices and 65535 indices": inline_mesh(part=dict(pieces=[dict(vertex_count=65535, indices=[j % 65535 for j in range(65535)])])),
        "a collision grid of 16384 cells": inline_mesh(part=dict(grid=inline_grid(width=128, height=128))),
        "a collision grid of 32767 triangles": inline_mesh(part=dict(grid=inline_grid(lists={0: [0, 32766]}, triangles=32767))),
        "a collision grid list of 1048576 indices": inline_mesh(part=dict(grid=inline_grid(lists={0: [0] * (1 << 20)}, triangles=1, vertices=3))),
        "a collision grid of 32767 vertices": inline_mesh(part=dict(grid=inline_grid(vertices=32767))),
    }
    flag_high = bytearray(336)
    struct.pack_into("<I", flag_high, 0x40, 1 << 24)
    unnamed = bytearray(inline_stream())
    unnamed[8 + 0x24:8 + 0x24 + 300] = b"\0" + b"x" * 299   # an empty name, then 299 characters that are not zero: the name is terminated at its first byte
    cases.update({
        "a collision grid 16384 cells wide": inline_mesh(part=dict(grid=inline_grid(width=16384, height=1))),
        "a collision grid 16384 cells high": inline_mesh(part=dict(grid=inline_grid(width=1, height=16384))),
        "a list in every cell of a grid": inline_mesh(part=dict(grid=inline_grid(lists={0: [0, 1], 1: [0]}))),
        "a list of no indices": inline_mesh(part=dict(grid=inline_grid(lists={0: []}, triangles=0))),
        "a grid of no triangles and no vertices": inline_mesh(part=dict(grid=inline_grid(lists={}, triangles=0, vertices=0))),
        "a listed triangle whose spare half-word is large": inline_mesh(part=dict(grid=inline_grid(spare=60000))),
        "a vertex 256 of 300": inline_mesh(part=dict(grid=inline_grid(vertices=300, tri_vertices=[(0, 256, 2), (1, 2, 3)]))),
        "an empty mesh name followed by characters that are not zero": inline_mesh(stream=bytes(unnamed)),
        "an emitter flag of 1 << 24 and its part index": inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(flag_high) + struct.pack("<I", 0))),
    })
    for kind in (2, 5, 6):
        cases[f"part type {kind}"] = inline_mesh(part=dict(words={0x8C: kind}))
    # a flag word the walk reads, set as 1 << 24: the chunk it announces must still be there
    for name, off, part in (("a parent", 0x98, dict(parent=0)), ("a collision grid", 0x100, dict(grid=inline_grid())), ("hand positions", 0xC8, dict()), ("cached positions", 0x104, dict(cached=(2, 32, 96))),
                            ("cached orientations", 0x108, dict(cached=(2, 32, 96))), ("hand orientations", 0x10C, dict()), ("a reference", 0x124, dict(reference=0))):
        cases[f"{name} announced by a flag of 1 << 24"] = inline_mesh(part=dict(part, words={off: 1 << 24}))
    return cases


def admitted_cases() -> dict:
    """The meshes the loader admits: the shapes a converted PS2 mesh has (children, parents, references, shared pieces, a collision grid whose unlisted tail is as the PS2
    exporter left it, emitters with part indices, animation modes), at the limits."""
    two = inline_stream(textures=2, tex_name=b"two.tga", parts=3, part_list=[
        inline_part(0, 3, 2, children=[1, 2]), inline_part(1, 3, 2, parent=0, reference=2), inline_part(2, 3, 2, parent=0, pieces=[])])
    emitter = bytearray(336)
    struct.pack_into("<I", emitter, 0x40, 1)
    cemt = chunk(b"CEMT", struct.pack("<i", 336) + bytes(emitter) + struct.pack("<I", 0) + bytes(336))
    return {
        "the smallest": inline_mesh(),
        "kept flag 1, last id": inline_mesh(runtime_id=29999, kept=1),
        "three parts with children, parents and a reference, two textures": inline_mesh(two),
        "a part without vertices (its CMVB holds no piece)": inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, pieces=[]), inline_part(1, 2, 1)]),
        "two pieces sharing the first's vertices, the second with a slot of its own": inline_mesh(part=dict(pieces=[dict(), dict(texr=[-1, 0, -1, -1, -1, -1])])),
        "12 pieces": inline_mesh(part=dict(pieces=[dict() for _ in range(12)])),
        "an animation mode": inline_mesh(anim=2),
        "two emitters, one with a part index": inline_mesh(emitters=2, cemt=cemt),
        "16 textures of 16 frames": inline_mesh(textures=16, frames=[16] * 16),
        "cached positions and orientations for 2 frames": inline_mesh(part=dict(cached=(2, 32, 96))),
        "a collision grid": inline_mesh(part=dict(grid=inline_grid())),
        "a collision grid with garbage in the triangles no list names": inline_mesh(part=dict(grid=inline_grid(
            triangles=3, lists={0: [0, 1]}, tri_vertices=[(0, 1, 2), (1, 2, 3), (60000, 61000, 62000)]))),
        "a collision grid whose CPBT carries another triangle count (the PS2 exporter's)": inline_mesh(part=dict(grid=inline_grid(cpbt={0x78: 24892}))),
        "a collision grid of absent cells": inline_mesh(part=dict(grid=inline_grid(lists={}, triangles=0))),
        "512 parts": inline_mesh(parts=512, part_list=[inline_part(i, 512, 1, pieces=[]) for i in range(512)]),
        "100000 vertices in all": inline_mesh(parts=2, part_list=[inline_part(i, 2, 1, pieces=[dict(vertex_count=50000)]) for i in range(2)]),
        "600000 indices in all": inline_mesh(parts=10, part_list=[inline_part(i, 10, 1, pieces=[dict(indices=[j % 4 for j in range(60000)])]) for i in range(10)]),
        "1024 pieces in all": inline_mesh(parts=86, part_list=[inline_part(i, 86, 1, pieces=[dict() for _ in range(12 if i < 85 else 4)]) for i in range(86)]),
        # the exporter dumped live objects, so the shipped parts carry stale pointers in every slot the reader replaces
        "stale pointers in the slots the reader replaces": inline_mesh(part=dict(
            words={0x80: STALE, 0x84: STALE, 0x94: STALE, 0xC4: STALE, 0xFC: STALE, 0x128: STALE, 0x134: STALE, 0x138: STALE},
            cmvb={0x08: STALE, 0x10C: STALE, 0x124: STALE})),
        "no position sets": inline_mesh(part=dict(words={0xB4: 0})),
        "two position sets (the most a shipped part has)": inline_mesh(part=dict(words={0xB4: 2})),
        # meshes chained to the first, framed as the shipped chains are (5 meshes each)
        "a chain of 2 meshes": inline_mesh(inline_chain(2)),
        "a chain of 5 meshes, as the shipped chains are": inline_mesh(inline_chain(5)),
        "a chain of 16 meshes, the most": inline_mesh(inline_chain(16)),
        "a chain whose meshes have two textures and two parts each": inline_mesh(inline_chain(3, textures=2, tex_name=b"two.tga", parts=2)),
        "a chain that fills the vertex total (two meshes of 50000 vertices)": inline_mesh(inline_chain(2, part=dict(pieces=[dict(vertex_count=50000)]))),
        "a chain with the last runtime id": inline_mesh(inline_chain(2, ids=[29999]), runtime_id=20000),
        "a chain whose chained meshes have a kept flag of 0": inline_mesh(inline_chain(3, links={1: dict(kept=0), 2: dict(kept=0)})),
        "a chained mesh with the lowest runtime id": inline_mesh(inline_chain(2, ids=[20000]), runtime_id=20005),
        **at_the_limits(),
    }


def past_the_limits() -> dict:
    """{label: (mesh payload, words)}: a step past each limit that at_the_limits() sits on, an index equal to its count, and the words a one-byte misread would miss."""
    emitter = bytearray(336)
    struct.pack_into("<I", emitter, 0x40, 1)
    flagged = struct.pack("<i", 336) + bytes(emitter)
    grid = lambda **kw: dict(grid=inline_grid(**kw))
    same_words = "a chain, older-format vertices or triangles, bones or a field of view"
    cases = {
        "a CEMT of 3 bytes": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", bytes(3))), "336-byte emitter record size"),
        "a CEMT of the record size alone": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336))), "holds fewer emitters than its count"),
        "an emitter one byte short": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(335))), "holds fewer emitters than its count"),
        "an emitter whose part index is the part count": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", flagged + struct.pack("<I", 1))), "part index is missing or not a part of the mesh"),
        "a child equal to the part count": (inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, children=[2]), inline_part(1, 2, 1)]), "a child that is not a part of the mesh"),
        "a second child that is not a part": (inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, children=[0, 5]), inline_part(1, 2, 1)]), "a child that is not a part of the mesh"),
        "a parent equal to the part count": (inline_mesh(part=dict(parent=1)), "whose PRNT is not one part of the mesh"),
        "a reference equal to the part count": (inline_mesh(part=dict(reference=1)), "whose REFR is not one part of the mesh"),
        "a piece of 65536 vertices": (inline_mesh(part=dict(pieces=[dict(vertex_count=65536)])), "vertex count is zero, over 65535, or not its vertex bytes"),
        "a piece of 65536 indices": (inline_mesh(part=dict(pieces=[dict(indices=[0] * 65536)])), "whose MMPT counts disagree"),
        "a texture slot of the last position past the textures": (inline_mesh(part=dict(pieces=[dict(texr=[-1, -1, -1, -1, -1, 7])])), "a texture slot that is not -1 or one of the mesh's textures"),
        "a second piece with other vertex bytes": (inline_mesh(part=dict(pieces=[dict(), dict(vbytes=145)])), "does not share the first piece's vertices"),
        "a second piece with another vertex count and the same bytes": (inline_mesh(part=dict(pieces=[dict(), dict(vertex_count=5, vbytes=144)])), "does not share the first piece's vertices"),
        "a texture name with the character below the first printable": (inline_mesh(tex_name=b"a\x1fb"), "name is not printable ASCII"),
        "a texture name with the first character past the printable": (inline_mesh(tex_name=b"a\x7fb"), "name is not printable ASCII"),
        "empty cached chunks and no PMVB": (inline_mesh(part=dict(cached=(0, 0, 0), no_pmvb=True)), "without its PMVB"),
        "a grid of SIZS indices over the cap": (inline_mesh(part=grid(sizs=(1, (1 << 20) + 1))), "declares more lists or indices than it can hold"),
        "a grid list over the cap": (inline_mesh(part=grid(sizs=(1, 1 << 20), lists={0: [0] * ((1 << 20) + 1)}, triangles=1, vertices=3)), "a list whose size is not its count"),
        "a grid of 32768 triangles and a list below": (inline_mesh(part=grid(triangles=32768)), "lists a triangle it does not have, or has more than 32767"),
        "a part type of 1 << 24": (inline_mesh(part=dict(words={0x8C: 1 << 24})), "skeletal or a camera"),
        "a CEMT that declares a byte more than the stream holds": (inline_mesh(emitters=1, cemt=b"CEMT" + struct.pack("<I", 341) + struct.pack("<i", 336) + bytes(336)),
                                                                   "336-byte emitter record size"),
        "an emitter whose part index is three bytes": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", flagged + bytes(3))), "part index is missing or not a part of the mesh"),
        "a PBCS of 3 bytes": (inline_mesh(part=grid(cells=chunk(b"PBCS", bytes(3)) + chunk(b"PBCS", struct.pack("<i", 0)))), "fewer PBCS cells than its width and height"),
        "a PBSQ of 3 bytes": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"PBSQ", bytes(3)))) + chunk(b"PBCS", struct.pack("<i", 0)))),
                              "has a PBET that is not one PBSQ"),
        "a PBET that holds a PBSQ and another chunk": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"PBSQ", struct.pack("<i", 0)) + chunk(b"JUNK", b"")))
                                                                             + chunk(b"PBCS", struct.pack("<i", 0)))), "has a PBET that is not one PBSQ"),
        "a list naming the triangle that equals the count": (inline_mesh(part=grid(lists={0: [0, 2]})), "lists a triangle it does not have"),
        "a listed triangle naming the vertex that equals the count": (inline_mesh(part=grid(tri_vertices=[(0, 1, 4), (1, 2, 3)])), "names a vertex it does not have"),
        "a vertex 256 of 200": (inline_mesh(part=grid(vertices=200, tri_vertices=[(0, 256, 2), (1, 2, 3)])), "names a vertex it does not have"),
    }
    for off in (0x9C, 0xA0, 0xA4, 0xA8, 0xAC, 0xB0, 0xC0, 0xCC, 0xD0, 0xD4, 0xD8):
        for value in (1, 1 << 24):
            cases[f"the word at {off:#x} set to {value:#x}"] = (inline_mesh(part=dict(words={off: value})), same_words)
    for off, label, words in ((8, "a chain word", "whose chain word is set and no chained mesh follows"), (0xC, "cutscene sequences", "with cutscene sequences (not admitted)")):
        for value in (1, 1 << 24):
            cases[f"{label} as {value:#x}"] = (inline_mesh(cmsh={off: value}), words)
    for off, label in ((0x14, "animation modes"), (0x1C, "emitters"), (0x15C, "parts")):
        cases[f"{label} as 1 << 24"] = (inline_mesh(cmsh={off: 1 << 24}), "count out of bounds")
    return cases


def refused_cases() -> dict:
    """{label: (mesh payload, words the refusal contains)}: streams the loader's readers would misread, one rule at a time."""
    grid = lambda **kw: dict(grid=inline_grid(**kw))
    return {
        "no stream at all (325 bytes)": (inline_mesh(stream=b""), "does not start with a 372-byte CMSH record"),
        "a stream of zeros": (inline_mesh(stream=bytes(500)), "does not start with a 372-byte CMSH record"),
        "a CMST first": (inline_mesh(stream=chunk(b"CMST", b"") + inline_stream()), "does not start with a 372-byte CMSH record"),
        "a CMSH of 371 bytes": (inline_mesh(stream=chunk(b"CMSH", bytes(371)) + inline_stream()[380:]), "does not start with a 372-byte CMSH record"),
        # the mesh record
        "an unterminated name": (inline_mesh(name=b"", stream=inline_stream(name=b"x" * 300)), "whose name is not terminated"),
        "a chain word and nothing after the mesh": (inline_mesh(cmsh={8: 1}), "whose chain word is set and no chained mesh follows"),
        "a cutscene sequence": (inline_mesh(cmsh={0xC: 1}), "with cutscene sequences (not admitted)"),
        "17 textures": (inline_mesh(textures=17), "count out of bounds"),
        "9 animation modes": (inline_mesh(anim=9), "count out of bounds"),
        "513 emitters": (inline_mesh(emitters=513), "count out of bounds"),
        "no parts": (inline_mesh(parts=0), "count out of bounds"),
        "513 parts": (inline_mesh(parts=513, part_list=[inline_part(i, 513, 1, pieces=[]) for i in range(513)]), "count out of bounds"),
        "fewer parts than the record says": (inline_mesh(cmsh={0x15C: 2}), "fewer MESP parts than its part count"),
        # textures
        "a CMST of 35 bytes": (inline_mesh(cmst=bytes(35)), "whose CMST is not its texture count of 36-byte records"),
        "a texture of no frames": (inline_mesh(frames=[0]), "no frames or more than 16"),
        "a texture of 17 frames": (inline_mesh(frames=[17]), "no frames or more than 16"),
        "fewer texture lists than the record says": (inline_mesh(cmsh={4: 2}, cmst=(bytes(8) + struct.pack("<i", 1) + bytes(24)) * 2), "fewer MSHT texture lists"),
        "a TEXB one byte short": (inline_mesh(texb_delta=-1), "whose MSHT is not one TEXB"),
        "a TEXB one byte long": (inline_mesh(texb_delta=1), "whose MSHT is not one TEXB"),
        "two TEXBs in an MSHT": (inline_mesh(second_texb=True), "whose MSHT is not one TEXB"),
        "an empty texture name": (inline_mesh(tex_name=b""), "name is empty or not terminated"),
        "a texture name without its NUL": (inline_mesh(tex_name=b"x" * 128), "name is empty or not terminated"),
        "a texture name with a control character": (inline_mesh(tex_name=b"a\x01b"), "name is not printable ASCII"),
        "a texture name with a byte over 0x7E": (inline_mesh(tex_name=b"a\xe9b"), "name is not printable ASCII"),
        # the parts
        "a CMSP of 315 bytes": (inline_mesh(part=dict(cmsp_delta=-1)), "does not start with a 316-byte CMSP record"),
        "a CMSP of 317 bytes": (inline_mesh(part=dict(cmsp_delta=1)), "does not start with a 316-byte CMSP record"),
        "a skeletal part": (inline_mesh(part=dict(words={0x8C: 3})), "skeletal or a camera"),
        "a camera part": (inline_mesh(part=dict(words={0x8C: 4})), "skeletal or a camera"),
        "part type 0": (inline_mesh(part=dict(words={0x8C: 0})), "skeletal or a camera"),
        "part type 7": (inline_mesh(part=dict(words={0x8C: 7})), "skeletal or a camera"),
        "a chained part": (inline_mesh(part=dict(words={0x9C: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "older-format vertices": (inline_mesh(part=dict(words={0xA8: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "older-format pvertices": (inline_mesh(part=dict(words={0xAC: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "older-format triangles": (inline_mesh(part=dict(words={0xB0: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "bones": (inline_mesh(part=dict(words={0xC0: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "a field of view": (inline_mesh(part=dict(words={0xCC: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "bone weights": (inline_mesh(part=dict(words={0xD4: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "bone slots": (inline_mesh(part=dict(words={0xD8: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        # the fields the reader keeps from the file and the part's destructor or the draw then uses
        "a chain count": (inline_mesh(part=dict(words={0xA0: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "a chained flag": (inline_mesh(part=dict(words={0xA4: 1})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "a bones pointer and no bones": (inline_mesh(part=dict(words={0xD0: STALE})), "a chain, older-format vertices or triangles, bones or a field of view"),
        "3 position sets": (inline_mesh(part=dict(words={0xB4: 3})), "more position sets than the shipped parts have"),
        "2^24 position sets": (inline_mesh(part=dict(words={0xB4: 1 << 24})), "more position sets than the shipped parts have"),
        "2^31 - 1 position sets": (inline_mesh(part=dict(words={0xB4: 0x7FFFFFFF})), "more position sets than the shipped parts have"),
        "2^32 - 1 position sets": (inline_mesh(part=dict(words={0xB4: 0xFFFFFFFF})), "more position sets than the shipped parts have"),
        "no virtual frames": (inline_mesh(part=dict(vframes=0)), "no virtual frames"),
        "no virtual frames and a stale map pointer": (inline_mesh(part=dict(vframes=0, words={0xC4: STALE})), "no virtual frames"),
        "no hand frames": (inline_mesh(part=dict(hframes=0)), "no hand frames"),
        "no hand frames and stale table pointers": (inline_mesh(part=dict(hframes=0, words={0xC8: STALE, 0x10C: STALE})), "no hand frames"),
        "more children than parts": (inline_mesh(part=dict(words={0x90: 2})), "a child, frame or cache count out of bounds"),
        "65536 virtual frames": (inline_mesh(part=dict(words={0xB8: 65536})), "a child, frame or cache count out of bounds"),
        "65536 frames": (inline_mesh(part=dict(words={0xBC: 65536})), "a child, frame or cache count out of bounds"),
        "65536 cached frames": (inline_mesh(part=dict(words={0x118: 65536})), "a child, frame or cache count out of bounds"),
        "a child that is not a part": (inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, children=[5]), inline_part(1, 2, 1)]), "a child that is not a part of the mesh"),
        "a CHLD that is not the child count": (inline_mesh(part=dict(words={0x90: 1})), "whose CHLD is not its child count"),
        "a parent that is not a part": (inline_mesh(part=dict(parent=7)), "whose PRNT is not one part of the mesh"),
        "a parent pointer and no PRNT": (inline_mesh(part=dict(words={0x98: 1}, box=True)), "whose PRNT is not one part of the mesh"),
        "no bounding box": (inline_mesh(part=dict(box=False)), "without its bounding box"),
        "a VHFM that is not the virtual-frame count": (inline_mesh(part=dict(words={0xB8: 3})), "whose VHFM is not its virtual-frame count"),
        "an HORI that is not the frame count": (inline_mesh(part=dict(words={0xBC: 2})), "whose HORI is not its frame count of matrices"),
        "an HPOS that is not the frame count": (inline_mesh(part=dict(orientations=False, words={0xBC: 2})), "whose HPOS is not its frame count of vectors"),
        "a reference that is not a part": (inline_mesh(part=dict(reference=9)), "whose REFR is not one part of the mesh"),
        "a reference pointer and no REFR": (inline_mesh(part=dict(words={0x124: 1})), "whose REFR is not one part of the mesh"),
        "a collision grid pointer and no PBKT": (inline_mesh(part=dict(words={0x100: 1})), "has a collision grid but no PBKT"),
        "a CPOS that is not the cached frame count of vectors": (inline_mesh(part=dict(cached=(2, 31, 96))), "whose CPOS is not its cached frame count of vectors"),
        "a CORI that is not the cached frame count of matrices": (inline_mesh(part=dict(cached=(2, 32, 97))), "whose CORI is not its cached frame count of matrices"),
        "a cache pointer and no CPOS": (inline_mesh(part=dict(words={0x104: 1})), "whose CPOS is not its cached frame count of vectors"),
        "a cache pointer and no CORI": (inline_mesh(part=dict(words={0x108: 1})), "whose CORI is not its cached frame count of matrices"),
        "a CMVB of 295 bytes": (inline_mesh(part=dict(cmvb_delta=-1)), "does not start with a 296-byte CMVB"),
        "13 pieces": (inline_mesh(part=dict(pieces=[dict() for _ in range(13)])), "more than 12 vertex-buffer pieces"),
        "48-byte vertices": (inline_mesh(part=dict(cmvb={0x114: 48})), "not the 36-byte format drawn as a strip"),
        "another vertex format": (inline_mesh(part=dict(cmvb={0x118: 0})), "not the 36-byte format drawn as a strip"),
        "a triangle list": (inline_mesh(part=dict(cmvb={0x11C: 3})), "not the 36-byte format drawn as a strip"),
        "a shader pointer": (inline_mesh(part=dict(cmvb={0x110: STALE})), "carries a shader pointer"),
        "a piece pointer in the first unused slot": (inline_mesh(part=dict(cmvb={0x0C: STALE})), "piece pointer beyond its pieces"),
        "a piece pointer in the last slot": (inline_mesh(part=dict(cmvb={0x104: STALE})), "piece pointer beyond its pieces"),
        "a piece pointer in slot 0 of a part without pieces": (inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, pieces=[], cmvb={0x08: STALE}), inline_part(1, 2, 1)]),
                                                               "piece pointer beyond its pieces"),
        "a piece pointer in the slot after twelve pieces": (inline_mesh(part=dict(pieces=[dict() for _ in range(12)], cmvb={0x08 + 4 * 12: STALE})), "piece pointer beyond its pieces"),
        "bytes after the last piece": (inline_mesh(part=dict(after=chunk(b"JUNK", b""))), "bytes in its PMVB after its last piece"),
        "bytes after the vertex buffer": (inline_mesh(part=dict(tail=chunk(b"JUNK", b""))), "bytes after its vertex buffer"),
        # the pieces
        "a piece not built": (inline_mesh(part=dict(pieces=[dict(built=0)])), "whose MMPT counts disagree"),
        "a piece of 2 indices": (inline_mesh(part=dict(pieces=[dict(indices=[0, 1])])), "whose MMPT counts disagree"),
        "index bytes that are not twice the count": (inline_mesh(part=dict(pieces=[dict(ibytes=7)])), "whose MMPT counts disagree"),
        "a primitive count that is not the index count less 2": (inline_mesh(part=dict(pieces=[dict(prims=3)])), "whose MMPT counts disagree"),
        "no vertices": (inline_mesh(part=dict(pieces=[dict(vertex_count=0, indices=[0, 0, 0, 0])])), "vertex count is zero, over 65535, or not its vertex bytes"),
        "vertex bytes that are not 36 for each": (inline_mesh(part=dict(pieces=[dict(vbytes=143)])), "vertex count is zero, over 65535, or not its vertex bytes"),
        "a second piece with other vertices": (inline_mesh(part=dict(pieces=[dict(), dict(vertex_count=5)])), "does not share the first piece's vertices"),
        "an index past the vertices": (inline_mesh(part=dict(pieces=[dict(indices=[0, 1, 2, 4])])), "an index past its vertices"),
        "an IBUF longer than its bytes": (inline_mesh(part=dict(pieces=[dict(ibuf_extra=2)])), "whose IBUF is not its index bytes"),
        "a first VBUF longer than its vertices": (inline_mesh(part=dict(vbuf_extra=4)), "whose VBUF is not its vertices"),
        "a second VBUF that is not empty": (inline_mesh(part=dict(pieces=[dict(), dict(vbuf2=36)])), "whose VBUF is not its vertices"),
        "a TEXR of 28 bytes": (inline_mesh(part=dict(pieces=[dict(texr_extra=4)])), "without a 24-byte TEXR"),
        "an MMPT of 28 bytes": (inline_mesh(part=dict(pieces=[dict(mmpt_extra=4)])), "without a 24-byte MMPT"),
        "an MMPT of 20 bytes": (inline_mesh(part=dict(pieces=[dict(mmpt_cut=4)])), "without a 24-byte MMPT"),
        "100001 vertices in all": (inline_mesh(parts=2, part_list=[inline_part(0, 2, 1, pieces=[dict(vertex_count=50001)]), inline_part(1, 2, 1, pieces=[dict(vertex_count=50000)])]),
                                   "more than 100000 vertices, 600000 indices or 1024 pieces"),
        "two parts of 65535 vertices": (inline_mesh(parts=2, part_list=[inline_part(i, 2, 1, pieces=[dict(vertex_count=65535)]) for i in range(2)]),
                                        "more than 100000 vertices, 600000 indices or 1024 pieces"),
        "600001 indices in all": (inline_mesh(parts=10, part_list=[inline_part(i, 10, 1, pieces=[dict(indices=[j % 4 for j in range(60001 if i == 9 else 60000)])]) for i in range(10)]),
                                  "more than 100000 vertices, 600000 indices or 1024 pieces"),
        "1025 pieces in all": (inline_mesh(parts=86, part_list=[inline_part(i, 86, 1, pieces=[dict() for _ in range(12 if i < 85 else 5)]) for i in range(86)]),
                               "more than 100000 vertices, 600000 indices or 1024 pieces"),
        "a stream of 16 MiB and one byte": (inline_mesh(stream=bytes((16 << 20) + 1)), "an inline mesh over 16 MiB"),
        "a stream of exactly 16 MiB is not over the cap (it is no mesh either)": (inline_mesh(stream=bytes(16 << 20)), "does not start with a 372-byte CMSH record"),
        "a texture slot past the textures": (inline_mesh(part=dict(pieces=[dict(texr=[1, -1, -1, -1, -1, -1])])), "a texture slot that is not -1 or one of the mesh's textures"),
        "a texture slot of -2": (inline_mesh(part=dict(pieces=[dict(texr=[0, -2, -1, -1, -1, -1])])), "a texture slot that is not -1 or one of the mesh's textures"),
        # the collision grid
        "a grid with fewer cells than its size": (inline_mesh(part=grid(width=3, height=1, lists={0: [0, 1]}, cells=grid_cells(2, 1, {0: [0, 1]}))), "fewer PBCS cells than its width and height"),
        "a grid of no width": (inline_mesh(part=grid(width=0, height=1, lists={}, triangles=0)), "has a size out of bounds"),
        "a grid of 200 by 200 cells": (inline_mesh(part=grid(width=200, height=200, lists={}, triangles=0)), "has a size out of bounds"),
        "a grid of 16385 cells": (inline_mesh(part=grid(width=16385, height=1, lists={}, triangles=0)), "has a size out of bounds"),
        "a cell that is neither present nor absent": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 2)) + chunk(b"PBCS", struct.pack("<i", 0)))),
                                                     "neither present nor absent"),
        "an absent cell with data": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<ii", 0, 0)) + chunk(b"PBCS", struct.pack("<i", 0)), lists={})),
                                     "an absent cell with data"),
        "a list longer than its size": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"PBSQ", struct.pack("<i", 5) + bytes(4))))
                                                         + chunk(b"PBCS", struct.pack("<i", 0)))), "a list whose size is not its count"),
        "a list with bytes after its indices": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"PBSQ", struct.pack("<i", 1) + bytes(4))))
                                                         + chunk(b"PBCS", struct.pack("<i", 0)), lists={0: [0]})), "a list whose size is not its count"),
        "a list naming a triangle past the count": (inline_mesh(part=grid(lists={0: [0, 5]})), "lists a triangle it does not have"),
        "a list naming triangle 32767": (inline_mesh(part=grid(lists={0: [0, 32767]}, triangles=32768)), "lists a triangle past 32767"),
        "more lists than SIZS declares": (inline_mesh(part=grid(sizs=(0, 2))), "more lists or indices than its SIZS declares"),
        "more indices than SIZS declares": (inline_mesh(part=grid(sizs=(1, 1))), "more lists or indices than its SIZS declares"),
        "a SIZS with more lists than cells": (inline_mesh(part=grid(sizs=(3, 2))), "declares more lists or indices than it can hold"),
        "a PBKE of 14 bytes": (inline_mesh(part=grid(pbke_size=14)), "fewer 12-byte PBKE triangles than its count"),
        "a PBKE of 10 bytes": (inline_mesh(part=grid(pbke_size=10)), "fewer 12-byte PBKE triangles than its count"),
        "a PLQT of more triangles than PBFK holds": (inline_mesh(part=grid(plqt=3)), "fewer 12-byte PBKE triangles than its count"),
        "a PLQT of fewer triangles than PBFK holds": (inline_mesh(part=grid(plqt=1, lists={0: [0]})), "bytes in its PBFK after its triangles"),
        "a listed triangle naming a vertex it lacks": (inline_mesh(part=grid(tri_vertices=[(0, 1, 9), (1, 2, 3)])), "a listed triangle that names a vertex it does not have"),
        "more vertices than 32767": (inline_mesh(part=grid(vertices=32768)), "names a vertex it does not have"),
        # the rules of the grid and of the part that the loader's own cases do not reach (the stager's table names them, so that a change of any is seen)
        "a grid that does not start with a 184-byte CPBT": (inline_mesh(part=grid(cpbt_raw=bytes(183))), "does not start with a 184-byte CPBT"),
        "a SIZS of 7 bytes": (inline_mesh(part=grid(sizs_raw=bytes(7))), "has no 8-byte SIZS after its CPBT"),
        "a present cell that holds more than a PBET": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"PBSQ", struct.pack("<i", 0))) + b"x")
                                                                              + chunk(b"PBCS", struct.pack("<i", 0)))), "has a present cell that is not one PBET"),
        "a PBET that is not one PBSQ": (inline_mesh(part=grid(cells=chunk(b"PBCS", struct.pack("<i", 1) + chunk(b"PBET", chunk(b"JUNK", bytes(4)))) + chunk(b"PBCS", struct.pack("<i", 0)))),
                                        "has a PBET that is not one PBSQ"),
        "a PLQT of 5 bytes": (inline_mesh(part=grid(plqt_raw=bytes(5))), "has no 4-byte PLQT after its cells"),
        "no PBFK": (inline_mesh(part=grid(no_pbfk=True)), "has no PBFK"),
        "a PBPN of 5 bytes": (inline_mesh(part=grid(pbpn_raw=bytes(5))), "has no 4-byte PBPN"),
        "a PBPP of 7 bytes": (inline_mesh(part=grid(pbpp_size=7)), "fewer 6-byte PBPP vertices than its count"),
        "one PBPP fewer than the count": (inline_mesh(part=grid(pbpp_count=3)), "fewer 6-byte PBPP vertices than its count"),
        "a chunk after the last vertex": (inline_mesh(part=grid(tail=chunk(b"JUNK", b""))), "has bytes after its last vertex"),
        "a part without its PMVB": (inline_mesh(part=dict(no_pmvb=True)), "without its PMVB"),
        # the end of the stream
        "a CAMD that is not the animation-mode count": (inline_mesh(anim=1, stream=inline_stream(anim=1).replace(chunk(b"CAMD", bytes(36)), chunk(b"CAMD", bytes(35)))),
                                                       "whose CAMD is not its animation-mode count"),
        "a CEMT with another record size": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 335) + bytes(336))), "336-byte emitter record size"),
        "fewer emitters than the record says": (inline_mesh(emitters=2, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(336))), "holds fewer emitters than its count"),
        "an emitter with a part and no index": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(0x40) + struct.pack("<I", 1) + bytes(336 - 0x44))),
                                                "part index is missing or not a part of the mesh"),
        "an emitter whose index is not a part": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(0x40) + struct.pack("<I", 1) + bytes(336 - 0x44)
                                                                                     + struct.pack("<I", 9))), "part index is missing or not a part of the mesh"),
        "bytes after the last emitter": (inline_mesh(emitters=1, cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(336) + b"x")), "bytes after its last emitter"),
        "emitters in the record and no CEMT": (inline_mesh(emitters=1, cemt=b""), "whose CEMT does not start with the 336-byte emitter record size"),
        "no bounding box at the end": (inline_mesh(stream=inline_stream()[:-48]), "without its bounding box"),
        "a chunk after the last": (inline_mesh(tail=chunk(b"JUNK", b"")), "bytes after its last chunk"),
        "a byte after the last": (inline_mesh(tail=b"x"), "bytes after its last chunk"),
        **past_the_limits(),
        # chains: the framing, the reference, the ids, the length, the whole profile for each mesh
        "a chain word and 332 bytes after the mesh": (inline_mesh(stream=inline_stream(cmsh={8: 1}) + bytes(332)), "whose chain word is set and no chained mesh follows"),
        "a chain word and 333 bytes that are not a chained mesh": (inline_mesh(stream=inline_stream(cmsh={8: 1}) + bytes(333)), "is not framed by PMSH and PMS2 headers that fill the rest"),
        "a PMSH header with another tag": (inline_mesh(inline_chain(2, links={1: dict(pmsh_tag=b"PMSX")})), "is not framed by PMSH and PMS2 headers"),
        "a PMS2 header with another tag": (inline_mesh(inline_chain(2, links={1: dict(pms2_tag=b"PMS3")})), "is not framed by PMSH and PMS2 headers"),
        "a PMSH size one short": (inline_mesh(inline_chain(2, links={1: dict(pmsh_delta=-1)})), "is not framed by PMSH and PMS2 headers"),
        "a PMSH size one long": (inline_mesh(inline_chain(2, links={1: dict(pmsh_delta=1)})), "is not framed by PMSH and PMS2 headers"),
        "a PMS2 size one short": (inline_mesh(inline_chain(2, links={1: dict(pms2_delta=-1)})), "is not framed by PMSH and PMS2 headers"),
        "a PMS2 size one long": (inline_mesh(inline_chain(2, links={1: dict(pms2_delta=1)})), "is not framed by PMSH and PMS2 headers"),
        "a chained reference with a name": (inline_mesh(inline_chain(2, links={1: dict(name=b"x")})), "has a reference name that is not all zero"),
        "a chained reference with a second name byte set": (inline_mesh(inline_chain(2, links={1: dict(name=b"\0x")})), "has a reference name that is not all zero"),
        "a chained mesh with runtime id 19999": (inline_mesh(inline_chain(2, ids=[19999])), "has a runtime id outside 20000 to 29999"),
        "a chained mesh with runtime id 30000": (inline_mesh(inline_chain(2, ids=[30000])), "has a runtime id outside 20000 to 29999"),
        "a chained mesh with a shipped mesh's runtime id": (inline_mesh(inline_chain(2, ids=[277])), "has a runtime id outside 20000 to 29999"),
        "a chained mesh with the first mesh's runtime id": (inline_mesh(inline_chain(2, ids=[20000])), "or one that another mesh of the chain has"),
        "two chained meshes with one runtime id": (inline_mesh(inline_chain(3, ids=[20001, 20001])), "or one that another mesh of the chain has"),
        "the last chained mesh with the second one's runtime id": (inline_mesh(inline_chain(4, ids=[20001, 20002, 20001])), "or one that another mesh of the chain has"),
        "a chained reference with an optional word": (inline_mesh(inline_chain(2, links={1: dict(optional=1)})), "has an optional word set or a kept flag that is not 0 or 1"),
        "a chained reference with an optional word whose high byte is set": (inline_mesh(inline_chain(2, links={1: dict(optional=1 << 24)})), "has an optional word set or a kept flag that is not 0 or 1"),
        "a chained reference whose last name byte is set": (inline_mesh(inline_chain(2, links={1: dict(name=bytes(299) + b"x")})), "has a reference name that is not all zero"),
        "a chained reference with a kept flag of 2": (inline_mesh(inline_chain(2, links={1: dict(kept=2)})), "has an optional word set or a kept flag that is not 0 or 1"),
        "a chain of 17 meshes": (inline_mesh(inline_chain(17)), "a chain of more than 16 meshes"),
        "a last mesh whose chain word is set and nothing follows": (inline_mesh(inline_chain(2, last=inline_stream(cmsh={8: 1}))), "whose chain word is set and no chained mesh follows"),
        "a byte after the last chunk of the last mesh of a chain": (inline_mesh(inline_chain(2, last=inline_stream() + b"x")), "bytes after its last chunk"),
        "a byte after a whole chain, so that its headers no longer fill the rest": (inline_mesh(inline_chain(2) + b"x"), "is not framed by PMSH and PMS2 headers that fill the rest"),
        "a skeletal part in a chained mesh": (inline_mesh(inline_chain(2, last=inline_stream(part=dict(words={0x8C: 3})))), "skeletal or a camera"),
        "cutscene sequences in a chained mesh": (inline_mesh(inline_chain(2, last=inline_stream(cmsh={0xC: 1}))), "with cutscene sequences (not admitted)"),
        "17 textures in a chained mesh": (inline_mesh(inline_chain(2, last=inline_stream(textures=17))), "count out of bounds"),
        "a chained mesh without its CMSH": (inline_mesh(inline_stream(cmsh={8: 1}) + chain_link(bytes(400))), "does not start with a 372-byte CMSH record"),
        "the totals of a chain (three meshes of 40000 vertices)": (inline_mesh(inline_chain(3, part=dict(pieces=[dict(vertex_count=40000)]))),
                                                                   "more than 100000 vertices, 600000 indices or 1024 pieces"),
    }


class AdmittedTests(unittest.TestCase):
    def test_the_profile_the_loader_admits_is_admitted(self) -> None:
        cases = admitted_cases()
        self.assertGreater(len(cases), 40)
        for label, mesh in cases.items():
            with self.subTest(label):
                self.assertIsNone(check(mesh))


class RefusedTests(unittest.TestCase):
    def test_each_stream_the_loaders_readers_would_misread_is_refused_for_its_reason(self) -> None:
        cases = refused_cases()
        self.assertGreater(len(cases), 190)
        for label, (mesh, words) in cases.items():
            with self.subTest(label):
                reason = check(mesh)
                self.assertIsNotNone(reason, "admitted what the loader refuses")
                self.assertIn(words, reason)

    def test_every_reason_the_walk_can_give_is_given_by_some_case(self) -> None:
        # the table can fail on any rule: each reason string in the module is the whole answer for at least one authored stream
        reasons = {check(mesh) for mesh, _ in refused_cases().values()}
        source = ast.parse(Path(walk.__file__).read_text())
        literals = {node.value for node in ast.walk(source) if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith("an inline mesh")}
        self.assertGreater(len(literals), 70)
        self.assertEqual(set(), literals - reasons, "reasons no case reaches")
        self.assertEqual(set(), reasons - literals - {None})

    def test_a_reason_is_a_whole_answer_not_a_fragment(self) -> None:
        for label, (mesh, words) in refused_cases().items():
            with self.subTest(label):
                reason = check(mesh)
                self.assertTrue(reason.startswith("an inline mesh"), reason)


class LimitTests(unittest.TestCase):
    def test_the_limits_are_the_loaders_literals(self) -> None:
        # not the module's constants: mods.cpp's kMeshMax* (a change of the loader's profile is a change here in the same step)
        self.assertEqual((16 << 20, 16, 512, 8, 512, 100000, 600000, 1024, 65535, 2, 16384, 32767, 1 << 20, 32767, 16),
                         (walk.MESH_MAX_BYTES, walk.MESH_MAX_TEXTURES, walk.MESH_MAX_PARTS, walk.MESH_MAX_ANIM_MODES, walk.MESH_MAX_EMITTERS, walk.MESH_MAX_VERTICES,
                          walk.MESH_MAX_INDICES, walk.MESH_MAX_GROUPS, walk.MESH_MAX_FRAMES, walk.MESH_MAX_FRAME_SETS, walk.MESH_MAX_CELLS, walk.MESH_MAX_GRID_TRIANGLES,
                          walk.MESH_MAX_GRID_INDICES, walk.MESH_MAX_GRID_VERTICES, walk.MESH_MAX_CHAIN))


class RobustnessTests(unittest.TestCase):
    """The walk answers every stream with None or a reason and never raises: a stager that crashed on a mod's file would refuse nothing."""

    def check(self, stream: bytes) -> None:
        reason = walk.check_inline_mesh(stream)
        self.assertTrue(reason is None or isinstance(reason, str))

    def test_every_truncation_of_a_mesh_with_every_kind_of_chunk(self) -> None:
        emitter = bytearray(336)
        struct.pack_into("<I", emitter, 0x40, 1)
        rich = inline_stream(textures=2, tex_name=b"two.tga", parts=2, anim=1, emitters=1,
                             cemt=chunk(b"CEMT", struct.pack("<i", 336) + bytes(emitter) + struct.pack("<I", 0)),
                             part_list=[inline_part(0, 2, 2, children=[1], grid=inline_grid(), cached=(2, 32, 96)), inline_part(1, 2, 2, parent=0, reference=0)])
        self.assertIsNone(walk.check_inline_mesh(rich))
        for cut in range(len(rich)):
            self.check(rich[:cut])

    def test_every_byte_of_a_mesh_set_to_each_of_four_values(self) -> None:
        stream = inline_stream(textures=2, tex_name=b"two.tga", parts=2, part_list=[inline_part(0, 2, 2, children=[1], grid=inline_grid()), inline_part(1, 2, 2, parent=0)])
        self.assertIsNone(walk.check_inline_mesh(stream))
        for at in range(len(stream)):
            for value in (0x00, 0x01, 0x7F, 0xFF):
                if stream[at] != value:
                    self.check(stream[:at] + bytes([value]) + stream[at + 1:])


if __name__ == "__main__":
    unittest.main()
