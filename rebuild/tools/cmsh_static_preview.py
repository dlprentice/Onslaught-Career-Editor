# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded CMSH static-preview profile v0 parser and OBJ emitter."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import stat
import struct
import sys
from typing import Iterable
import zlib


MAX_SOURCE = 64 * 1024 * 1024
MAX_INFLATE = 128 * 1024 * 1024
MAX_BODY = 32 * 1024 * 1024
MAX_TEXTURES = 256
MAX_PARTS = 256
MAX_GROUPS = 1_024
MAX_VERTICES = 100_000
MAX_INDICES = 600_000
MAX_TRIANGLES = 200_000
MAX_OPAQUE = 16 * 1024 * 1024
MAX_OBJ = 32 * 1024 * 1024
MAX_AGGREGATE_SOURCE = 256 * 1024 * 1024
MAX_COORDINATE = 1_000_000.0
MIN_NORMAL_DETERMINANT = 1e-8
MAX_NORMAL_CONDITION = 1e8
MIN_NORMAL_LENGTH = 1e-12
TEXR_SENTINEL_U32: frozenset[int] = frozenset({0xFFFFFFFF})


class CmshProfileError(ValueError):
    """A deterministic, path-free profile rejection."""

    def __init__(self, category: str, offset: int, role: str, *, space: str = "body") -> None:
        self.category = category
        self.offset = offset
        self.role = role
        self.space = space
        super().__init__(f"{category}: {space} offset 0x{offset:x}: {role}")


@dataclass(frozen=True)
class _Chunk:
    tag: bytes
    payload: memoryview
    offset: int


class _Reader:
    def __init__(self, data: bytes | memoryview, *, origin: int = 0, limit_role: str = "container", absolute_limit: int | None = None) -> None:
        self.data = memoryview(data)
        self.pos = 0
        self.origin = origin
        self.limit_role = limit_role
        self.absolute_limit = absolute_limit

    def _fail(self, category: str, role: str, *, at: int | None = None) -> None:
        raise CmshProfileError(category, self.origin + (self.pos if at is None else at), role)

    def chunk(self, role: str) -> _Chunk:
        start = self.pos
        if len(self.data) - self.pos < 8:
            self._fail("truncation", f"{role} header")
        tag = bytes(self.data[self.pos : self.pos + 4])
        length = struct.unpack_from("<I", self.data, self.pos + 4)[0]
        self.pos += 8
        if length > MAX_BODY:
            self._fail("limit exceeded", f"{role} payload", at=start)
        if self.absolute_limit is not None and self.origin + self.pos + length > self.absolute_limit:
            self._fail("limit exceeded", f"{role} exceeds CMSH body cap", at=start)
        if length > len(self.data) - self.pos:
            self._fail("truncation", f"{role} payload", at=start)
        payload = self.data[self.pos : self.pos + length]
        self.pos += length
        return _Chunk(tag, payload, self.origin + start)

    def expected(self, tag: bytes, role: str, *, length: int | None = None) -> _Chunk:
        chunk = self.chunk(role)
        if chunk.tag != tag:
            category = "unsupported bones/reference graph" if chunk.tag in {b"BONE", b"BONW", b"BONS", b"REFR"} else "unexpected tag/order"
            raise CmshProfileError(category, chunk.offset, f"{role} expected {tag.decode('ascii')}")
        if length is not None and len(chunk.payload) != length:
            raise CmshProfileError("invalid declared length/count", chunk.offset, role)
        return chunk

    def require_end(self) -> None:
        if self.pos != len(self.data):
            self._fail("unexpected tag/order", f"trailing bytes in {self.limit_role}")


@dataclass(frozen=True)
class _Transform:
    rows: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    position: tuple[float, float, float]


@dataclass(frozen=True)
class _BoundingBox:
    center: tuple[float, float, float]
    half_extents: tuple[float, float, float]
    valid: int
    radius: float


@dataclass(frozen=True)
class MeshTexture:
    name: str
    raw_cmst_entry: bytes
    raw_texb_metadata: bytes
    raw_name_field: bytes


@dataclass(frozen=True)
class MeshVertex:
    position: tuple[float, float, float]
    normal: tuple[float, float, float] | None
    uv: tuple[float, float] | None
    raw_color_u32: int
    # Set only when `uv` is None because the released asset stored a non-finite
    # texture coordinate: the two raw dwords, so nothing the file said is lost.
    raw_uv_u32: tuple[int, int] | None = None
    # Skinned (stride-48) vertices only: the three bone slots, already divided
    # back down to `BONE` array indices. See `_SKINNED_VERTEX_STRIDE`.
    bone_slots: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class MeshGroup:
    indices: tuple[int, ...]
    raw_texr_u32: tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class _RigidTrack:
    """The released non-skeletal per-part rigid transform track.

    `hierarchy` holds the `hFrames` distinct authored poses decoded from
    `HORI`/`HPOS`. `frame_map` is the `VHFM` byte per virtual frame, selecting
    which hierarchy pose plays on that frame. `cached_orientations` and
    `cached_positions` are the `CORI`/`CPOS` records, retained only as a
    cross-check: they are a derived model-space composition of `hierarchy`
    along the `PRNT` chain and carry no independent information.
    """

    frame_map: tuple[int, ...]
    hierarchy: tuple[_Transform, ...]
    cached_orientation_bytes: bytes
    cached_position_bytes: bytes


@dataclass(frozen=True)
class _Part:
    name: str
    part_type: int
    transform: _Transform
    bounding_box: _BoundingBox
    vertices: tuple[MeshVertex, ...]
    groups: tuple[MeshGroup, ...]
    children: tuple[int, ...] = ()
    parent: int | None = None
    reference: int | None = None
    track: _RigidTrack | None = None
    # The released `BONE` array: one part index per bone, in slot order. Empty
    # for every part that declares `numBones == 0`.
    bones: tuple[int, ...] = ()


@dataclass(frozen=True)
class ParsedMesh:
    parts: tuple[_Part, ...]
    textures: tuple[MeshTexture, ...] = ()
    # How many released vertices stored a non-finite texture coordinate. This is
    # a property of the shipped asset, not of the decode; see `_parse_pm_vb`.
    non_finite_uv_count: int = 0


_PART_ORDERS = {
    tuple(value.split())
    for value in (
        "PRNT BBOX VHFM HORI HPOS CPOS CORI PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS PBKT CPOS PMVB",
        "PRNT BBOX VHFM HORI HPOS PBKT CPOS PMVB",
        "PRNT BBOX VHFM HORI HPOS CPOS PMVB",
        "PRNT BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB",
        "CHLD BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB",
        "BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB",
        "CHLD BBOX VHFM HORI HPOS CPOS CORI PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS PBKT PMVB",
        "PRNT BBOX VHFM HORI HPOS PBKT PMVB",
        "PRNT BBOX VHFM HORI HPOS HFOV CPOS CORI PMVB",
        "PRNT BBOX VHFM HORI HPOS PMVB",
        "PRNT NMIC BBOX VHFM HORI HPOS PBKT CPOS PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS CPOS CORI PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS CPOS PMVB",
        # 2026-07-31, from the full-corpus mirror sweep: 11 shipped meshes carry
        # this order - the CHLD variant of the CPOS REFR row below, and the
        # CORI-less variant of the CHLD CPOS CORI REFR row. CORI is a derived
        # verification cache (ASSET-EXTRACTION-COVERAGE-2026-07-25.md), so its
        # absence is not a structural difference. Converts 10 of the 19
        # previously-unsupported meshes; index G:\bea-asset-mirror\INDEX.jsonl.
        "CHLD PRNT BBOX VHFM HORI HPOS CPOS REFR PMVB",
        "PRNT BBOX VHFM HORI HPOS CPOS CORI REFR PMVB",
        "PRNT BBOX VHFM HORI HPOS CPOS REFR PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS CPOS CORI REFR PMVB",
        # 2026-07-31: the two skinned orders. `BONE` occurs in exactly 7 shipped
        # meshes and in 0 of the other 206, once per mesh, always on the single
        # part whose CMSP declares numBones != 0. Five meshes present the CORI
        # variant (m_f_dtroop, m_ftrooper, m_mcommando, m_mfiredude, m_mgrunt),
        # two the CORI-less one (m_Sentinel Arm Big, m_Sentinel Arm Small).
        "CHLD PRNT BBOX VHFM HORI HPOS BONE PBKT CPOS CORI PMVB",
        "PRNT BBOX VHFM HORI HPOS BONE PBKT CPOS PMVB",
    )
}

