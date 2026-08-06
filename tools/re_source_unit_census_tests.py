#!/usr/bin/env python3
"""Focused synthetic and optional frozen-bundle tests for source-unit census."""

from __future__ import annotations

import copy
import csv
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

from capstone import Cs, CS_ARCH_X86, CS_MODE_32


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_source_unit_census.py"
SPEC = importlib.util.spec_from_file_location("re_source_unit_census", TOOL)
assert SPEC is not None and SPEC.loader is not None
census = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(census)
BUNDLE_VALUE = os.environ.get("BEA_SOURCE_UNIT_BUNDLE", "")
BUNDLE = Path(BUNDLE_VALUE).resolve() if BUNDLE_VALUE else None


def pe_fixture() -> bytearray:
    data = bytearray(0x264000)
    data[:2] = b"MZ"
    pe = 0x100
    struct.pack_into("<I", data, 0x3C, pe)
    data[pe : pe + 4] = b"PE\0\0"
    struct.pack_into("<H", data, pe + 4, 0x014C)
    struct.pack_into("<H", data, pe + 6, 4)
    struct.pack_into("<H", data, pe + 20, 224)
    optional = pe + 24
    struct.pack_into("<H", data, optional, 0x010B)
    struct.pack_into("<I", data, optional + 28, census.IMAGE_BASE)
    table = optional + 224
    sections = (
        (b".text", 0x1D6F9D, 0x1000, 0x1D7000, 0x1000),
        (b".rdata", 0x4985C, 0x1D8000, 0x4A000, 0x1D8000),
        (b".data", 0x3B2614, 0x222000, 0x3F000, 0x222000),
        (b".rsrc", 0x2F50, 0x5D5000, 0x3000, 0x261000),
    )
    for index, (name, virtual_size, rva, raw_size, raw_pointer) in enumerate(sections):
        offset = table + index * 40
        data[offset : offset + len(name)] = name
        struct.pack_into("<IIII", data, offset + 8, virtual_size, rva, raw_size, raw_pointer)
    return data


def decode(blob: bytes, base: int = census.IMAGE_BASE):
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    instructions = list(decoder.disasm(blob, base))
    return instructions, {instruction.address: index for index, instruction in enumerate(instructions)}


def forward_fixture(prefix: bytes, target: int | None = None) -> tuple[bytes, dict, int]:
    site = census.IMAGE_BASE
    blob = bytearray(b"\x90" * census.MAX_FORWARD_BYTES)
    blob[: len(prefix)] = prefix
    if target is not None:
        call = len(prefix)
        displacement = target - (site + call + 5)
        blob[call : call + 5] = b"\xe8" + struct.pack("<i", displacement)
    pe = {
        "sections": [
            {
                "name": ".text", "rva": 0, "virtualSize": len(blob),
                "rawSize": len(blob), "rawPointer": 0,
            }
        ]
    }
    return bytes(blob), pe, site


class CanonicalTsvTests(unittest.TestCase):
    def test_render_pins_column_order_and_final_lf(self) -> None:
        self.assertEqual(
            b"left\tright\nA\tB\n",
            census.render_tsv(("left", "right"), [{"left": "A", "right": "B"}]),
        )

    def test_reordered_header_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.tsv"
            path.write_text("right\tleft\nB\tA\n", encoding="utf-8", newline="")
            with self.assertRaisesRegex(census.CensusError, "header"):
                census.read_exact_tsv(path, ("left", "right"), "fixture")

    def test_trailing_blank_and_unexpected_comment_are_refused(self) -> None:
        for body in ("left\tright\nA\tB\n\n", "left\tright\nA\tB\n# ignored\n"):
            with self.subTest(body=body):
                with tempfile.TemporaryDirectory() as temporary:
                    path = Path(temporary) / "bad.tsv"
                    path.write_text(body, encoding="utf-8", newline="")
                    with self.assertRaises(census.CensusError):
                        census.read_exact_tsv(path, ("left", "right"), "fixture")

    def test_extra_column_and_control_value_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.tsv"
            path.write_text("left\tright\nA\tB\textra\n", encoding="utf-8", newline="")
            with self.assertRaisesRegex(census.CensusError, "malformed"):
                census.read_exact_tsv(path, ("left", "right"), "fixture")
        with self.assertRaisesRegex(census.CensusError, "control separator"):
            census.render_tsv(("left",), [{"left": "A\tB"}])


