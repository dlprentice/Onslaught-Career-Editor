# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import zlib

import cmsh_static_preview as preview


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload


def _cmsp(*, part: int, children: int, base_position: tuple[float, float, float], rotated: bool) -> bytes:
    payload = bytearray(316)
    identity = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    orientation = (
        (0.0, 1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        if rotated
        else identity
    )
    struct.pack_into("<12f", payload, 0x00, *identity)
    struct.pack_into("<12f", payload, 0x30, *orientation)
    struct.pack_into("<4f", payload, 0x60, 0.0, 0.0, 0.0, 1.0)
    struct.pack_into("<4f", payload, 0x70, *base_position, 1.0)
    struct.pack_into("<III", payload, 0x88, part, 1, children)
    struct.pack_into("<IIIIII", payload, 0xA8, 0, 0, 0, 0, 1, 1)
    struct.pack_into("<I", payload, 0xC0, 0)
    return _chunk(b"CMSP", bytes(payload))


def _bbox() -> bytes:
    return _chunk(b"BBOX", _chunk(b"BBOX", bytes(range(40))))


def _cmvb(group_count: int) -> bytes:
    payload = bytearray(296)
    payload[264] = group_count
    struct.pack_into("<III", payload, 276, 36, 0x152, 4)
    return _chunk(b"CMVB", bytes(payload))


def _vertices() -> bytes:
    rows = [
        (1.0, 2.0, 3.0),
        (4.0, 5.0, 6.0),
        (7.0, 8.0, 9.0),
        (2.0, 2.0, 3.0),
    ]
    return b"".join(struct.pack("<6fI2f", *position, 0.0, 1.0, 0.0, 0xFFFFFFFF, 0.0, 0.0) for position in rows)


def _group(indices: tuple[int, ...], *, owns_vertices: bool) -> bytes:
    vertex_payload = _vertices() if owns_vertices else b""
    declared_vertex_bytes = 4 * 36
    index_payload = struct.pack(f"<{len(indices)}H", *indices)
    mmpt = struct.pack("<6I", declared_vertex_bytes, len(index_payload), len(indices), 4, len(indices) - 2, 1)
    return (
        _chunk(b"MMPT", mmpt)
        + _chunk(b"IBUF", index_payload)
        + _chunk(b"VBUF", vertex_payload)
        + _chunk(b"TEXR", bytes(24))
    )


def _pmvb(*, populated: bool) -> bytes:
    if not populated:
        return _chunk(b"PMVB", _cmvb(0))
    return _chunk(b"PMVB", _cmvb(2) + _group((0, 1, 2, 2, 3), owns_vertices=True) + _group((0, 2, 3), owns_vertices=False))


def _reference_group(indices: tuple[int, ...], *, owns_vertices: bool) -> bytes:
    rows = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0))
    vertex_payload = (
        b"".join(struct.pack("<6fI2f", *position, 0.0, 1.0, 0.0, 0xFFFFFFFF, 0.0, 0.0) for position in rows)
        if owns_vertices
        else b""
    )
    index_payload = struct.pack(f"<{len(indices)}H", *indices)
    mmpt = struct.pack("<6I", 3 * 36, len(index_payload), len(indices), 3, len(indices) - 2, 1)
    return (
        _chunk(b"MMPT", mmpt)
        + _chunk(b"IBUF", index_payload)
        + _chunk(b"VBUF", vertex_payload)
        + _chunk(b"TEXR", bytes(24))
    )


def _reference_geometry() -> bytes:
    return _chunk(
        b"PMVB",
        _cmvb(2)
        + _reference_group((0, 1, 2), owns_vertices=True)
        + _reference_group((0, 2, 1), owns_vertices=False),
    )


def _multipart_part(
    part: int,
    *,
    parent: int | None,
    children: tuple[int, ...] = (),
    base_position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotated: bool = False,
    geometry: bytes | None = None,
    reference_payload: bytes | None = None,
    before_reference: bytes = b"",
    after_reference: bytes = b"",
) -> bytes:
    records = b""
    if children:
        records += _chunk(b"CHLD", struct.pack(f"<{len(children)}I", *children))
    if parent is not None:
        records += _chunk(b"PRNT", struct.pack("<I", parent))
    records += _bbox() + _chunk(b"VHFM", b"\x01") + _chunk(b"HORI", bytes(48)) + _chunk(b"HPOS", bytes(16))
    records += _chunk(b"CPOS", b"") + _chunk(b"CORI", b"") + before_reference
    if reference_payload is not None:
        records += _chunk(b"REFR", reference_payload)
    records += after_reference + (geometry if geometry is not None else _pmvb(populated=False))
    return _chunk(
        b"MESP",
        _cmsp(part=part, children=len(children), base_position=base_position, rotated=rotated) + records,
    )


