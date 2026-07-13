# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded CMSH static-preview profile v0 parser and geometry-only OBJ emitter."""

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
class _Part:
    transform: _Transform
    vertices: tuple[tuple[float, float, float], ...]
    groups: tuple[tuple[int, ...], ...]
    children: tuple[int, ...] = ()
    parent: int | None = None
    reference: int | None = None


@dataclass(frozen=True)
class ParsedMesh:
    parts: tuple[_Part, ...]


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
        "PRNT BBOX VHFM HORI HPOS CPOS CORI REFR PMVB",
        "CHLD PRNT BBOX VHFM HORI HPOS CPOS CORI REFR PMVB",
    )
}
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


def _parse_pm_vb(payload: memoryview, origin: int, budget: _Budget) -> tuple[tuple[tuple[float, float, float], ...], tuple[tuple[int, ...], ...]]:
    reader = _Reader(payload, origin=origin, limit_role="PMVB")
    cmvb = reader.expected(b"CMVB", "CMVB", length=296)
    group_count = cmvb.payload[264]
    if group_count == 0:
        reader.require_end()
        return (), ()
    if not 1 <= group_count <= 12:
        raise CmshProfileError("limit exceeded", cmvb.offset, "MMPT group count")
    stride, fvf, topology = struct.unpack_from("<III", cmvb.payload, 276)
    if stride != 36 or fvf != 0x152:
        raise CmshProfileError("unsupported profile", cmvb.offset, "stride/FVF")
    if topology != 4:
        raise CmshProfileError("unsupported topology", cmvb.offset, "topology field")

    owned: tuple[tuple[float, float, float], ...] = ()
    groups: list[tuple[int, ...]] = []
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
            if vbytes != vcount * 36:
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
        reader.expected(b"TEXR", f"TEXR {group_index}", length=24)
        if group_index == 0:
            if len(vbuf.payload) != vbytes:
                raise CmshProfileError("invalid declared length/count", vbuf.offset, "owned VBUF")
            rows: list[tuple[float, float, float]] = []
            for vertex in range(vcount):
                offset = vertex * 36
                values = _finite_floats(vbuf.payload, offset, 6, "vertex position/normal", vbuf.offset + 8)
                _finite_floats(vbuf.payload, offset + 28, 2, "vertex UV", vbuf.offset + 8)
                rows.append((values[0], values[1], values[2]))
            owned = tuple(rows)
        elif len(vbuf.payload) != 0:
            raise CmshProfileError("invalid declared length/count", vbuf.offset, "secondary VBUF reuse")
        indices = struct.unpack(f"<{icount}H", ibuf.payload)
        if any(index >= (vertex_count or 0) for index in indices):
            raise CmshProfileError("index out of bounds", ibuf.offset, f"IBUF {group_index}")
        if not any(len({indices[k], indices[k + 1], indices[k + 2]}) == 3 for k in range(icount - 2)):
            raise CmshProfileError("invalid declared length/count", ibuf.offset, "strip has no surviving triangle")
        groups.append(tuple(indices))
    reader.require_end()
    return owned, tuple(groups)


def _validate_reference_source_pm_vb(payload: memoryview, origin: int) -> None:
    reader = _Reader(payload, origin=origin, limit_role="REFR source PMVB")
    cmvb = reader.expected(b"CMVB", "CMVB", length=296)
    if cmvb.payload[264] != 0:
        raise CmshProfileError("unsupported bones/reference graph", cmvb.offset, "REFR populated source PMVB")
    stride, fvf, topology = struct.unpack_from("<III", cmvb.payload, 276)
    if (stride, fvf, topology) not in {(36, 0x152, 4), (0, 0, 0)}:
        raise CmshProfileError("unsupported profile", cmvb.offset, "REFR source stride/FVF/topology")
    reader.require_end()