class PeTests(unittest.TestCase):
    def test_exact_pe_layout_and_initialized_mappings(self) -> None:
        pe = census.parse_pe(bytes(pe_fixture()))
        section, address = census.offset_mapping(pe, 0x222100)
        self.assertEqual(".data", section["name"])
        self.assertEqual(0x00622100, address)
        with self.assertRaisesRegex(census.CensusError, "uninitialized"):
            census.offset_mapping(pe, 0x1000 + 0x1D6F9D)
        with self.assertRaisesRegex(census.CensusError, "uninitialized"):
            census.va_to_offset(pe, census.IMAGE_BASE + 0x222000 + 0x3F000)

    def test_bad_headers_and_architecture_are_refused(self) -> None:
        mutations = []
        bad = pe_fixture(); bad[:2] = b"NZ"; mutations.append((bad, "DOS"))
        bad = pe_fixture(); bad[0x100 : 0x104] = b"PX\0\0"; mutations.append((bad, "PE signature"))
        bad = pe_fixture(); struct.pack_into("<H", bad, 0x104, 0x8664); mutations.append((bad, "i386"))
        bad = pe_fixture(); struct.pack_into("<H", bad, 0x118, 0x020B); mutations.append((bad, "PE32"))
        for data, message in mutations:
            with self.subTest(message=message):
                with self.assertRaisesRegex(census.CensusError, message):
                    census.parse_pe(bytes(data))

    def test_duplicate_and_overlapping_sections_are_refused(self) -> None:
        table = 0x100 + 24 + 224
        duplicate = pe_fixture()
        duplicate[table + 40 : table + 48] = b".text\0\0\0"
        with self.assertRaisesRegex(census.CensusError, "duplicate"):
            census.parse_pe(bytes(duplicate))
        overlap = pe_fixture()
        struct.pack_into("<I", overlap, table + 40 + 20, 0x1D7000)
        with self.assertRaisesRegex(census.CensusError, "overlapping"):
            census.parse_pe(bytes(overlap))

    def test_truncation_is_refused(self) -> None:
        with self.assertRaises(census.CensusError):
            census.parse_pe(bytes(pe_fixture()[:0x200]))


class PathPolicyTests(unittest.TestCase):
    def test_monitor_and_array_aliases_preserve_raw_but_collapse_canonical(self) -> None:
        monitor = [
            r"C:\dev\ONSLAUGHT2\Monitor.h",
            r"C:\dev\ONSLAUGHT2\monitor.h",
            r"C:\dev\ONSLAUGHT2\MissionScript\..\Monitor.h",
            r"C:\dev\ONSLAUGHT2\MissionScript\..\monitor.h",
        ]
        array = [r"C:\dev\ONSLAUGHT2\Array.h", r"C:\dev\ONSLAUGHT2\array.h"]
        self.assertEqual(1, len({census.canonicalize_source_path(value)[0] for value in monitor}))
        self.assertEqual("monitor.h", census.canonicalize_source_path(monitor[2])[1])
        self.assertEqual(1, len({census.canonicalize_source_path(value)[0] for value in array}))

    def test_escape_control_and_wrong_extension_are_refused(self) -> None:
        for value in (
            r"C:\dev\ONSLAUGHT2\..\escape.cpp",
            "C:\\dev\\ONSLAUGHT2\\bad\tname.cpp",
            r"C:\dev\ONSLAUGHT2\readme.txt",
        ):
            with self.subTest(value=value):
                with self.assertRaises(census.CensusError):
                    census.canonicalize_source_path(value)
        self.assertIsNone(census.PATH_REGEX.search(b"C:\\dev\\ONSLAUGHT2\\missing.cpp"))
        self.assertIsNone(census.PATH_REGEX.search(b"C:\\dev\\ONSLAUGHT2\\wrong.txt\x00"))