def reference_fixture_parts() -> list[bytes]:
    return [
        _multipart_part(0, parent=None, children=(1, 2, 3), base_position=(100.0, 200.0, 300.0), rotated=True),
        _multipart_part(1, parent=0, base_position=(10.0, 20.0, 30.0), rotated=True, geometry=_reference_geometry()),
        _multipart_part(2, parent=0, base_position=(40.0, 50.0, 60.0), reference_payload=struct.pack("<I", 1)),
        _multipart_part(3, parent=0, children=(4,), base_position=(-10.0, -20.0, -30.0), rotated=True, reference_payload=struct.pack("<I", 1)),
        _multipart_part(4, parent=3),
    ]


def build_reference_fixture_stream(parts: list[bytes] | None = None) -> bytes:
    selected = reference_fixture_parts() if parts is None else parts
    header = bytearray(380)
    header[0:4] = b"CMSH"
    struct.pack_into("<I", header, 4, 372)
    struct.pack_into("<I", header, 0x164, len(selected))
    return bytes(header) + _chunk(b"CMST", b"") + b"".join(selected)


def _part(*, parent: bool) -> bytes:
    if parent:
        records = (
            _chunk(b"CHLD", struct.pack("<I", 1))
            + _chunk(b"PRNT", struct.pack("<I", 0))
            + _bbox()
            + _chunk(b"VHFM", b"\x01")
            + _chunk(b"HORI", bytes(48))
            + _chunk(b"HPOS", bytes(16))
            + _chunk(b"PBKT", b"opaque")
            + _chunk(b"CPOS", b"\x02\x03")
            + _chunk(b"CORI", b"\x04")
            + _pmvb(populated=False)
        )
        return _chunk(b"MESP", _cmsp(part=0, children=1, base_position=(0.0, 0.0, 0.0), rotated=False) + records)
    records = (
        _chunk(b"PRNT", struct.pack("<I", 0))
        + _bbox()
        + _chunk(b"VHFM", b"\x01")
        + _chunk(b"HORI", bytes(48))
        + _chunk(b"HPOS", bytes(16))
        + _chunk(b"CPOS", b"")
        + _chunk(b"CORI", b"")
        + _pmvb(populated=True)
    )
    return _chunk(b"MESP", _cmsp(part=1, children=0, base_position=(10.0, 20.0, 30.0), rotated=True) + records)


def build_fixture_stream() -> bytes:
    header = bytearray(380)
    header[0:4] = b"CMSH"
    struct.pack_into("<I", header, 4, 372)
    struct.pack_into("<I", header, 0x0C, 1)
    header[0x2C:0x34] = b"fixture\0"
    struct.pack_into("<I", header, 0x164, 2)
    texture = _chunk(b"CMST", bytes(36)) + _chunk(b"MSHT", _chunk(b"TEXB", bytes(148)))
    return bytes(header) + texture + _part(parent=True) + _part(parent=False) + _chunk(b"BBOX", b"post")


def build_fixture_aya() -> bytes:
    stream = build_fixture_stream()
    split = len(stream) // 2
    members = [zlib.compress(stream[:split]), zlib.compress(stream[split:])]
    return b"".join(struct.pack("<I", len(member)) + member for member in members)


ACCEPTED_PART_ORDERS = tuple(
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
    )
)
ACCEPTED_SIBLING_ORDERS = (
    (),
    ("BBOX",),
    ("BBOX", "CEMT"),
    ("CAMD", "BBOX"),
    ("CAMD", "BBOX", "CEMT"),
    ("BBOX", "PMS2"),
    ("CAMD", "BBOX", "CEMT", "PMS2"),
)


def _record(tag: str) -> bytes:
    return {
        "CHLD": _chunk(b"CHLD", struct.pack("<I", 0)),
        "PRNT": _chunk(b"PRNT", struct.pack("<I", 0)),
        "NMIC": _chunk(b"NMIC", struct.pack("<I", 0)),
        "BBOX": _bbox(),
        "VHFM": _chunk(b"VHFM", b"\x01"),
        "HORI": _chunk(b"HORI", bytes(48)),
        "HPOS": _chunk(b"HPOS", bytes(16)),
        "HFOV": _chunk(b"HFOV", bytes(4)),
        "PBKT": _chunk(b"PBKT", b"opaque"),
        "CPOS": _chunk(b"CPOS", b"position"),
        "CORI": _chunk(b"CORI", b"orientation"),
        "PMVB": _pmvb(populated=True),
        "ZZZZ": _chunk(b"ZZZZ", b""),
        "REFR": _chunk(b"REFR", b""),
    }[tag]


def build_order_stream(order: tuple[str, ...], siblings: tuple[str, ...] = (), overrides: dict[str, bytes] | None = None) -> bytes:
    header = bytearray(380)
    header[0:4] = b"CMSH"
    struct.pack_into("<I", header, 4, 372)
    struct.pack_into("<I", header, 0x0C, 0)
    struct.pack_into("<I", header, 0x164, 1)
    children = 1 if "CHLD" in order else 0
    part = _chunk(
        b"MESP",
        _cmsp(part=0, children=children, base_position=(0.0, 0.0, 0.0), rotated=False)
        + b"".join((overrides or {}).get(tag, _record(tag)) for tag in order),
    )
    return bytes(header) + _chunk(b"CMST", b"") + part + b"".join(_chunk(tag.encode("ascii"), b"x") for tag in siblings)