# A skinned part streams a 48-byte vertex and leaves the FVF word zero, because
# the released engine does not describe it with a D3D fixed-function FVF. The
# layout is a rigid stride-36 vertex with three bone slots spliced in after the
# position:
#
#   0x00 float3  position          (part-local, exactly as a rigid vertex)
#   0x0c float3  bone slots        (each = BONE array index * 3)
#   0x18 float3  normal
#   0x24 dword   diffuse
#   0x28 float2  texture coordinate
#
# Measured over all 3,203 shipped skinned vertices: the normal at 0x18 is unit
# length to 1.5e-8 and no other offset is; the diffuse dword at 0x24 is
# 0xffffffff in every one; the coordinate at 0x28 follows the same V-sign
# convention as the rigid path; and every one of the 9,609 slot words is an
# exact non-negative multiple of three whose quotient is a valid BONE index.
#
# WHAT IS NOT RECOVERED: how the three slots are combined. The vertex is fully
# accounted for by the fields above, so it carries no per-vertex blend weight,
# yet the released renderer allocates "Bone slots" and "Bone weights" as
# separate per-part buffers (allocation labels beside
# `C:\dev\ONSLAUGHT2\MeshRenderer.cpp` in the pristine specimen
# `BEA.exe.original.backup`, sha256 74154bfa..., at file offset 0x230077).
# The weighting rule is therefore a runtime property that the asset does not
# state, and nothing here infers one. It does not affect this decoder: the
# stored positions are the bind pose in part-local space, so a static preview
# places a skinned part exactly as it places a rigid one.
_SKINNED_VERTEX_STRIDE = 48
_RIGID_VERTEX_STRIDE = 36
_RIGID_VERTEX_FVF = 0x152
# Each slot holds the bone's base offset in a three-register matrix palette, so
# the stored float is the BONE array index multiplied by three.
_BONE_SLOT_STRIDE = 3
_BONE_SLOTS_PER_VERTEX = 3
_SIBLING_ORDERS = {
    (b"BBOX",),
    (b"BBOX", b"CEMT"),
    (b"CAMD", b"BBOX"),
    (b"CAMD", b"BBOX", b"CEMT"),
    (b"BBOX", b"PMS2"),
    (b"CAMD", b"BBOX", b"CEMT", b"PMS2"),
}


def _u32(data: bytes | memoryview, offset: int, role: str, origin: int) -> int:
    if offset + 4 > len(data):
        raise CmshProfileError("truncation", origin + offset, role)
    return struct.unpack_from("<I", data, offset)[0]


def _finite_floats(data: bytes | memoryview, offset: int, count: int, role: str, origin: int) -> tuple[float, ...]:
    end = offset + count * 4
    if end > len(data):
        raise CmshProfileError("truncation", origin + offset, role)
    values = struct.unpack_from(f"<{count}f", data, offset)
    if not all(math.isfinite(value) for value in values):
        raise CmshProfileError("non-finite numeric value", origin + offset, role)
    return values


def _orientation(data: bytes | memoryview, offset: int, role: str, origin: int) -> tuple[float, ...]:
    values = struct.unpack_from("<12f", data, offset)
    if not all(math.isfinite(values[index]) for index in (0, 1, 2, 4, 5, 6, 8, 9, 10)):
        raise CmshProfileError("non-finite numeric value", origin + offset, role)
    return values