class DecodePolicyTests(unittest.TestCase):
    def test_candidate_requires_push_opcode_and_then_instruction_start(self) -> None:
        string_va = 0x12345678
        self.assertEqual([], census.exact_push_offsets(struct.pack("<I", string_va), string_va))
        embedded = b"\xb8\x68" + struct.pack("<I", string_va)
        self.assertEqual([1], census.exact_push_offsets(embedded, string_va))
        instructions, indices = decode(embedded)
        with self.assertRaisesRegex(census.CensusError, "instruction start"):
            census.decoded_line(instructions, indices, census.IMAGE_BASE + 1)

    def test_decoded_adjacent_line_boundary(self) -> None:
        instructions, indices = decode(b"\x6a\x7f\x68\x78\x56\x34\x12")
        self.assertEqual(
            ("0x00400000", "PUSH_IMM8", "127", "ADJACENT_DECODED_LINE_PUSH"),
            census.decoded_line(instructions, indices, census.IMAGE_BASE + 2),
        )
        instructions, indices = decode(b"\x68\x80\x00\x00\x00\x68\x78\x56\x34\x12")
        self.assertEqual(
            ("0x00400000", "PUSH_IMM32", "128", "ADJACENT_DECODED_LINE_PUSH"),
            census.decoded_line(instructions, indices, census.IMAGE_BASE + 5),
        )

    def test_nonpush_or_unadjacent_is_none(self) -> None:
        instructions, indices = decode(b"\x90\x68\x78\x56\x34\x12")
        self.assertEqual("NONE", census.decoded_line(instructions, indices, census.IMAGE_BASE + 1)[1])

    def test_noncanonical_line_encodings_are_refused(self) -> None:
        instructions, indices = decode(b"\x6a\x80\x68\x78\x56\x34\x12")
        with self.assertRaisesRegex(census.CensusError, "high-bit"):
            census.decoded_line(instructions, indices, census.IMAGE_BASE + 2)
        instructions, indices = decode(b"\x68\x7f\x00\x00\x00\x68\x78\x56\x34\x12")
        with self.assertRaisesRegex(census.CensusError, "below 128"):
            census.decoded_line(instructions, indices, census.IMAGE_BASE + 5)

    def test_first_expected_direct_call_and_conditional_branch_pass(self) -> None:
        blob, pe, site = forward_fixture(b"\x68\x78\x56\x34\x12\x75\x00", 0x005490E0)
        call, target = census.first_direct_call(blob, pe, site)
        self.assertEqual(site + 7, call)
        self.assertEqual(0x005490E0, target)

    def test_unknown_call_and_terminators_refuse(self) -> None:
        blob, pe, site = forward_fixture(b"\x68\x78\x56\x34\x12", 0x005490E1)
        with self.assertRaisesRegex(census.CensusError, "unknown"):
            census.first_direct_call(blob, pe, site)
        for terminal in (b"\xc3", b"\xcb", b"\xeb\x00"):
            with self.subTest(terminal=terminal.hex()):
                blob, pe, site = forward_fixture(b"\x68\x78\x56\x34\x12" + terminal, 0x005490E0)
                with self.assertRaises(census.CensusError):
                    census.first_direct_call(blob, pe, site)

    def test_indirect_or_out_of_window_call_is_not_direct_authority(self) -> None:
        blob, pe, site = forward_fixture(b"\x68\x78\x56\x34\x12\xff\xd0\xc3")
        with self.assertRaises(census.CensusError):
            census.first_direct_call(blob, pe, site)
        blob, pe, site = forward_fixture(b"\x68\x78\x56\x34\x12")
        with self.assertRaisesRegex(census.CensusError, "within 256"):
            census.first_direct_call(blob, pe, site)


class OwnerPolicyTests(unittest.TestCase):
    def test_fragment_hole_maps_residual_not_function_hull_and_end_is_exclusive(self) -> None:
        intervals = [
            {"lo": 0x1000, "hi": 0x1010, "kind": "FUNCTION", "entity": "F", "row": {}},
            {"lo": 0x1010, "hi": 0x1020, "kind": "RESIDUAL", "entity": "R", "row": {}},
            {"lo": 0x1020, "hi": 0x1030, "kind": "FUNCTION", "entity": "F", "row": {}},
        ]
        owners = {"allIntervals": intervals, "starts": [row["lo"] for row in intervals]}
        self.assertEqual("R", census.owner_at(owners, 0x1015)["entity"])
        self.assertEqual("R", census.owner_at(owners, 0x1010)["entity"])
        self.assertEqual("F", census.owner_at(owners, 0x1020)["entity"])

    def test_overlap_and_neither_owner_are_refused(self) -> None:
        with self.assertRaisesRegex(census.CensusError, "overlap"):
            census._require_no_overlap(
                [{"lo": 0x1000, "hi": 0x1020}, {"lo": 0x1010, "hi": 0x1030}],
                "fixture",
            )
        owners = {"allIntervals": [{"lo": 0x1000, "hi": 0x1010}], "starts": [0x1000]}
        with self.assertRaisesRegex(census.CensusError, "neither"):
            census.owner_at(owners, 0x1020)