def _parse_part(chunk: _Chunk, part_index: int, part_count: int, budget: _Budget) -> _Part:
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
    if bones:
        raise CmshProfileError("unsupported bones/reference graph", cmsp.offset, "CMSP numBones")
    if child_count > 256 or aframes > 2 or not 1 <= vframes <= 512 or not 1 <= hframes <= 256:
        raise CmshProfileError("limit exceeded", cmsp.offset, "CMSP frame/hierarchy counts")

    tags: list[str] = []
    vertices: tuple[tuple[float, float, float], ...] = ()
    groups: tuple[tuple[int, ...], ...] = ()
    children: tuple[int, ...] = ()
    parent: int | None = None
    reference: int | None = None
    while reader.pos < len(reader.data):
        record = reader.chunk("MESP record")
        try:
            tag = record.tag.decode("ascii")
        except UnicodeDecodeError as error:
            raise CmshProfileError("unexpected tag/order", record.offset, "non-ASCII MESP tag") from error
        tags.append(tag)
        if record.tag in {b"BONE", b"BONW", b"BONS"}:
            raise CmshProfileError("unsupported bones/reference graph", record.offset, tag)
        if record.tag == b"CHLD":
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
            nested.expected(b"BBOX", "inner BBOX", length=40)
            nested.require_end()
            if len(record.payload) != 48:
                raise CmshProfileError("invalid declared length/count", record.offset, "outer BBOX")
        elif record.tag == b"VHFM":
            if len(record.payload) != vframes:
                raise CmshProfileError("invalid declared length/count", record.offset, "VHFM")
        elif record.tag == b"HORI":
            if len(record.payload) != hframes * 48:
                raise CmshProfileError("invalid declared length/count", record.offset, "HORI")
        elif record.tag == b"HPOS":
            if len(record.payload) != hframes * 16:
                raise CmshProfileError("invalid declared length/count", record.offset, "HPOS")
        elif record.tag == b"HFOV":
            if len(record.payload) != hframes * 4:
                raise CmshProfileError("invalid declared length/count", record.offset, "HFOV")
        elif record.tag in {b"PBKT", b"CPOS", b"CORI"}:
            if len(record.payload) > MAX_OPAQUE:
                raise CmshProfileError("limit exceeded", record.offset, tag)
        elif record.tag == b"PMVB":
            if reference is None:
                vertices, groups = _parse_pm_vb(record.payload, record.offset + 8, budget)
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
    rows = ((base[0], base[1], base[2]), (base[4], base[5], base[6]), (base[8], base[9], base[10]))
    return _Part(_Transform(rows, position), vertices, groups, children, parent, reference)


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
        if target.reference is not None or not target.vertices or not target.groups:
            raise CmshProfileError("unsupported bones/reference graph", 0, "REFR direct geometry target")
        if part.vertices or part.groups:
            raise CmshProfileError("unsupported bones/reference graph", 0, "REFR ambiguous geometry source")
        resolved.append(_Part(part.transform, target.vertices, target.groups, part.children, part.parent, part.reference))

    expanded_vertices = expanded_indices = expanded_groups = expanded_triangles = 0
    for part in resolved:
        expanded_vertices = _checked_add(expanded_vertices, len(part.vertices), MAX_VERTICES, "expanded vertex count")
        expanded_groups = _checked_add(expanded_groups, len(part.groups), MAX_GROUPS, "expanded group count")
        for indices in part.groups:
            expanded_indices = _checked_add(expanded_indices, len(indices), MAX_INDICES, "expanded index count")
            surviving = sum(len({indices[k], indices[k + 1], indices[k + 2]}) == 3 for k in range(len(indices) - 2))
            expanded_triangles = _checked_add(expanded_triangles, surviving, MAX_TRIANGLES, "expanded triangle count")
    return tuple(resolved)