def _rows(
    orientation: tuple[float, ...],
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    """A released 48-byte orientation record is three rows of three floats plus one pad float."""
    return (
        (orientation[0], orientation[1], orientation[2]),
        (orientation[4], orientation[5], orientation[6]),
        (orientation[8], orientation[9], orientation[10]),
    )


def _position(data: bytes | memoryview, offset: int, role: str, origin: int) -> tuple[float, float, float]:
    values = struct.unpack_from("<4f", data, offset)
    if not all(math.isfinite(value) for value in values[:3]):
        raise CmshProfileError("non-finite numeric value", origin + offset, role)
    return values[:3]


@dataclass
class _Budget:
    groups: int = 0
    vertices: int = 0
    indices: int = 0


def inflate_aya(source: bytes) -> bytes:
    if len(source) > MAX_SOURCE:
        raise CmshProfileError("limit exceeded", 0, "AYA source", space="archive")
    position = 0
    output = bytearray()
    record = 0
    while position < len(source):
        header = position
        if len(source) - position < 4:
            raise CmshProfileError("truncation", header, "AYA record header", space="archive")
        compressed_length = struct.unpack_from("<I", source, position)[0]
        position += 4
        if compressed_length == 0 or compressed_length > len(source) - position:
            raise CmshProfileError("invalid framing", header, "AYA compressed length", space="archive")
        compressed = source[position : position + compressed_length]
        position += compressed_length
        decoder = zlib.decompressobj()
        try:
            remaining = MAX_INFLATE - len(output)
            inflated = decoder.decompress(compressed, remaining + 1)
        except zlib.error as error:
            raise CmshProfileError("invalid framing", header, f"AYA zlib member {record}", space="archive") from error
        if len(inflated) > remaining or decoder.unconsumed_tail:
            raise CmshProfileError("limit exceeded", header, "AYA inflate", space="archive")
        if not decoder.eof or decoder.unused_data:
            raise CmshProfileError("invalid framing", header, f"AYA zlib member {record}", space="archive")
        inflated += decoder.flush()
        if len(inflated) > remaining:
            raise CmshProfileError("limit exceeded", header, "AYA inflate", space="archive")
        output.extend(inflated)
        record += 1
    if record == 0:
        raise CmshProfileError("invalid framing", 0, "empty AYA archive", space="archive")
    return bytes(output)


def _vertex_uv(
    data: bytes | memoryview, offset: int, origin: int
) -> tuple[tuple[float, float] | None, tuple[int, int] | None]:
    """A vertex texture coordinate, or `None` plus its raw dwords if non-finite.

    Rejecting the mesh here would diverge from the released loader. `M_Prison.msh`
    stores five non-finite texture coordinates and is loaded by name from four
    shipped level archives (`710_res_PC`, `720_res_PC`, `731_res_PC`,
    `732_res_PC`), so retail demonstrably accepts them. The raw dwords are kept
    and the count is reported; no substitute value is ever invented.
    """
    if offset + 8 > len(data):
        raise CmshProfileError("truncation", origin + offset, "vertex UV")
    values = struct.unpack_from("<2f", data, offset)
    if all(math.isfinite(value) for value in values):
        return values, None
    return None, struct.unpack_from("<2I", data, offset)


def _parse_skinned_vertex(
    data: memoryview, offset: int, origin: int, bone_count: int
) -> tuple[MeshVertex, int]:
    """One stride-48 skinned vertex. Returns it plus 1 if its UV was non-finite."""
    values = _finite_floats(data, offset, 3, "vertex position", origin)
    normal = _finite_floats(data, offset + 0x18, 3, "vertex normal", origin)
    raw_slots = _finite_floats(data, offset + 0x0C, _BONE_SLOTS_PER_VERTEX, "vertex bone slots", origin)
    slots: list[int] = []
    for slot in raw_slots:
        index, remainder = divmod(slot, _BONE_SLOT_STRIDE)
        if remainder or index < 0 or index != int(index):
            raise CmshProfileError("invalid declared length/count", origin + offset, "vertex bone slot")
        if not 0 <= int(index) < bone_count:
            raise CmshProfileError("index out of bounds", origin + offset, "vertex bone slot")
        slots.append(int(index))
    uv, raw_uv = _vertex_uv(data, offset + 0x28, origin)
    raw_color_u32 = struct.unpack_from("<I", data, offset + 0x24)[0]
    return (
        MeshVertex(values, normal, uv, raw_color_u32, raw_uv, (slots[0], slots[1], slots[2])),
        1 if uv is None else 0,
    )


def _parse_rigid_vertex(data: memoryview, offset: int, origin: int) -> tuple[MeshVertex, int]:
    """One stride-36 rigid vertex. Returns it plus 1 if its UV was non-finite."""
    values = _finite_floats(data, offset, 6, "vertex position/normal", origin)
    uv, raw_uv = _vertex_uv(data, offset + 28, origin)
    raw_color_u32 = struct.unpack_from("<I", data, offset + 24)[0]
    return MeshVertex(values[:3], values[3:6], uv, raw_color_u32, raw_uv), 1 if uv is None else 0


def _parse_pm_vb(
    payload: memoryview, origin: int, budget: _Budget, bone_count: int = 0
) -> tuple[tuple[MeshVertex, ...], tuple[MeshGroup, ...], int]:
    reader = _Reader(payload, origin=origin, limit_role="PMVB")
    cmvb = reader.expected(b"CMVB", "CMVB", length=296)
    group_count = cmvb.payload[264]
    if group_count == 0:
        reader.require_end()
        return (), (), 0
    if not 1 <= group_count <= 12:
        raise CmshProfileError("limit exceeded", cmvb.offset, "MMPT group count")
    stride, fvf, topology = struct.unpack_from("<III", cmvb.payload, 276)
    # A skinned part streams the wider vertex and leaves the FVF word zero; a
    # rigid one streams the D3D fixed-function vertex. The part's declared
    # numBones selects which, so the two never have to be guessed apart.
    if bone_count:
        expected_stride, expected_fvf = _SKINNED_VERTEX_STRIDE, 0
    else:
        expected_stride, expected_fvf = _RIGID_VERTEX_STRIDE, _RIGID_VERTEX_FVF
    if stride != expected_stride or fvf != expected_fvf:
        raise CmshProfileError("unsupported profile", cmvb.offset, "stride/FVF")
    if topology != 4:
        raise CmshProfileError("unsupported topology", cmvb.offset, "topology field")

    non_finite_uv = 0
    owned: tuple[MeshVertex, ...] = ()
    groups: list[MeshGroup] = []
    declared_vertex_bytes = vertex_count = None
    for group_index in range(group_count):
        mmpt = reader.expected(b"MMPT", f"MMPT {group_index}", length=24)
        vbytes, ibytes, icount, vcount, primitive_count, active = struct.unpack("<6I", mmpt.payload)
        if active != 1 or icount < 3 or primitive_count != icount - 2 or ibytes != icount * 2:
            raise CmshProfileError("invalid declared length/count", mmpt.offset, f"MMPT {group_index}")
        if icount > MAX_INDICES or budget.indices + icount > MAX_INDICES:
            raise CmshProfileError("limit exceeded", mmpt.offset, "index count")
        if budget.groups + 1 > MAX_GROUPS:
            raise CmshProfileError("limit exceeded", mmpt.offset, "aggregate group count")
        if group_index == 0:
            if vcount == 0 or vcount > MAX_VERTICES:
                raise CmshProfileError("limit exceeded", mmpt.offset, "owned vertex count")
            if budget.vertices + vcount > MAX_VERTICES:
                raise CmshProfileError("limit exceeded", mmpt.offset, "aggregate owned vertex count")
            if vbytes != vcount * expected_stride:
                raise CmshProfileError("invalid declared length/count", mmpt.offset, "owned VBUF declaration")
            declared_vertex_bytes, vertex_count = vbytes, vcount
        elif vbytes != declared_vertex_bytes or vcount != vertex_count:
            raise CmshProfileError("invalid declared length/count", mmpt.offset, "secondary VBUF reuse declaration")
        budget.groups += 1
        budget.indices += icount
        if group_index == 0:
            budget.vertices += vcount
        ibuf = reader.expected(b"IBUF", f"IBUF {group_index}", length=ibytes)
        vbuf = reader.expected(b"VBUF", f"VBUF {group_index}")
        texr = reader.expected(b"TEXR", f"TEXR {group_index}", length=24)
        if group_index == 0:
            if len(vbuf.payload) != vbytes:
                raise CmshProfileError("invalid declared length/count", vbuf.offset, "owned VBUF")
            rows: list[MeshVertex] = []
            for vertex in range(vcount):
                offset = vertex * expected_stride
                if bone_count:
                    row, degraded = _parse_skinned_vertex(
                        vbuf.payload, offset, vbuf.offset + 8, bone_count
                    )
                else:
                    row, degraded = _parse_rigid_vertex(vbuf.payload, offset, vbuf.offset + 8)
                non_finite_uv += degraded
                rows.append(row)
            owned = tuple(rows)
        elif len(vbuf.payload) != 0:
            raise CmshProfileError("invalid declared length/count", vbuf.offset, "secondary VBUF reuse")
        indices = struct.unpack(f"<{icount}H", ibuf.payload)
        if any(index >= (vertex_count or 0) for index in indices):
            raise CmshProfileError("index out of bounds", ibuf.offset, f"IBUF {group_index}")
        if not any(len({indices[k], indices[k + 1], indices[k + 2]}) == 3 for k in range(icount - 2)):
            raise CmshProfileError("invalid declared length/count", ibuf.offset, "strip has no surviving triangle")
        raw_texr_u32 = struct.unpack("<6I", texr.payload)
        groups.append(MeshGroup(tuple(indices), raw_texr_u32))
    reader.require_end()
    return owned, tuple(groups), non_finite_uv


def _validate_reference_source_pm_vb(payload: memoryview, origin: int) -> None:
    reader = _Reader(payload, origin=origin, limit_role="REFR source PMVB")
    cmvb = reader.expected(b"CMVB", "CMVB", length=296)
    if cmvb.payload[264] != 0:
        raise CmshProfileError("unsupported bones/reference graph", cmvb.offset, "REFR populated source PMVB")
    # A zero-group reference owns no vertex stream. Released meshes leave the
    # otherwise-unused stride/FVF/topology words populated with non-semantic
    # data, so framing and the zero group count are the complete contract here.
    reader.require_end()


def _parse_part(
    chunk: _Chunk,
    part_index: int,
    part_count: int,
    budget: _Budget,
    hierarchy_frame: int | None,
) -> tuple[_Part, int]:
    reader = _Reader(chunk.payload, origin=chunk.offset + 8, limit_role="MESP")
    cmsp = reader.expected(b"CMSP", "CMSP", length=316)
    payload = cmsp.payload
    base = _orientation(payload, 0x30, "base orientation", cmsp.offset + 8)
    _orientation(payload, 0x00, "current orientation", cmsp.offset + 8)
    _position(payload, 0x60, "offset position", cmsp.offset + 8)
    position = _position(payload, 0x70, "base position", cmsp.offset + 8)
    number, part_type, child_count = struct.unpack_from("<III", payload, 0x88)
    dvert, pvert, tris, aframes, vframes, hframes, bones = struct.unpack_from("<7I", payload, 0xA8)
    if number != part_index or not 1 <= part_type <= 6 or dvert or pvert or tris:
        raise CmshProfileError("invalid declared length/count", cmsp.offset, "CMSP identity/counts")
    if bones > part_count:
        raise CmshProfileError("limit exceeded", cmsp.offset, "CMSP numBones")
    if child_count > 256 or aframes > 2 or not 1 <= vframes <= 512 or not 1 <= hframes <= 256:
        raise CmshProfileError("limit exceeded", cmsp.offset, "CMSP frame/hierarchy counts")
    raw_name = bytes(payload[0xDC:0xFC])
    name_bytes = raw_name.split(b"\0", 1)[0]
    if b"\0" not in raw_name:
        raise CmshProfileError("invalid declared length/count", cmsp.offset, "CMSP part name")
    try:
        part_name = name_bytes.decode("utf-8") or f"part-{part_index}"
    except UnicodeDecodeError as error:
        raise CmshProfileError("unexpected tag/order", cmsp.offset, "CMSP part name") from error

    tags: list[str] = []
    vertices: tuple[MeshVertex, ...] = ()
    groups: tuple[MeshGroup, ...] = ()
    bone_parts: tuple[int, ...] = ()
    non_finite_uv = 0
    children: tuple[int, ...] = ()
    parent: int | None = None
    reference: int | None = None
    bounding_box: _BoundingBox | None = None
    hierarchy_orientation: tuple[float, ...] | None = None
    hierarchy_position: tuple[float, float, float] | None = None
    frame_map: tuple[int, ...] | None = None
    track_orientations: list[tuple[float, ...]] = []
    track_positions: list[tuple[float, float, float]] = []
    cached_orientation_bytes = b""
    cached_position_bytes = b""
    selected_frame = min(hierarchy_frame, hframes - 1) if hierarchy_frame is not None else None
    while reader.pos < len(reader.data):
        record = reader.chunk("MESP record")
        try:
            tag = record.tag.decode("ascii")
        except UnicodeDecodeError as error:
            raise CmshProfileError("unexpected tag/order", record.offset, "non-ASCII MESP tag") from error
        tags.append(tag)
        if record.tag in {b"BONW", b"BONS"}:
            raise CmshProfileError("unsupported bones/reference graph", record.offset, tag)
        if record.tag == b"BONE":
            # One u32 per bone, each a part index in this same mesh: the skeleton
            # is drawn from the part hierarchy rather than stored separately.
            # Length is exactly numBones * 4 in all 7 shipped skinned meshes.
            if bones == 0 or len(record.payload) != bones * 4:
                raise CmshProfileError("invalid declared length/count", record.offset, "BONE")
            bone_parts = struct.unpack(f"<{bones}I", record.payload)
            if any(bone >= part_count for bone in bone_parts):
                raise CmshProfileError("index out of bounds", record.offset, "BONE")
        elif record.tag == b"CHLD":
            if len(record.payload) != child_count * 4 or child_count == 0:
                raise CmshProfileError("invalid declared length/count", record.offset, "CHLD")
            children = struct.unpack(f"<{child_count}I", record.payload)
            if any(child >= part_count for child in children):
                raise CmshProfileError("index out of bounds", record.offset, "CHLD")
        elif record.tag in {b"PRNT", b"NMIC"}:
            if len(record.payload) != 4:
                raise CmshProfileError("invalid declared length/count", record.offset, tag)
            target = struct.unpack("<I", record.payload)[0]
            if target >= part_count:
                raise CmshProfileError("index out of bounds", record.offset, tag)
            if record.tag == b"PRNT":
                parent = target
        elif record.tag == b"REFR":
            if len(record.payload) != 4:
                raise CmshProfileError("invalid declared length/count", record.offset, "REFR")
            reference = struct.unpack("<I", record.payload)[0]
            if reference >= part_count:
                raise CmshProfileError("index out of bounds", record.offset, "REFR")
        elif record.tag == b"BBOX":
            nested = _Reader(record.payload, origin=record.offset + 8, limit_role="outer BBOX")
            inner = nested.expected(b"BBOX", "inner BBOX", length=40)
            nested.require_end()
            if len(record.payload) != 48:
                raise CmshProfileError("invalid declared length/count", record.offset, "outer BBOX")
            values = struct.unpack("<3fI3fIIf", inner.payload)
            center = values[0:3]
            half_extents = values[4:7]
            valid = values[8]
            radius = values[9]
            bounding_box = _BoundingBox(center, half_extents, valid, radius)
        elif record.tag == b"VHFM":
            if len(record.payload) != vframes:
                raise CmshProfileError("invalid declared length/count", record.offset, "VHFM")
            frame_map = tuple(bytes(record.payload))
        elif record.tag == b"HORI":
            if len(record.payload) != hframes * 48:
                raise CmshProfileError("invalid declared length/count", record.offset, "HORI")
            track_orientations = [
                _orientation(record.payload, frame * 48, "hierarchy orientation", record.offset + 8)
                for frame in range(hframes)
            ]
            if selected_frame is not None:
                hierarchy_orientation = _orientation(
                    record.payload,
                    selected_frame * 48,
                    "selected hierarchy orientation",
                    record.offset + 8,
                )
        elif record.tag == b"HPOS":
            if len(record.payload) != hframes * 16:
                raise CmshProfileError("invalid declared length/count", record.offset, "HPOS")
            track_positions = [
                _position(record.payload, frame * 16, "hierarchy position", record.offset + 8)
                for frame in range(hframes)
            ]
            if selected_frame is not None:
                hierarchy_position = _position(
                    record.payload,
                    selected_frame * 16,
                    "selected hierarchy position",
                    record.offset + 8,
                )
        elif record.tag == b"HFOV":
            if len(record.payload) != hframes * 4:
                raise CmshProfileError("invalid declared length/count", record.offset, "HFOV")
        elif record.tag in {b"PBKT", b"CPOS", b"CORI"}:
            if len(record.payload) > MAX_OPAQUE:
                raise CmshProfileError("limit exceeded", record.offset, tag)
            # CPOS/CORI are the derived model-space composition cache, one
            # record per *virtual* frame (not per hierarchy frame). Released
            # meshes collapse them to a single record when the part and its
            # whole PRNT chain are static.
            if record.tag == b"CPOS":
                cached_position_bytes = bytes(record.payload)
            elif record.tag == b"CORI":
                cached_orientation_bytes = bytes(record.payload)
        elif record.tag == b"PMVB":
            if reference is None:
                vertices, groups, non_finite_uv = _parse_pm_vb(
                    record.payload, record.offset + 8, budget, bones
                )
            else:
                try:
                    _validate_reference_source_pm_vb(record.payload, record.offset + 8)
                except CmshProfileError as error:
                    raise CmshProfileError("unsupported bones/reference graph", record.offset, "REFR source PMVB") from error
        else:
            raise CmshProfileError("unexpected tag/order", record.offset, tag)
    if tuple(tags) not in _PART_ORDERS:
        raise CmshProfileError("unexpected tag/order", chunk.offset, "complete MESP record order")
    if ("CHLD" in tags) != (child_count > 0):
        raise CmshProfileError("invalid declared length/count", chunk.offset, "CHLD presence")
    if ("BONE" in tags) != (bones > 0):
        raise CmshProfileError("invalid declared length/count", chunk.offset, "BONE presence")
    selected_orientation = hierarchy_orientation if hierarchy_orientation is not None else base
    selected_position = hierarchy_position if hierarchy_position is not None else position
    rows = _rows(selected_orientation)
    if bounding_box is None:
        raise CmshProfileError("unexpected tag/order", chunk.offset, "missing BBOX")
    if (
        frame_map is None
        or len(track_orientations) != hframes
        or len(track_positions) != hframes
    ):
        raise CmshProfileError("unexpected tag/order", chunk.offset, "incomplete rigid transform track")
    track = _RigidTrack(
        frame_map,
        tuple(
            _Transform(_rows(track_orientations[frame]), track_positions[frame])
            for frame in range(hframes)
        ),
        cached_orientation_bytes,
        cached_position_bytes,
    )
    return (
        _Part(
            part_name,
            part_type,
            _Transform(rows, selected_position),
            bounding_box,
            vertices,
            groups,
            children,
            parent,
            reference,
            track,
            bone_parts,
        ),
        non_finite_uv,
    )


def _checked_add(total: int, increment: int, limit: int, role: str) -> int:
    if increment < 0 or total > limit or increment > limit - total:
        raise CmshProfileError("limit exceeded", 0, role)
    return total + increment


def _validate_reference_hierarchy(parts: tuple[_Part, ...]) -> None:
    roots = [index for index, part in enumerate(parts) if part.parent is None]
    if len(roots) != 1:
        raise CmshProfileError("unsupported bones/reference graph", 0, "REFR hierarchy roots")
    claimed: dict[int, int] = {}
    for parent_index, part in enumerate(parts):
        for child in part.children:
            if child in claimed:
                raise CmshProfileError("unsupported bones/reference graph", 0, "REFR duplicate parent")
            claimed[child] = parent_index
    for index, part in enumerate(parts):
        if part.parent is None:
            if index in claimed:
                raise CmshProfileError("unsupported bones/reference graph", 0, "REFR root has parent")
        elif claimed.get(index) != part.parent:
            raise CmshProfileError("unsupported bones/reference graph", 0, "REFR hierarchy reciprocity")
    for start in range(len(parts)):
        seen: set[int] = set()
        current: int | None = start
        while current is not None:
            if current in seen:
                raise CmshProfileError("unsupported bones/reference graph", 0, "REFR parent cycle")
            seen.add(current)
            current = parts[current].parent


def _resolve_references(parts: tuple[_Part, ...]) -> tuple[_Part, ...]:
    if not any(part.reference is not None for part in parts):
        return parts
    _validate_reference_hierarchy(parts)
    resolved: list[_Part] = []
    for index, part in enumerate(parts):
        if part.reference is None:
            resolved.append(part)
            continue
        target_index = part.reference
        if target_index >= index:
            raise CmshProfileError("unsupported bones/reference graph", 0, "REFR must target earlier part")
        target = parts[target_index]
        if target.reference is not None:
            raise CmshProfileError("unsupported bones/reference graph", 0, "REFR chained reference")
        if part.vertices or part.groups:
            raise CmshProfileError("unsupported bones/reference graph", 0, "REFR ambiguous geometry source")
        if not target.vertices or not target.groups:
            # The target part is itself empty, so the reference resolves to no
            # geometry and the referring part keeps its own (empty) state. Two
            # shipped references do this, both in `m_Building 5 Top.msh`
            # (parts 2 and 3 -> part 1); the other 386 target real geometry.
            resolved.append(part)
            continue
        resolved.append(
            _Part(
                part.name,
                part.part_type,
                part.transform,
                target.bounding_box,
                target.vertices,
                target.groups,
                part.children,
                part.parent,
                part.reference,
                part.track,
                part.bones,
            )
        )

    expanded_vertices = expanded_indices = expanded_groups = expanded_triangles = 0
    for part in resolved:
        expanded_vertices = _checked_add(expanded_vertices, len(part.vertices), MAX_VERTICES, "expanded vertex count")
        expanded_groups = _checked_add(expanded_groups, len(part.groups), MAX_GROUPS, "expanded group count")
        for group in part.groups:
            indices = group.indices
            expanded_indices = _checked_add(expanded_indices, len(indices), MAX_INDICES, "expanded index count")
            surviving = sum(len({indices[k], indices[k + 1], indices[k + 2]}) == 3 for k in range(len(indices) - 2))
            expanded_triangles = _checked_add(expanded_triangles, surviving, MAX_TRIANGLES, "expanded triangle count")
    return tuple(resolved)


def parse_cmsh_stream(data: bytes, *, hierarchy_frame: int | None = None) -> ParsedMesh:
    if hierarchy_frame is not None and hierarchy_frame < 0:
        raise CmshProfileError("invalid declared length/count", 0, "hierarchy frame")
    if len(data) > MAX_INFLATE:
        raise CmshProfileError("limit exceeded", 0, "inflated CMSH stream")
    if len(data) < 380:
        raise CmshProfileError("truncation", 0, "CMSH header")
    if data[:4] != b"CMSH":
        raise CmshProfileError("unexpected tag/order", 0, "CMSH tag")
    if struct.unpack_from("<I", data, 4)[0] != 372:
        raise CmshProfileError("invalid declared length/count", 0, "CMSH payload")
    texture_count = _u32(data, 0x0C, "texture count", 0)
    part_count = _u32(data, 0x164, "part count", 0)
    if texture_count > MAX_TEXTURES or not 1 <= part_count <= MAX_PARTS:
        raise CmshProfileError("limit exceeded", 0, "CMSH counts")
    reader = _Reader(memoryview(data)[380:], origin=380, limit_role="CMSH stream", absolute_limit=MAX_BODY)
    cmst = reader.expected(b"CMST", "CMST", length=texture_count * 36)
    textures: list[MeshTexture] = []
    for index in range(texture_count):
        msht = reader.expected(b"MSHT", f"MSHT {index}", length=156)
        nested = _Reader(msht.payload, origin=msht.offset + 8, limit_role="MSHT")
        texb = nested.expected(b"TEXB", f"TEXB {index}", length=148)
        nested.require_end()
        raw_name_field = bytes(texb.payload[20:148])
        name_bytes = raw_name_field.split(b"\0", 1)[0]
        name = name_bytes.decode("utf-8", errors="replace")
        textures.append(
            MeshTexture(
                name=name,
                raw_cmst_entry=bytes(cmst.payload[index * 36 : (index + 1) * 36]),
                raw_texb_metadata=bytes(texb.payload[:20]),
                raw_name_field=raw_name_field,
            )
        )
    part_chunks = [reader.expected(b"MESP", f"MESP {index}") for index in range(part_count)]
    budget = _Budget()
    decoded = [
        _parse_part(chunk, index, part_count, budget, hierarchy_frame)
        for index, chunk in enumerate(part_chunks)
    ]
    non_finite_uv = sum(count for _, count in decoded)
    parts = _resolve_references(tuple(part for part, _ in decoded))
    reader.absolute_limit = None
    siblings: list[bytes] = []
    while reader.pos < len(reader.data):
        sibling = reader.chunk("post-body sibling")
        if len(sibling.payload) > MAX_OPAQUE:
            raise CmshProfileError("limit exceeded", sibling.offset, "post-body sibling")
        siblings.append(sibling.tag)
    if siblings and tuple(siblings) not in _SIBLING_ORDERS:
        raise CmshProfileError("unexpected tag/order", reader.origin, "post-body sibling order")
    return ParsedMesh(parts, tuple(textures), non_finite_uv)


def _number(value: float) -> str:
    if value == 0.0:
        return "0"
    return repr(value)


def _obj_attribute(
    value: tuple[float, ...] | None,
    count: int,
    role: str,
) -> tuple[float, ...] | None:
    if value is None:
        return None
    if not isinstance(value, tuple) or len(value) != count:
        raise CmshProfileError("invalid declared length/count", 0, role)
    if not all(isinstance(component, (int, float)) and math.isfinite(component) for component in value):
        raise CmshProfileError("non-finite numeric value", 0, role)
    return value


def _normal_matrix(
    rows: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    a, b, c = rows[0]
    d, e, f = rows[1]
    g, h, i = rows[2]
    cofactors = (
        (e * i - f * h, f * g - d * i, d * h - e * g),
        (c * h - b * i, a * i - c * g, b * g - a * h),
        (b * f - c * e, c * d - a * f, a * e - b * d),
    )
    determinant = a * cofactors[0][0] + b * cofactors[0][1] + c * cofactors[0][2]
    if not math.isfinite(determinant) or abs(determinant) < MIN_NORMAL_DETERMINANT:
        raise CmshProfileError("OBJ rejection", 0, "degenerate normal transform")
    inverse_transpose = tuple(
        tuple(component / determinant for component in row)
        for row in cofactors
    )
    matrix_norm = max(sum(abs(component) for component in row) for row in rows)
    inverse_norm = max(
        sum(abs(inverse_transpose[column][row]) for column in range(3))
        for row in range(3)
    )
    condition = matrix_norm * inverse_norm
    if not math.isfinite(condition) or condition > MAX_NORMAL_CONDITION:
        raise CmshProfileError("OBJ rejection", 0, "ill-conditioned normal transform")
    return inverse_transpose


def _transform_obj_normal(
    matrix: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
    normal: tuple[float, float, float],
) -> tuple[float, float, float]:
    x, y, z = normal
    transformed = (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z,
        -(matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z),
    )
    length = math.sqrt(sum(component * component for component in transformed))
    if not math.isfinite(length) or length < MIN_NORMAL_LENGTH:
        raise CmshProfileError("OBJ rejection", 0, "degenerate transformed normal")
    return tuple(0.0 if abs(component / length) < 1e-15 else component / length for component in transformed)


def emit_obj(
    mesh: ParsedMesh,
    *,
    include_vertex_attributes: bool = False,
    include_material_layer_groups: bool = False,
    include_vertex_colors: bool = False,
) -> bytes:
    lines: list[str] = []
    encoded_bytes = 0

    def append_line(line: str) -> None:
        nonlocal encoded_bytes
        encoded_bytes = _checked_add(encoded_bytes, len(line.encode("utf-8")) + 1, MAX_OBJ, "OBJ bytes")
        lines.append(line)

    bases: list[int | None] = []
    emitted_vertices = 0
    for part in mesh.parts:
        if not part.vertices:
            bases.append(None)
            continue
        bases.append(emitted_vertices + 1)
        rows = part.transform.rows
        bx, by, bz = part.transform.position
        for vertex in part.vertices:
            x, y, z = vertex.position
            tx = (((rows[0][0] * x) + (rows[0][1] * y)) + (rows[0][2] * z)) + bx
            ty = (((rows[1][0] * x) + (rows[1][1] * y)) + (rows[1][2] * z)) + by
            tz = (((rows[2][0] * x) + (rows[2][1] * y)) + (rows[2][2] * z)) + bz
            values = (tx, ty, -tz)
            if not all(math.isfinite(value) for value in values):
                raise CmshProfileError("non-finite numeric value", 0, "transformed position")
            if any(abs(value) > MAX_COORDINATE for value in values):
                raise CmshProfileError("limit exceeded", 0, "transformed position")
            record = "v " + " ".join(_number(value) for value in values)
            if include_vertex_colors:
                # FVF 0x152 carries a D3DCOLOR DIFFUSE dword at vertex offset 24.
                # Retail keeps D3DRS_LIGHTING on with D3DRS_DIFFUSEMATERIALSOURCE
                # and D3DRS_AMBIENTMATERIALSOURCE both D3DMCS_COLOR1, so this dword
                # is the per-vertex diffuse and ambient material reflectance.
                color = vertex.raw_color_u32
                alpha = (color >> 24) & 0xFF
                if alpha != 0xFF:
                    # Stage zero also runs ALPHAOP MODULATE against D3DTA_DIFFUSE.
                    # No mesh in the retail corpus carries a non-opaque vertex
                    # alpha, and the OBJ colour extension cannot express one, so
                    # refuse rather than silently drop it.
                    raise CmshProfileError(
                        "unsupported profile", 0, "non-opaque vertex diffuse alpha"
                    )
                record += " " + " ".join(
                    _number(((color >> shift) & 0xFF) / 255.0)
                    for shift in (16, 8, 0)
                )
            append_line(record)
            emitted_vertices = _checked_add(emitted_vertices, 1, MAX_VERTICES, "OBJ vertices")

    uv_indices: list[tuple[int | None, ...] | None] = [None] * len(mesh.parts)
    normal_indices: list[tuple[int | None, ...] | None] = [None] * len(mesh.parts)
    if include_vertex_attributes:
        emitted_uvs = 0
        for part_index, part in enumerate(mesh.parts):
            indices: list[int | None] = []
            for vertex in part.vertices:
                uv = _obj_attribute(vertex.uv, 2, "vertex UV")
                if uv is None:
                    indices.append(None)
                    continue
                emitted_uvs = _checked_add(emitted_uvs, 1, MAX_VERTICES, "OBJ texture coordinates")
                indices.append(emitted_uvs)
                append_line("vt " + " ".join(_number(value) for value in uv))
            uv_indices[part_index] = tuple(indices)

        emitted_normals = 0
        for part_index, part in enumerate(mesh.parts):
            indices = []
            normal_matrix = _normal_matrix(part.transform.rows) if part.vertices else None
            for vertex in part.vertices:
                normal = _obj_attribute(vertex.normal, 3, "vertex normal")
                if normal is None:
                    indices.append(None)
                    continue
                if normal_matrix is None:
                    raise CmshProfileError("OBJ rejection", 0, "missing normal transform")
                values = _transform_obj_normal(normal_matrix, normal)
                emitted_normals = _checked_add(emitted_normals, 1, MAX_VERTICES, "OBJ normals")
                indices.append(emitted_normals)
                append_line("vn " + " ".join(_number(value) for value in values))
            normal_indices[part_index] = tuple(indices)

    faces = 0
    for part_index, (part, base) in enumerate(zip(mesh.parts, bases, strict=True)):
        if base is None:
            continue
        part_uvs = uv_indices[part_index]
        part_normals = normal_indices[part_index]
        if include_vertex_attributes and (
            part_uvs is None
            or part_normals is None
            or len(part_uvs) != len(part.vertices)
            or len(part_normals) != len(part.vertices)
        ):
            raise CmshProfileError("invalid declared length/count", 0, "OBJ vertex attributes")

        def face_reference(index: int, *, with_uv: bool = True) -> str:
            vertex_index = index + base
            uv_index = (part_uvs[index] if part_uvs is not None else None) if with_uv else None
            normal_index = part_normals[index] if part_normals is not None else None
            if uv_index is not None and normal_index is not None:
                return f"{vertex_index}/{uv_index}/{normal_index}"
            if uv_index is not None:
                return f"{vertex_index}/{uv_index}"
            if normal_index is not None:
                return f"{vertex_index}//{normal_index}"
            return str(vertex_index)

        for group in part.groups:
            if include_material_layer_groups:
                for texture_index in group.raw_texr_u32:
                    if texture_index not in TEXR_SENTINEL_U32 and texture_index >= len(mesh.textures):
                        raise CmshProfileError("OBJ rejection", 0, "unresolved material texture")
                signature = "-".join(f"{texture_index:08x}" for texture_index in group.raw_texr_u32)
                append_line(f"usemtl layers-{signature}")
            indices = group.indices
            for ordinal in range(len(indices) - 2):
                if ordinal % 2 == 0:
                    a, b, c = indices[ordinal : ordinal + 3]
                else:
                    b, a, c = indices[ordinal : ordinal + 3]
                if len({a, b, c}) < 3:
                    continue
                if not all(0 <= index < len(part.vertices) for index in (a, b, c)):
                    raise CmshProfileError("OBJ rejection", 0, "face index")
                a, b, c = a + base, c + base, b + base
                if not (1 <= a <= emitted_vertices and 1 <= b <= emitted_vertices and 1 <= c <= emitted_vertices):
                    raise CmshProfileError("OBJ rejection", 0, "face index")
                local_a, local_b, local_c = a - base, b - base, c - base
                # OBJ requires one reference form per face element. A released
                # vertex whose texture coordinate was non-finite has no `vt`, so
                # the whole face drops its texture-coordinate component rather
                # than mixing forms or inventing a substitute coordinate.
                with_uv = part_uvs is None or all(
                    part_uvs[local] is not None for local in (local_a, local_b, local_c)
                )
                append_line(
                    "f "
                    + " ".join(
                        face_reference(local, with_uv=with_uv)
                        for local in (local_a, local_b, local_c)
                    )
                )
                faces = _checked_add(faces, 1, MAX_TRIANGLES, "OBJ faces")
    if emitted_vertices == 0 or faces == 0:
        raise CmshProfileError("OBJ rejection", 0, "empty geometry")
    result = ("\n".join(lines) + "\n").encode("utf-8")
    if len(result) != encoded_bytes:
        raise CmshProfileError("OBJ rejection", 0, "OBJ byte accounting")
    return result


MAX_CACHED_ORIENTATION_DELTA = 1e-5
MAX_CACHED_POSITION_DELTA = 1e-4

_IDENTITY_ROWS = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _matrix_multiply(left, right):
    """(left * right)[i][j] = sum_k left[i][k]*right[k][j] — row-major storage, column vectors."""
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )


def _apply(matrix, vector) -> tuple[float, float, float]:
    return tuple(sum(matrix[i][k] * vector[k] for k in range(3)) for i in range(3))


def obj_part_vertex_ranges(mesh: ParsedMesh) -> tuple[tuple[int, int] | None, ...]:
    """The 1-based OBJ `v` index range each part occupies in `emit_obj` output."""
    ranges: list[tuple[int, int] | None] = []
    emitted = 0
    for part in mesh.parts:
        if not part.vertices:
            ranges.append(None)
            continue
        ranges.append((emitted + 1, len(part.vertices)))
        emitted += len(part.vertices)
    return tuple(ranges)


def _compose_model_space(mesh: ParsedMesh, virtual_frame: int):
    """Model-space (rows, position) per part on one virtual frame, composed root->leaf."""
    resolved: list[tuple[tuple, tuple[float, float, float]] | None] = [None] * len(mesh.parts)

    def resolve(index: int):
        cached = resolved[index]
        if cached is not None:
            return cached
        part = mesh.parts[index]
        track = part.track
        if track is None:
            raise CmshProfileError("unexpected tag/order", 0, "missing rigid transform track")
        local = track.hierarchy[track.frame_map[virtual_frame]]
        if part.parent is None:
            value = (local.rows, local.position)
        else:
            parent_rows, parent_position = resolve(part.parent)
            value = (
                _matrix_multiply(parent_rows, local.rows),
                tuple(
                    a + b
                    for a, b in zip(_apply(parent_rows, local.position), parent_position)
                ),
            )
        resolved[index] = value
        return value

    for index in range(len(mesh.parts)):
        resolve(index)
    return resolved


def build_rigid_transform_tracks(mesh: ParsedMesh) -> dict[str, object]:
    """Decode the released per-part rigid transform tracks into OBJ-space deltas.

    Returns one entry per part that carries geometry, giving the part's OBJ
    vertex range and — when the part or any `PRNT` ancestor has more than one
    authored hierarchy pose — one delta transform per virtual frame that maps
    the emitted rest vertices onto that frame. No resampling, interpolation, or
    smoothing occurs: the virtual frame count is exactly the released `vFrames`.

    Every composed frame is checked against the released `CPOS`/`CORI` cache and
    a disagreement is a hard rejection.
    """
    if not mesh.parts or any(part.track is None for part in mesh.parts):
        raise CmshProfileError("unexpected tag/order", 0, "missing rigid transform track")
    virtual_frames = len(mesh.parts[0].track.frame_map)
    if virtual_frames < 1 or any(len(part.track.frame_map) != virtual_frames for part in mesh.parts):
        raise CmshProfileError("invalid declared length/count", 0, "inconsistent virtual frame counts")
    for part in mesh.parts:
        if any(frame >= len(part.track.hierarchy) for frame in part.track.frame_map):
            raise CmshProfileError("index out of bounds", 0, "VHFM maps beyond a stored pose")

    composed = [_compose_model_space(mesh, frame) for frame in range(virtual_frames)]

    # Cross-check the composition against the released CPOS/CORI cache. A
    # released mesh stores either one record (the whole PRNT chain is static)
    # or exactly `vFrames` records; anything else is a rejection.
    cached_positions: list[tuple[tuple[float, float, float], ...]] = []
    cached_orientations: list[tuple[tuple, ...]] = []
    for part in mesh.parts:
        raw_position = part.track.cached_position_bytes
        raw_orientation = part.track.cached_orientation_bytes
        if len(raw_position) not in (0, 16, virtual_frames * 16):
            raise CmshProfileError("invalid declared length/count", 0, "CPOS record count")
        if len(raw_orientation) not in (0, 48, virtual_frames * 48):
            raise CmshProfileError("invalid declared length/count", 0, "CORI record count")
        cached_positions.append(
            tuple(
                _position(raw_position, frame * 16, "cached position", 0)
                for frame in range(len(raw_position) // 16)
            )
        )
        cached_orientations.append(
            tuple(
                _rows(_orientation(raw_orientation, frame * 48, "cached orientation", 0))
                for frame in range(len(raw_orientation) // 48)
            )
        )

    worst_orientation = 0.0
    worst_position = 0.0
    for frame in range(virtual_frames):
        for index in range(len(mesh.parts)):
            rows, position = composed[frame][index]
            stored_positions = cached_positions[index]
            stored_orientations = cached_orientations[index]
            if stored_positions:
                stored = stored_positions[min(frame, len(stored_positions) - 1)]
                worst_position = max(
                    worst_position, max(abs(a - b) for a, b in zip(position, stored))
                )
            if stored_orientations:
                stored_rows = stored_orientations[min(frame, len(stored_orientations) - 1)]
                worst_orientation = max(
                    worst_orientation,
                    max(abs(rows[i][j] - stored_rows[i][j]) for i in range(3) for j in range(3)),
                )
    if worst_orientation > MAX_CACHED_ORIENTATION_DELTA or worst_position > MAX_CACHED_POSITION_DELTA:
        raise CmshProfileError("OBJ rejection", 0, "CPOS/CORI cache disagrees with the composed track")

    # The emitted OBJ places every part by its CMSP base transform, so the rest
    # pose the deltas below are relative to must be virtual frame 0. Released
    # meshes satisfy this exactly; a mesh parsed with an explicit hierarchy
    # frame does not, and must not reach here.
    for index, part in enumerate(mesh.parts):
        rows, position = composed[0][index]
        if (
            max(abs(rows[i][j] - part.transform.rows[i][j]) for i in range(3) for j in range(3))
            > MAX_CACHED_ORIENTATION_DELTA
            or max(abs(a - b) for a, b in zip(position, part.transform.position))
            > MAX_CACHED_POSITION_DELTA
        ):
            raise CmshProfileError("OBJ rejection", 0, "rest pose is not virtual frame 0")

    ranges = obj_part_vertex_ranges(mesh)
    animated_chain = [False] * len(mesh.parts)
    for index, part in enumerate(mesh.parts):
        moving = len(part.track.hierarchy) > 1
        if part.parent is not None:
            moving = moving or animated_chain[part.parent]
        animated_chain[index] = moving

    parts: list[dict[str, object]] = []
    for index, part in enumerate(mesh.parts):
        vertex_range = ranges[index]
        if vertex_range is None:
            continue
        rest_rows, rest_position = composed[0][index]
        record: dict[str, object] = {
            "hierarchyFrameCount": len(part.track.hierarchy),
            "name": part.name,
            "objVertexCount": vertex_range[1],
            "objVertexStart": vertex_range[0],
            "parent": part.parent,
            "part": index,
        }
        if animated_chain[index]:
            # rest orientation is orthonormal, so its inverse is its transpose.
            inverse_rest = tuple(
                tuple(rest_rows[j][i] for j in range(3)) for i in range(3)
            )
            frames: list[dict[str, object]] = []
            for frame in range(virtual_frames):
                rows, position = composed[frame][index]
                delta_rows = _matrix_multiply(rows, inverse_rest)
                delta_position = tuple(
                    a - b for a, b in zip(position, _apply(delta_rows, rest_position))
                )
                # emit_obj writes (x, y, -z); conjugate the delta by diag(1,1,-1)
                # so it applies directly to the emitted OBJ vertices.
                signs = (1.0, 1.0, -1.0)
                obj_rows = tuple(
                    tuple(delta_rows[i][j] * signs[i] * signs[j] for j in range(3))
                    for i in range(3)
                )
                frames.append(
                    {
                        "basis": [value for row in obj_rows for value in row],
                        "origin": [delta_position[i] * signs[i] for i in range(3)],
                    }
                )
            record["frames"] = frames
        parts.append(record)

    return {
        "cachedOrientationDelta": worst_orientation,
        "cachedPositionDelta": worst_position,
        "frameMaps": {
            str(index): list(part.track.frame_map)
            for index, part in enumerate(mesh.parts)
            if len(part.track.hierarchy) > 1
        },
        "hierarchyFrameCount": max(len(part.track.hierarchy) for part in mesh.parts),
        "parts": parts,
        "virtualFrameCount": virtual_frames,
    }


def emit_material_report(mesh: ParsedMesh) -> bytes:
    texture_names = [texture.name for texture in mesh.textures]
    parts: list[dict[str, object]] = []
    for part_index, part in enumerate(mesh.parts):
        groups: list[dict[str, object]] = []
        for group in part.groups:
            positions: list[dict[str, object]] = []
            for position, raw_u32 in enumerate(group.raw_texr_u32):
                row: dict[str, object] = {
                    "position": position,
                    "rawU32": raw_u32,
                    "retailSemantic": (
                        "base"
                        if position == 0
                        else "dot3Lighting"
                        if position == 1
                        else "environmentReflection"
                        if position == 2
                        else "disabledProjective"
                        if position == 3
                        else "alphaOverlay"
                        if position == 4
                        else "disabled"
                    ),
                    "status": "unresolved",
                }
                if raw_u32 in TEXR_SENTINEL_U32:
                    row["status"] = "sentinel"
                elif raw_u32 < len(mesh.textures):
                    row["status"] = "resolved"
                    row["textureIndex"] = raw_u32
                    row["textureName"] = mesh.textures[raw_u32].name
                positions.append(row)
            groups.append({"rawTexrU32": list(group.raw_texr_u32), "positions": positions})
        parts.append(
            {
                "partIndex": part_index,
                "geometrySourcePart": part.reference if part.reference is not None else part_index,
                "groups": groups,
            }
        )
    report = {
        "schemaVersion": "onslaught-cmsh-material-report.v1",
        "acceptedSentinelU32": sorted(TEXR_SENTINEL_U32),
        "retailPositionSemantics": [
            "base",
            "dot3Lighting",
            "environmentReflection",
            "disabledProjective",
            "alphaOverlay",
            "disabled",
        ],
        "textures": texture_names,
        "parts": parts,
    }
    result = (json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(result) > MAX_OBJ:
        raise CmshProfileError("limit exceeded", 0, "material report bytes")
    return result


def convert_aya_bytes(
    source: bytes,
    *,
    include_vertex_attributes: bool = False,
    include_material_layer_groups: bool = False,
    include_vertex_colors: bool = False,
    hierarchy_frame: int | None = None,
) -> bytes:
    return emit_obj(
        parse_cmsh_stream(inflate_aya(source), hierarchy_frame=hierarchy_frame),
        include_vertex_attributes=include_vertex_attributes,
        include_material_layer_groups=include_material_layer_groups,
        include_vertex_colors=include_vertex_colors,
    )


def _has_reparse_point(path: Path) -> bool:
    attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)) or path.is_symlink()


def _within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _validate_no_reparse_descendant(path: Path, root: Path, trusted_checkout: Path, *, must_exist: bool) -> None:
    if not _within(path, root):
        raise CmshProfileError("invalid framing", 0, "local path confinement")
    current = trusted_checkout
    for component in path.relative_to(trusted_checkout).parts:
        current /= component
        if os.path.lexists(current) and _has_reparse_point(current):
            raise CmshProfileError("invalid framing", 0, "reparse component")
    if must_exist and not path.exists():
        raise CmshProfileError("invalid framing", 0, "input directory")


def publish_anonymous_previews(
    checkout: Path,
    input_directory: Path,
    output_directory: Path,
    *,
    include_vertex_attributes: bool = False,
    include_material_layer_groups: bool = False,
    hierarchy_frame: int | None = None,
) -> tuple[int, int]:
    trusted_checkout = Path(__file__).resolve().parents[2]
    checkout = _absolute_lexical(checkout)
    input_directory = _absolute_lexical(input_directory)
    output_directory = _absolute_lexical(output_directory)
    if os.path.normcase(str(checkout)) != os.path.normcase(str(trusted_checkout)):
        raise CmshProfileError("invalid framing", 0, "trusted checkout")
    allowed_inputs = (
        checkout / "game",
        checkout / "local-lab" / "rebuild-godot" / "input",
        checkout / "rebuild" / "OnslaughtRebuild.Godot" / "Assets" / "Aquila" / "Source",
        checkout / "rebuild" / "OnslaughtRebuild.Godot" / "Assets" / "Level100" / "Source",
    )
    allowed_output = checkout / "local-lab" / "rebuild-godot" / "generated"
    try:
        input_root = next((root for root in allowed_inputs if _within(input_directory, root)), None)
        if input_root is None:
            raise CmshProfileError("invalid framing", 0, "input root")
        _validate_no_reparse_descendant(input_directory, input_root, checkout, must_exist=True)
        _validate_no_reparse_descendant(output_directory, allowed_output, checkout, must_exist=False)
        if not input_directory.is_dir():
            raise CmshProfileError("invalid framing", 0, "input directory")
        if output_directory.exists() and any(output_directory.iterdir()):
            raise CmshProfileError("invalid framing", 0, "output session must be empty")
        candidates = sorted(
            (path for path in input_directory.iterdir() if path.suffix.lower() == ".aya"),
            key=lambda path: path.name.casefold(),
        )
        if len(candidates) > 256:
            raise CmshProfileError("limit exceeded", 0, "candidate count")
        aggregate_bytes = 0
        for source in candidates:
            metadata = os.lstat(source)
            if _has_reparse_point(source) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise CmshProfileError("invalid framing", 0, "candidate file")
            if metadata.st_size > MAX_SOURCE:
                raise CmshProfileError("limit exceeded", 0, "candidate source bytes")
            aggregate_bytes += metadata.st_size
            if aggregate_bytes > MAX_AGGREGATE_SOURCE:
                raise CmshProfileError("limit exceeded", 0, "aggregate candidate source bytes")
    except OSError as error:
        raise CmshProfileError("invalid framing", 0, "local preflight") from error

    tools_root = trusted_checkout / "tools"
    if str(tools_root) not in sys.path:
        sys.path.insert(0, str(tools_root))
    from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError  # type: ignore[import-not-found]

    matches = failures = 0
    categories: Counter[str] = Counter()
    published: list[Path] = []
    try:
        with SecuredOutputRoot(output_directory, protected_sources=[input_directory, *candidates]) as secured:
            for ordinal, source in enumerate(candidates, 1):
                metadata = os.lstat(source)
                if _has_reparse_point(source) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                    raise CmshProfileError("invalid framing", 0, "held candidate file")
                data = source.read_bytes()
                if len(data) != metadata.st_size:
                    raise CmshProfileError("invalid framing", 0, "candidate changed during read")
                anonymous = f"candidate-{ordinal:04d}"
                try:
                    obj = convert_aya_bytes(
                        data,
                        include_vertex_attributes=include_vertex_attributes,
                        include_material_layer_groups=include_material_layer_groups,
                        hierarchy_frame=hierarchy_frame,
                    )
                except CmshProfileError as error:
                    failures += 1
                    categories[error.category] += 1
                    continue
                with secured.atomic_binary_writer(output_directory / f"{anonymous}.obj") as writer:
                    writer.write(obj)
                published.append(output_directory / f"{anonymous}.obj")
                matches += 1
            summary = {
                "schemaVersion": "onslaught-cmsh-static-preview-summary.v0",
                "matched": matches,
                "rejected": failures,
                "categories": dict(sorted(categories.items())),
            }
            with secured.atomic_text_writer(output_directory / "summary.json") as writer:
                json.dump(summary, writer, sort_keys=True, separators=(",", ":"))
                writer.write("\n")
    except (CmshProfileError, OSError, UnsafeGeneratedOutputError) as error:
        for path in published:
            try:
                metadata = os.lstat(path)
                if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1 and not _has_reparse_point(path):
                    path.unlink()
            except OSError:
                pass
        if isinstance(error, CmshProfileError):
            raise
        raise CmshProfileError("invalid framing", 0, "guarded local publication") from error
    return matches, failures


def _main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate anonymous local CMSH profile-v0 OBJ previews")
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--vertex-attributes",
        action="store_true",
        help="include retained profile-v0 texture coordinates and normals in OBJ output",
    )
    parser.add_argument(
        "--material-layer-groups",
        action="store_true",
        help="emit one OBJ material group per MMPT using its complete six-slot TEXR signature",
    )
    parser.add_argument(
        "--hierarchy-frame",
        type=int,
        help="select one authored hierarchy frame for every part, clamped to each part's available track",
    )
    arguments = parser.parse_args(argv)
    if arguments.hierarchy_frame is not None and arguments.hierarchy_frame < 0:
        parser.error("--hierarchy-frame must be non-negative")
    try:
        matches, failures = publish_anonymous_previews(
            arguments.checkout,
            arguments.input,
            arguments.output,
            include_vertex_attributes=arguments.vertex_attributes,
            include_material_layer_groups=arguments.material_layer_groups,
            hierarchy_frame=arguments.hierarchy_frame,
        )
    except (CmshProfileError, OSError) as error:
        print(f"preview failed: {error}", file=sys.stderr)
        return 2
    print(f"anonymous previews: {matches} matched, {failures} rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