EXPECTED_OBJ = b"""v 12.0 19.0 -33.0
v 15.0 16.0 -36.0
v 18.0 13.0 -39.0
v 12.0 18.0 -33.0
f 1 3 2
f 1 4 3
"""
EXPECTED_SHA256 = "3bee52cf5bf193beb090e8065c7eb057490730cd87977a268507f1091870c848"

EXPECTED_REFERENCE_OBJ = b"""v 12.0 19.0 -33.0
v 15.0 16.0 -36.0
v 18.0 13.0 -39.0
v 41.0 52.0 -63.0
v 44.0 55.0 -66.0
v 47.0 58.0 -69.0
v -8.0 -21.0 27.0
v -5.0 -24.0 24.0
v -2.0 -27.0 21.0
f 1 3 2
f 1 2 3
f 4 6 5
f 4 5 6
f 7 9 8
f 7 8 9
"""
EXPECTED_REFERENCE_SHA256 = "ddf266ab5650cc4dc234e23595dac092f873a9b9222b91efff3f17dd6917b93e"


def _validate_obj_semantics(value: bytes) -> None:
    text = value.decode("utf-8")
    assert text.endswith("\n") and "\r" not in text
    lines = text.splitlines()
    vertices = [line for line in lines if line.startswith("v ")]
    faces = [line for line in lines if line.startswith("f ")]
    assert len(vertices) == 4 and len(faces) == 2
    assert all(len(line.split()) == 4 for line in lines)
    assert all(1 <= int(token) <= len(vertices) for line in faces for token in line.split()[1:])