@unittest.skipUnless(BUNDLE is not None and BUNDLE.is_dir(), "no frozen source-unit bundle requested")
class FrozenBundlePoisonTests(unittest.TestCase):
    def setUp(self) -> None:
        assert BUNDLE is not None
        self.temporary = Path(tempfile.mkdtemp(prefix="source-unit-poison-"))
        self.bundle = self.temporary / "bundle"
        shutil.copytree(BUNDLE, self.bundle)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary)

    def ready(self) -> dict:
        return json.loads((self.bundle / "source-unit-census.ready.json").read_text(encoding="utf-8"))

    def write_ready(self, ready: dict) -> None:
        (self.bundle / "source-unit-census.ready.json").write_text(
            json.dumps(ready, indent=2) + "\n", encoding="utf-8", newline="",
        )

    def restamp(self, ready: dict, name: str) -> None:
        ready["outputs"][name] = census.stamp(self.bundle / name, self.bundle)

    def test_frozen_owner_replays_its_bundle(self) -> None:
        self.assertEqual("READY", census.verify_bundle(self.bundle)["status"])

    def test_unmanifested_and_missing_files_are_refused(self) -> None:
        (self.bundle / "poison.txt").write_text("poison", encoding="utf-8")
        with self.assertRaisesRegex(census.CensusError, "unmanifested"):
            census.verify_bundle(self.bundle)
        (self.bundle / "poison.txt").unlink()
        (self.bundle / "source-units.tsv").unlink()
        with self.assertRaises(census.CensusError):
            census.verify_bundle(self.bundle)

    def test_symlink_output_is_refused_when_supported(self) -> None:
        path = self.bundle / "source-units.tsv"
        target = self.temporary / "source-units-target.tsv"
        shutil.copyfile(path, target)
        path.unlink()
        try:
            path.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaisesRegex(census.CensusError, "symlink"):
            census.verify_bundle(self.bundle)

    def test_self_restamped_trailing_blank_is_refused(self) -> None:
        path = self.bundle / "source-units.tsv"
        path.write_bytes(path.read_bytes() + b"\n")
        ready = self.ready(); self.restamp(ready, "source-units.tsv"); self.write_ready(ready)
        with self.assertRaises(census.CensusError):
            census.verify_bundle(self.bundle)

    def test_self_restamped_reordered_header_is_refused(self) -> None:
        path = self.bundle / "source-units.tsv"
        lines = path.read_text(encoding="utf-8").splitlines()
        columns = lines[0].split("\t"); columns[0], columns[1] = columns[1], columns[0]
        lines[0] = "\t".join(columns)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
        ready = self.ready(); self.restamp(ready, "source-units.tsv"); self.write_ready(ready)
        with self.assertRaises(census.CensusError):
            census.verify_bundle(self.bundle)

    def test_frozen_tool_and_count_poison_are_refused(self) -> None:
        owner = self.bundle / "source-unit-owner.py"
        owner.write_bytes(owner.read_bytes() + b"\n# poison\n")
        ready = self.ready(); self.restamp(ready, "source-unit-owner.py"); ready["tool"] = ready["outputs"]["source-unit-owner.py"]; self.write_ready(ready)
        with self.assertRaisesRegex(census.CensusError, "running tool"):
            census.verify_bundle(self.bundle)

    def test_ready_count_poison_is_refused(self) -> None:
        ready = self.ready()
        ready["counts"]["decodedCandidates"] -= 1
        self.write_ready(ready)
        with self.assertRaisesRegex(census.CensusError, "counts/state"):
            census.verify_bundle(self.bundle)


if __name__ == "__main__":
    unittest.main(verbosity=2)