def parse_cmsh_stream(data: bytes) -> ParsedMesh:
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
    reader.expected(b"CMST", "CMST", length=texture_count * 36)
    for index in range(texture_count):
        msht = reader.expected(b"MSHT", f"MSHT {index}", length=156)
        nested = _Reader(msht.payload, origin=msht.offset + 8, limit_role="MSHT")
        nested.expected(b"TEXB", f"TEXB {index}", length=148)
        nested.require_end()
    part_chunks = [reader.expected(b"MESP", f"MESP {index}") for index in range(part_count)]
    budget = _Budget()
    parts = _resolve_references(tuple(_parse_part(chunk, index, part_count, budget) for index, chunk in enumerate(part_chunks)))
    reader.absolute_limit = None
    siblings: list[bytes] = []
    while reader.pos < len(reader.data):
        sibling = reader.chunk("post-body sibling")
        if len(sibling.payload) > MAX_OPAQUE:
            raise CmshProfileError("limit exceeded", sibling.offset, "post-body sibling")
        siblings.append(sibling.tag)
    if siblings and tuple(siblings) not in _SIBLING_ORDERS:
        raise CmshProfileError("unexpected tag/order", reader.origin, "post-body sibling order")
    return ParsedMesh(parts)


def _number(value: float) -> str:
    if value == 0.0:
        return "0"
    return repr(value)


def emit_obj(mesh: ParsedMesh) -> bytes:
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
        for x, y, z in part.vertices:
            tx = (((rows[0][0] * x) + (rows[0][1] * y)) + (rows[0][2] * z)) + bx
            ty = (((rows[1][0] * x) + (rows[1][1] * y)) + (rows[1][2] * z)) + by
            tz = (((rows[2][0] * x) + (rows[2][1] * y)) + (rows[2][2] * z)) + bz
            values = (tx, ty, -tz)
            if not all(math.isfinite(value) for value in values):
                raise CmshProfileError("non-finite numeric value", 0, "transformed position")
            if any(abs(value) > MAX_COORDINATE for value in values):
                raise CmshProfileError("limit exceeded", 0, "transformed position")
            append_line("v " + " ".join(_number(value) for value in values))
            emitted_vertices = _checked_add(emitted_vertices, 1, MAX_VERTICES, "OBJ vertices")
    faces = 0
    for part, base in zip(mesh.parts, bases, strict=True):
        if base is None:
            continue
        for indices in part.groups:
            for ordinal in range(len(indices) - 2):
                if ordinal % 2 == 0:
                    a, b, c = indices[ordinal : ordinal + 3]
                else:
                    b, a, c = indices[ordinal : ordinal + 3]
                if len({a, b, c}) < 3:
                    continue
                a, b, c = a + base, c + base, b + base
                if not (1 <= a <= emitted_vertices and 1 <= b <= emitted_vertices and 1 <= c <= emitted_vertices):
                    raise CmshProfileError("OBJ rejection", 0, "face index")
                append_line(f"f {a} {b} {c}")
                faces = _checked_add(faces, 1, MAX_TRIANGLES, "OBJ faces")
    if emitted_vertices == 0 or faces == 0:
        raise CmshProfileError("OBJ rejection", 0, "empty geometry")
    result = ("\n".join(lines) + "\n").encode("utf-8")
    if len(result) != encoded_bytes:
        raise CmshProfileError("OBJ rejection", 0, "OBJ byte accounting")
    return result


def convert_aya_bytes(source: bytes) -> bytes:
    return emit_obj(parse_cmsh_stream(inflate_aya(source)))


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


def publish_anonymous_previews(checkout: Path, input_directory: Path, output_directory: Path) -> tuple[int, int]:
    trusted_checkout = Path(__file__).resolve().parents[2]
    checkout = _absolute_lexical(checkout)
    input_directory = _absolute_lexical(input_directory)
    output_directory = _absolute_lexical(output_directory)
    if os.path.normcase(str(checkout)) != os.path.normcase(str(trusted_checkout)):
        raise CmshProfileError("invalid framing", 0, "trusted checkout")
    allowed_inputs = (checkout / "game", checkout / "local-lab" / "rebuild-godot" / "input")
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
                    obj = convert_aya_bytes(data)
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
    arguments = parser.parse_args(argv)
    try:
        matches, failures = publish_anonymous_previews(arguments.checkout, arguments.input, arguments.output)
    except (CmshProfileError, OSError) as error:
        print(f"preview failed: {error}", file=sys.stderr)
        return 2
    print(f"anonymous previews: {matches} matched, {failures} rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