class CmshStaticPreviewTests(unittest.TestCase):
    def test_generated_archive_emits_exact_geometry_only_obj(self) -> None:
        result = preview.convert_aya_bytes(build_fixture_aya())
        self.assertEqual(EXPECTED_OBJ, result)
        self.assertEqual(EXPECTED_SHA256, hashlib.sha256(result).hexdigest())
        _validate_obj_semantics(result)

    def test_reference_fixture_emits_owner_and_instances_in_part_sequence_order(self) -> None:
        result = preview.emit_obj(preview.parse_cmsh_stream(build_reference_fixture_stream()))
        self.assertEqual(EXPECTED_REFERENCE_OBJ, result)
        self.assertEqual(EXPECTED_REFERENCE_SHA256, hashlib.sha256(result).hexdigest())
        self.assertEqual(9, sum(line.startswith(b"v ") for line in result.splitlines()))
        self.assertEqual(6, sum(line.startswith(b"f ") for line in result.splitlines()))

    def test_reference_length_target_and_geometry_source_fail_closed(self) -> None:
        for length in (0, 3, 8):
            parts = reference_fixture_parts()
            parts[2] = _multipart_part(2, parent=0, reference_payload=bytes(length))
            with self.subTest(case="length", length=length):
                with self.assertRaisesRegex(preview.CmshProfileError, "invalid declared length/count"):
                    preview.parse_cmsh_stream(build_reference_fixture_stream(parts))

        target_cases = {
            "self": 2,
            "forward_last_index": 4,
            "out_of_range": 5,
            "empty_target": 0,
        }
        for case, target in target_cases.items():
            parts = reference_fixture_parts()
            parts[2] = _multipart_part(2, parent=0, reference_payload=struct.pack("<I", target))
            pattern = "index out of bounds" if case == "out_of_range" else "unsupported bones/reference graph"
            with self.subTest(case=case):
                with self.assertRaisesRegex(preview.CmshProfileError, pattern):
                    preview.parse_cmsh_stream(build_reference_fixture_stream(parts))

        for case, geometry in (
            ("populated", _reference_geometry()),
            ("residual", _chunk(b"PMVB", _cmvb(0) + b"x")),
        ):
            parts = reference_fixture_parts()
            parts[2] = _multipart_part(2, parent=0, geometry=geometry, reference_payload=struct.pack("<I", 1))
            with self.subTest(case=case):
                with self.assertRaisesRegex(preview.CmshProfileError, "unsupported bones/reference graph"):
                    preview.parse_cmsh_stream(build_reference_fixture_stream(parts))

    def test_reference_chains_cycles_order_and_hierarchy_fail_closed(self) -> None:
        chain = [
            _multipart_part(0, parent=None, children=(1, 2), geometry=_reference_geometry()),
            _multipart_part(1, parent=0, reference_payload=struct.pack("<I", 0)),
            _multipart_part(2, parent=0, reference_payload=struct.pack("<I", 1)),
        ]
        cycle = [
            _multipart_part(0, parent=None, children=(1, 2)),
            _multipart_part(1, parent=0, reference_payload=struct.pack("<I", 2)),
            _multipart_part(2, parent=0, reference_payload=struct.pack("<I", 1)),
        ]
        for case, parts in (("chain", chain), ("cycle", cycle)):
            with self.subTest(case=case):
                with self.assertRaisesRegex(preview.CmshProfileError, "unsupported bones/reference graph"):
                    preview.parse_cmsh_stream(build_reference_fixture_stream(parts))

        duplicate = reference_fixture_parts()
        duplicate[2] = _multipart_part(
            2,
            parent=0,
            reference_payload=struct.pack("<I", 1),
            before_reference=_chunk(b"REFR", struct.pack("<I", 1)),
        )
        wrong_order = reference_fixture_parts()
        wrong_order[2] = _multipart_part(
            2,
            parent=0,
            reference_payload=struct.pack("<I", 1),
            after_reference=_chunk(b"CPOS", b""),
        )
        for case, parts in (("duplicate", duplicate), ("wrong_order", wrong_order)):
            with self.subTest(case=case):
                with self.assertRaisesRegex(preview.CmshProfileError, "unexpected tag/order"):
                    preview.parse_cmsh_stream(build_reference_fixture_stream(parts))

        missing_reciprocal = reference_fixture_parts()
        missing_reciprocal[0] = _multipart_part(0, parent=None, children=(1, 3), base_position=(100.0, 200.0, 300.0), rotated=True)
        duplicate_parent = reference_fixture_parts()
        duplicate_parent[3] = _multipart_part(3, parent=0, children=(2, 4), reference_payload=struct.pack("<I", 1))
        parent_cycle = reference_fixture_parts()
        parent_cycle[0] = _multipart_part(0, parent=3, children=(1, 2, 3))
        parent_cycle[3] = _multipart_part(3, parent=0, children=(0, 4), reference_payload=struct.pack("<I", 1))
        for case, parts in (
            ("missing_reciprocal", missing_reciprocal),
            ("duplicate_parent", duplicate_parent),
            ("parent_cycle", parent_cycle),
        ):
            with self.subTest(case=case):
                with self.assertRaisesRegex(preview.CmshProfileError, "unsupported bones/reference graph"):
                    preview.parse_cmsh_stream(build_reference_fixture_stream(parts))

    def test_reference_expansion_caps_count_every_instance(self) -> None:
        stream = build_reference_fixture_stream()
        for cap_name, at_cap, above_cap in (
            ("MAX_VERTICES", 9, 8),
            ("MAX_GROUPS", 6, 5),
            ("MAX_INDICES", 18, 17),
            ("MAX_TRIANGLES", 6, 5),
        ):
            with self.subTest(cap=cap_name, boundary="cap"):
                with mock.patch.object(preview, cap_name, at_cap):
                    self.assertEqual(EXPECTED_REFERENCE_OBJ, preview.emit_obj(preview.parse_cmsh_stream(stream)))
            with self.subTest(cap=cap_name, boundary="cap_plus_one"):
                with mock.patch.object(preview, cap_name, above_cap):
                    with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
                        preview.emit_obj(preview.parse_cmsh_stream(stream))

        with mock.patch.object(preview, "MAX_OBJ", len(EXPECTED_REFERENCE_OBJ)):
            self.assertEqual(EXPECTED_REFERENCE_OBJ, preview.emit_obj(preview.parse_cmsh_stream(stream)))
        with mock.patch.object(preview, "MAX_OBJ", len(EXPECTED_REFERENCE_OBJ) - 1):
            with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
                preview.emit_obj(preview.parse_cmsh_stream(stream))

    def test_reference_profile_does_not_admit_bones_or_stride48(self) -> None:
        bone_parts = reference_fixture_parts()
        bone_parts[2] = _multipart_part(
            2,
            parent=0,
            reference_payload=struct.pack("<I", 1),
            after_reference=_chunk(b"BONE", b""),
        )
        with self.assertRaisesRegex(preview.CmshProfileError, "unsupported bones/reference graph"):
            preview.parse_cmsh_stream(build_reference_fixture_stream(bone_parts))

        stride48 = bytearray(_reference_geometry())
        cmvb = stride48.find(b"CMVB")
        struct.pack_into("<I", stride48, cmvb + 8 + 276, 48)
        stride_parts = reference_fixture_parts()
        stride_parts[1] = _multipart_part(1, parent=0, geometry=bytes(stride48))
        with self.assertRaisesRegex(preview.CmshProfileError, "unsupported profile"):
            preview.parse_cmsh_stream(build_reference_fixture_stream(stride_parts))

        empty_stride48 = bytearray(_pmvb(populated=False))
        empty_cmvb = empty_stride48.find(b"CMVB")
        struct.pack_into("<I", empty_stride48, empty_cmvb + 8 + 276, 48)
        source_stride_parts = reference_fixture_parts()
        source_stride_parts[2] = _multipart_part(
            2,
            parent=0,
            geometry=bytes(empty_stride48),
            reference_payload=struct.pack("<I", 1),
        )
        with self.assertRaisesRegex(preview.CmshProfileError, "unsupported bones/reference graph"):
            preview.parse_cmsh_stream(build_reference_fixture_stream(source_stride_parts))

    def test_parser_rejects_every_truncation_without_partial_output(self) -> None:
        stream = build_fixture_stream()
        valid_body_boundary = stream.rfind(b"BBOX")
        for length in range(len(stream)):
            if length == valid_body_boundary:
                continue
            with self.subTest(length=length):
                with self.assertRaises(preview.CmshProfileError):
                    preview.parse_cmsh_stream(stream[:length])

    def test_archive_rejects_trailing_or_incomplete_members(self) -> None:
        valid = build_fixture_aya()
        for malformed in (valid + b"x", valid[:-1], struct.pack("<I", 999) + b"short"):
            with self.assertRaises(preview.CmshProfileError):
                preview.inflate_aya(malformed)

    def test_rejects_unsupported_topology_and_secondary_vertex_payload(self) -> None:
        stream = bytearray(build_fixture_stream())
        cmvb = stream.rfind(b"CMVB")
        struct.pack_into("<I", stream, cmvb + 8 + 284, 5)
        with self.assertRaisesRegex(preview.CmshProfileError, "unsupported topology"):
            preview.parse_cmsh_stream(bytes(stream))

        stream = bytearray(build_fixture_stream())
        second_vbuf = stream.rfind(b"VBUF")
        struct.pack_into("<I", stream, second_vbuf + 4, 1)
        stream.insert(second_vbuf + 8, 0)
        mesp = stream.rfind(b"MESP", 0, second_vbuf)
        struct.pack_into("<I", stream, mesp + 4, struct.unpack_from("<I", stream, mesp + 4)[0] + 1)
        with self.assertRaises(preview.CmshProfileError):
            preview.parse_cmsh_stream(bytes(stream))

    def test_error_text_is_path_free_and_categorized(self) -> None:
        with self.assertRaises(preview.CmshProfileError) as caught:
            preview.parse_cmsh_stream(b"NOPE")
        message = str(caught.exception)
        self.assertIn("truncation", message)
        self.assertNotIn("\\", message)
        self.assertNotIn(":/", message)

    def test_all_exact_part_and_sibling_orders_are_accepted(self) -> None:
        for order in ACCEPTED_PART_ORDERS:
            with self.subTest(order=order):
                _validate_obj_semantics(preview.emit_obj(preview.parse_cmsh_stream(build_order_stream(order))))
        for siblings in ACCEPTED_SIBLING_ORDERS:
            with self.subTest(siblings=siblings):
                preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], siblings))

    def test_part_grammar_rejects_deletion_duplication_swap_insertion_and_reference(self) -> None:
        for order in ACCEPTED_PART_ORDERS:
            mutations = []
            mutations.extend(order[:index] + order[index + 1 :] for index in range(len(order)))
            mutations.extend(order[:index] + (order[index],) + order[index:] for index in range(len(order)))
            mutations.extend(order[:index] + (order[index + 1], order[index]) + order[index + 2 :] for index in range(len(order) - 1))
            mutations.extend(order[:index] + ("ZZZZ",) + order[index:] for index in range(len(order) + 1))
            for mutation in mutations:
                if mutation in ACCEPTED_PART_ORDERS:
                    continue
                with self.subTest(order=order, mutation=mutation):
                    with self.assertRaises(preview.CmshProfileError):
                        preview.parse_cmsh_stream(build_order_stream(mutation))
        with self.assertRaisesRegex(preview.CmshProfileError, "invalid declared length/count"):
            preview.parse_cmsh_stream(build_order_stream(("REFR",) + ACCEPTED_PART_ORDERS[0]))

    def test_numeric_index_and_primitive_mutations_fail_closed(self) -> None:
        mutations: list[tuple[str, int, bytes]] = []
        original = build_order_stream(ACCEPTED_PART_ORDERS[0])
        vbuf = original.find(b"VBUF")
        ibuf = original.find(b"IBUF")
        mmpt = original.find(b"MMPT")
        mutations.append(("non-finite", vbuf + 8, struct.pack("<f", float("nan"))))
        mutations.append(("index", ibuf + 8, struct.pack("<H", 99)))
        mutations.append(("primitive", mmpt + 8 + 16, struct.pack("<I", 99)))
        for name, offset, replacement in mutations:
            stream = bytearray(original)
            stream[offset : offset + len(replacement)] = replacement
            with self.subTest(name=name):
                with self.assertRaises(preview.CmshProfileError):
                    preview.parse_cmsh_stream(bytes(stream))

    def test_guarded_local_publication_uses_only_anonymous_obj_names(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        input_parent = checkout / "local-lab" / "rebuild-godot" / "input"
        output_parent = checkout / "local-lab" / "rebuild-godot" / "generated"
        input_parent.mkdir(parents=True, exist_ok=True)
        output_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=input_parent) as input_temp, tempfile.TemporaryDirectory(dir=output_parent) as output_temp:
            input_root = Path(input_temp)
            output_root = Path(output_temp) / "new" / "session"
            (input_root / "private-source-name.aya").write_bytes(build_fixture_aya())

            matches, failures = preview.publish_anonymous_previews(checkout, input_root, output_root)

            self.assertEqual((1, 0), (matches, failures))
            self.assertEqual(["candidate-0001.obj", "summary.json"], sorted(path.name for path in output_root.iterdir()))
            self.assertEqual(EXPECTED_OBJ, (output_root / "candidate-0001.obj").read_bytes())
            self.assertNotIn("private-source-name", " ".join(path.name for path in output_root.iterdir()))
            self.assertEqual(
                {
                    "schemaVersion": "onslaught-cmsh-static-preview-summary.v0",
                    "matched": 1,
                    "rejected": 0,
                    "categories": {},
                },
                json.loads((output_root / "summary.json").read_text(encoding="utf-8")),
            )
            with self.assertRaises(preview.CmshProfileError):
                preview.publish_anonymous_previews(checkout, input_root, checkout / "outside")
            with self.assertRaisesRegex(preview.CmshProfileError, "output session must be empty"):
                preview.publish_anonymous_previews(checkout, input_root, output_root)

    def test_local_publication_records_only_aggregate_path_free_rejections(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        input_parent = checkout / "local-lab" / "rebuild-godot" / "input"
        output_parent = checkout / "local-lab" / "rebuild-godot" / "generated"
        input_parent.mkdir(parents=True, exist_ok=True)
        output_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=input_parent) as input_temp, tempfile.TemporaryDirectory(dir=output_parent) as output_temp:
            input_root = Path(input_temp)
            output_root = Path(output_temp)
            (input_root / "sensitive-name.aya").write_bytes(b"bad")

            self.assertEqual((0, 1), preview.publish_anonymous_previews(checkout, input_root, output_root))
            summary = (output_root / "summary.json").read_text(encoding="utf-8")
            self.assertNotIn("sensitive-name", summary)
            self.assertEqual({"truncation": 1}, json.loads(summary)["categories"])

    def test_local_preflight_is_path_free_and_checkout_cannot_be_relabelled(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        private_missing = checkout / "local-lab" / "rebuild-godot" / "input" / "private-missing"
        output = checkout / "local-lab" / "rebuild-godot" / "generated" / "unused"
        with self.assertRaises(preview.CmshProfileError) as caught:
            preview.publish_anonymous_previews(checkout, private_missing, output)
        self.assertNotIn("private-missing", str(caught.exception))
        with tempfile.TemporaryDirectory() as external:
            fake = Path(external)
            (fake / "game").mkdir()
            with self.assertRaises(preview.CmshProfileError):
                preview.publish_anonymous_previews(fake, fake / "game", fake / "local-lab" / "rebuild-godot" / "generated")

    def test_vec4_w_components_are_opaque_not_finite_numeric_fields(self) -> None:
        original = build_order_stream(ACCEPTED_PART_ORDERS[0])
        cmsp = original.find(b"CMSP")
        for payload_offset in (0x0C, 0x1C, 0x2C, 0x3C, 0x4C, 0x5C, 0x6C, 0x7C):
            stream = bytearray(original)
            struct.pack_into("<f", stream, cmsp + 8 + payload_offset, float("nan"))
            with self.subTest(payload_offset=payload_offset):
                preview.parse_cmsh_stream(bytes(stream))

    def test_profile_rejects_missing_malformed_families(self) -> None:
        original = build_order_stream(ACCEPTED_PART_ORDERS[0])
        cmvb = original.find(b"CMVB")
        cmsp = original.find(b"CMSP")
        vbuf = original.find(b"VBUF")
        cases = (
            ("stride", cmvb + 8 + 276, struct.pack("<I", 48), "unsupported profile"),
            ("FVF", cmvb + 8 + 280, struct.pack("<I", 0), "unsupported profile"),
            ("bones", cmsp + 8 + 0xC0, struct.pack("<I", 1), "unsupported bones/reference graph"),
            ("UV infinity", vbuf + 8 + 28, struct.pack("<f", float("inf")), "non-finite numeric value"),
        )
        for name, offset, value, category in cases:
            stream = bytearray(original)
            stream[offset : offset + len(value)] = value
            with self.subTest(name=name):
                with self.assertRaisesRegex(preview.CmshProfileError, category):
                    preview.parse_cmsh_stream(bytes(stream))

        short_pm_vb = _chunk(b"PMVB", _cmvb(1) + _group((0, 1), owns_vertices=True))
        with self.assertRaises(preview.CmshProfileError):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"PMVB": short_pm_vb}))
        trailing_empty = _chunk(b"PMVB", _cmvb(0) + b"x")
        with self.assertRaises(preview.CmshProfileError):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"PMVB": trailing_empty}))
        for siblings in (("CEMT",), ("BBOX", "BBOX"), ("CAMD", "CEMT", "BBOX")):
            with self.subTest(siblings=siblings):
                with self.assertRaises(preview.CmshProfileError):
                    preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], siblings))

    def test_opaque_cap_and_empty_or_out_of_bounds_obj_policy(self) -> None:
        at_cap = _chunk(b"PBKT", bytes(16 * 1024 * 1024))
        preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[2], overrides={"PBKT": at_cap}))
        above_cap = _chunk(b"PBKT", bytes(16 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[2], overrides={"PBKT": above_cap}))

        empty_pm_vb = _chunk(b"PMVB", _cmvb(0))
        empty_mesh = preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"PMVB": empty_pm_vb}))
        with self.assertRaisesRegex(preview.CmshProfileError, "OBJ rejection"):
            preview.emit_obj(empty_mesh)

        stream = bytearray(build_order_stream(ACCEPTED_PART_ORDERS[0]))
        cmsp = stream.find(b"CMSP")
        struct.pack_into("<f", stream, cmsp + 8 + 0x70, 1_000_001.0)
        with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
            preview.emit_obj(preview.parse_cmsh_stream(bytes(stream)))

    def test_header_count_caps_fail_before_dependent_records(self) -> None:
        for offset in (0x0C, 0x164):
            stream = bytearray(build_order_stream(ACCEPTED_PART_ORDERS[0]))
            struct.pack_into("<I", stream, offset, 257)
            with self.subTest(offset=offset):
                with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
                    preview.parse_cmsh_stream(bytes(stream))

    def test_single_owned_group_and_remaining_container_failures(self) -> None:
        single = _chunk(b"PMVB", _cmvb(1) + _group((0, 1, 2), owns_vertices=True))
        obj = preview.emit_obj(preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"PMVB": single})))
        self.assertEqual(1, sum(line.startswith(b"f ") for line in obj.splitlines()))

        populated = _pmvb(populated=True)
        residual = _chunk(b"PMVB", populated[8:] + b"x")
        with self.assertRaises(preview.CmshProfileError):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"PMVB": residual}))

        reuse = bytearray(populated)
        second_mmpt = reuse.find(b"MMPT", reuse.find(b"MMPT") + 1)
        struct.pack_into("<I", reuse, second_mmpt + 8 + 12, 3)
        with self.assertRaises(preview.CmshProfileError):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"PMVB": bytes(reuse)}))

        bad_frame = _chunk(b"VHFM", b"")
        with self.assertRaises(preview.CmshProfileError):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], overrides={"VHFM": bad_frame}))
        bad_child = _chunk(b"CHLD", struct.pack("<I", 1))
        with self.assertRaisesRegex(preview.CmshProfileError, "index out of bounds"):
            preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[1], overrides={"CHLD": bad_child}))

    def test_every_short_sibling_transition_is_exactly_allowlisted(self) -> None:
        allowed = set(ACCEPTED_SIBLING_ORDERS)
        tags = ("CAMD", "BBOX", "CEMT", "PMS2")
        for length in range(1, 5):
            for siblings in itertools.product(tags, repeat=length):
                if siblings in allowed:
                    preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], siblings))
                else:
                    with self.assertRaises(preview.CmshProfileError):
                        preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0], siblings))

    def test_archive_and_body_caps_reject_before_profile_allocation(self) -> None:
        with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
            preview.inflate_aya(bytes(64 * 1024 * 1024 + 1))

        huge = zlib.compress(bytes(128 * 1024 * 1024 + 1), level=1)
        with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
            preview.inflate_aya(struct.pack("<I", len(huge)) + huge)

        header = bytearray(380)
        header[0:4] = b"CMSH"
        struct.pack_into("<I", header, 4, 372)
        struct.pack_into("<I", header, 0x164, 1)
        oversized_part = b"MESP" + struct.pack("<I", 32 * 1024 * 1024) + bytes(32 * 1024 * 1024)
        with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
            preview.parse_cmsh_stream(bytes(header) + _chunk(b"CMST", b"") + oversized_part)

    def test_candidate_count_and_aggregate_source_caps_are_preflight_only(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        input_parent = checkout / "local-lab" / "rebuild-godot" / "input"
        output_parent = checkout / "local-lab" / "rebuild-godot" / "generated"
        input_parent.mkdir(parents=True, exist_ok=True)
        output_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=input_parent) as input_temp, tempfile.TemporaryDirectory(dir=output_parent) as output_temp:
            for index in range(257):
                (Path(input_temp) / f"{index:04d}.aya").write_bytes(b"")
            with self.assertRaisesRegex(preview.CmshProfileError, "candidate count"):
                preview.publish_anonymous_previews(checkout, Path(input_temp), Path(output_temp))
        with tempfile.TemporaryDirectory(dir=input_parent) as input_temp, tempfile.TemporaryDirectory(dir=output_parent) as output_temp:
            for index in range(5):
                with (Path(input_temp) / f"{index:04d}.aya").open("wb") as stream:
                    stream.truncate(55 * 1024 * 1024)
            with self.assertRaisesRegex(preview.CmshProfileError, "aggregate candidate"):
                preview.publish_anonymous_previews(checkout, Path(input_temp), Path(output_temp))

    def test_late_candidate_change_rolls_back_prior_atomic_obj(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        input_parent = checkout / "local-lab" / "rebuild-godot" / "input"
        output_parent = checkout / "local-lab" / "rebuild-godot" / "generated"
        input_parent.mkdir(parents=True, exist_ok=True)
        output_parent.mkdir(parents=True, exist_ok=True)
        fixture = build_fixture_aya()
        with tempfile.TemporaryDirectory(dir=input_parent) as input_temp, tempfile.TemporaryDirectory(dir=output_parent) as output_temp:
            input_root, output_root = Path(input_temp), Path(output_temp)
            (input_root / "a.aya").write_bytes(fixture)
            (input_root / "b.aya").write_bytes(fixture)
            original_read = Path.read_bytes

            def changed_second(path: Path) -> bytes:
                return b"" if path.name == "b.aya" else original_read(path)

            with mock.patch.object(Path, "read_bytes", changed_second):
                with self.assertRaisesRegex(preview.CmshProfileError, "candidate changed"):
                    preview.publish_anonymous_previews(checkout, input_root, output_root)
            self.assertEqual([], list(output_root.iterdir()))

    def test_held_metadata_change_rejects_and_rolls_back_prior_obj(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        input_parent = checkout / "local-lab" / "rebuild-godot" / "input"
        output_parent = checkout / "local-lab" / "rebuild-godot" / "generated"
        input_parent.mkdir(parents=True, exist_ok=True)
        output_parent.mkdir(parents=True, exist_ok=True)
        fixture = build_fixture_aya()
        with tempfile.TemporaryDirectory(dir=input_parent) as input_temp, tempfile.TemporaryDirectory(dir=output_parent) as output_temp:
            input_root, output_root = Path(input_temp), Path(output_temp)
            (input_root / "a.aya").write_bytes(fixture)
            target = input_root / "b.aya"
            target.write_bytes(fixture)
            original_lstat = preview.os.lstat
            target_calls = 0

            def changed_link_count(path: object, *args: object, **kwargs: object) -> object:
                nonlocal target_calls
                result = original_lstat(path, *args, **kwargs)
                if Path(path) == target:
                    target_calls += 1
                    if target_calls >= 4:
                        return SimpleNamespace(
                            st_mode=result.st_mode,
                            st_nlink=2,
                            st_size=result.st_size,
                            st_file_attributes=getattr(result, "st_file_attributes", 0),
                        )
                return result

            with mock.patch.object(preview.os, "lstat", changed_link_count):
                with self.assertRaisesRegex(preview.CmshProfileError, "held candidate"):
                    preview.publish_anonymous_previews(checkout, input_root, output_root)
            self.assertEqual([], list(output_root.iterdir()))

    def test_aggregate_and_emitter_caps_have_exact_boundaries(self) -> None:
        pmvb_payload = memoryview((_chunk(b"PMVB", _cmvb(1) + _group((0, 1, 2), owns_vertices=True)))[8:])
        for budget in (
            preview._Budget(groups=1024),
            preview._Budget(vertices=99_999),
            preview._Budget(indices=599_999),
        ):
            with self.subTest(budget=budget):
                with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
                    preview._parse_pm_vb(pmvb_payload, 0, budget)

        mesh = preview.parse_cmsh_stream(build_order_stream(ACCEPTED_PART_ORDERS[0]))
        identity_obj = preview.emit_obj(mesh)
        with mock.patch.object(preview, "MAX_TRIANGLES", 2):
            self.assertEqual(identity_obj, preview.emit_obj(mesh))
        with mock.patch.object(preview, "MAX_TRIANGLES", 1):
            with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
                preview.emit_obj(mesh)
        with mock.patch.object(preview, "MAX_OBJ", len(identity_obj)):
            self.assertEqual(identity_obj, preview.emit_obj(mesh))
        with mock.patch.object(preview, "MAX_OBJ", len(identity_obj) - 1):
            with self.assertRaisesRegex(preview.CmshProfileError, "limit exceeded"):
                preview.emit_obj(mesh)

    def test_broken_reparse_dirent_is_not_treated_as_a_missing_output_component(self) -> None:
        checkout = Path(__file__).resolve().parents[2]
        root = checkout / "local-lab" / "rebuild-godot" / "generated"
        path = root / "broken" / "session"

        def lexical_exists(candidate: object) -> bool:
            return Path(candidate).name == "broken"

        def reparse(candidate: Path) -> bool:
            return candidate.name == "broken"

        with mock.patch.object(preview.os.path, "lexists", lexical_exists), mock.patch.object(preview, "_has_reparse_point", reparse):
            with self.assertRaisesRegex(preview.CmshProfileError, "reparse component"):
                preview._validate_no_reparse_descendant(path, root, checkout, must_exist=False)


if __name__ == "__main__":
    unittest.main()
