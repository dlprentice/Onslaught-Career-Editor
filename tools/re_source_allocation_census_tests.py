#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused can-fail tests for :mod:`re_source_allocation_census`."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from capstone import Cs, CS_ARCH_X86, CS_MODE_32


MODULE_PATH = Path(__file__).with_name("re_source_allocation_census.py")
SPEC = importlib.util.spec_from_file_location("re_source_allocation_census", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
census = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(census)


def one_section_pe(raw: bytes, *, image_base: int = 0x00400000, rva: int = 0x1000) -> tuple[bytes, int]:
    """Return a minimal file-backed PE32 fixture and its section VA."""
    raw_offset = 0x200
    data = bytearray(raw_offset + len(raw))
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", data, 0x86, 1)
    struct.pack_into("<H", data, 0x94, 0xE0)
    struct.pack_into("<H", data, 0x98, 0x10B)
    struct.pack_into("<I", data, 0x98 + 28, image_base)
    section = 0x80 + 24 + 0xE0
    data[section:section + 8] = b".text\0\0\0"
    struct.pack_into("<IIII", data, section + 8, len(raw), rva, len(raw), raw_offset)
    data[raw_offset:] = raw
    return bytes(data), image_base + rva


def memory_rows() -> bytes:
    rows = []
    for snapshot in ("BEFORE", "AFTER"):
        for index in range(129):
            row = {column: "0" for column in census.MEMORY_COLUMNS}
            row["snapshot"] = snapshot
            row["memoryTypeIndex"] = str(index)
            row["memoryTypeName"] = (
                "MessageBox" if index == 41 else
                "Name not found" if index == 42 else
                f"T{index}"
            )
            rows.append(row)
    return census.render_tsv(census.MEMORY_COLUMNS, rows)


def synthetic_bundle(root: Path, *, owner: bytes | None = None, ready: bytes | None = None) -> Path:
    root.mkdir(parents=True)
    bundle = root / "bundle"
    bundle.mkdir()
    inputs = bundle / "inputs"
    inputs.mkdir()
    for name in census.INPUT_NAMES:
        (inputs / name).write_bytes(b"")
    for name in census.OUTPUT_NAMES:
        (bundle / name).write_bytes(b"")
    (bundle / "source-allocation-owner.py").write_bytes(MODULE_PATH.read_bytes() if owner is None else owner)
    (bundle / "READY.json").write_bytes(census.canonical_json({}) if ready is None else ready)
    return bundle


class SourceAllocationCensusTests(unittest.TestCase):
    def test_runtime_type_snapshots_must_agree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "memory.tsv"
            path.write_bytes(memory_rows())
            names = census.parse_runtime_type_names(path)
            self.assertEqual(129, len(names))
            self.assertEqual("MessageBox", names[41])
            self.assertEqual("Name not found", names[42])

            poisoned = path.read_bytes().replace(b"AFTER\t42\tName not found", b"AFTER\t42\tName was found", 1)
            path.write_bytes(poisoned)
            with self.assertRaisesRegex(census.CensusError, "differ between snapshots"):
                census.parse_runtime_type_names(path)

    def test_physical_duplicate_and_runtime_fallback_are_exact(self) -> None:
        indices = list(range(42)) + [41] + list(range(43, 129))
        self.assertEqual(129, len(indices))
        raw = bytearray(130 * census.MEMORY_TABLE_STRIDE)
        runtime = [f"T{index}" for index in range(129)]
        runtime[41] = "MessageBox"
        runtime[42] = "Name not found"
        for ordinal, index in enumerate(indices):
            name = "MessageLog" if ordinal == 42 else runtime[index]
            record = ordinal * census.MEMORY_TABLE_STRIDE
            struct.pack_into("<I", raw, record, index)
            raw[record + 4:record + 4 + len(name)] = name.encode("ascii")
            struct.pack_into("<I", raw, record + 36, 0xFFFFFFFF)
        sentinel = 129 * census.MEMORY_TABLE_STRIDE
        struct.pack_into("<I", raw, sentinel, 129)
        struct.pack_into("<I", raw, sentinel + 36, 0xFFFFFFFF)
        pe_data, table_va = one_section_pe(bytes(raw))
        pe = census.parse_pe(pe_data)
        with (
            mock.patch.object(census, "MEMORY_TABLE_VA", table_va),
            mock.patch.object(census, "MEMORY_TABLE_SHA256", hashlib.sha256(raw[:sentinel]).hexdigest()),
        ):
            physical, logical = census.extract_memory_table(pe_data, pe, runtime)
        self.assertEqual(129, len(physical))
        self.assertEqual("MessageBox", logical[41]["memoryTypeName"])
        self.assertEqual("NO_PHYSICAL_ROW_RUNTIME_FALLBACK", logical[42]["mappingDisposition"])
        self.assertEqual("", logical[42]["physicalOrdinal"])

    def test_operand_decoder_distinguishes_immediate_and_register(self) -> None:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        immediate, register = list(md.disasm(b"\x6a\x2a\x51", 0x1000))
        self.assertEqual(("IMMEDIATE", "0x2a", 42), census.operand_value(md, immediate))
        self.assertEqual(("REGISTER", "ecx", None), census.operand_value(md, register))

    def test_local_constant_requires_no_branch_entry(self) -> None:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        clean = list(md.disasm(b"\xb9\x01\x00\x00\x00\x89\x08\x51", 0x1000))
        self.assertEqual(
            (1, "LOCAL_NO_ENTRY_LINEAR_IMMEDIATE"),
            census.resolve_local_constant(md, clean, "ecx", clean[-1].address),
        )

        # jne lands directly on the push and therefore permits a path that
        # bypasses the otherwise-nearest mov ecx,1 definition.
        branched = list(md.disasm(b"\x75\x05\xb9\x01\x00\x00\x00\x51", 0x2000))
        self.assertEqual(
            (None, "DYNAMIC_REGISTER_BRANCH_ENTRY"),
            census.resolve_local_constant(md, branched, "ecx", branched[-1].address),
        )

        call_clobber = list(md.disasm(b"\xb9\x01\x00\x00\x00\xe8\x00\x00\x00\x00\x51", 0x3000))
        self.assertEqual(
            (None, "DYNAMIC_REGISTER_CALL_CLOBBER"),
            census.resolve_local_constant(md, call_clobber, "ecx", call_clobber[-1].address),
        )

        partial_write = list(md.disasm(b"\xb9\x01\x00\x00\x00\xb1\x02\x51", 0x4000))
        self.assertEqual(
            (None, "DYNAMIC_REGISTER_ALIASED_WRITE"),
            census.resolve_local_constant(md, partial_write, "ecx", partial_write[-1].address),
        )

        dynamic_definition = list(md.disasm(b"\x8b\x4c\x24\x04\x51", 0x4800))
        self.assertEqual(
            (None, "DYNAMIC_REGISTER_NONCONSTANT_DEFINITION"),
            census.resolve_local_constant(md, dynamic_definition, "ecx", dynamic_definition[-1].address),
        )

        indirect_jump = list(md.disasm(b"\xb9\x01\x00\x00\x00\xff\xe0\x51", 0x5000))
        self.assertEqual(
            (None, "DYNAMIC_REGISTER_INDIRECT_CONTROL_FLOW"),
            census.resolve_local_constant(md, indirect_jump, "ecx", indirect_jump[-1].address),
        )

        nonfallthrough = list(md.disasm(b"\xb9\x01\x00\x00\x00\xc3\x51", 0x6000))
        self.assertEqual(
            (None, "DYNAMIC_REGISTER_NONFALLTHROUGH"),
            census.resolve_local_constant(md, nonfallthrough, "ecx", nonfallthrough[-1].address),
        )

    def test_primary_plate_is_redecoded_and_hash_bound(self) -> None:
        target = 0x00401100
        start = 0x00401000
        path_va = 0x00402000
        prefix = b"\x68" + struct.pack("<I", path_va) + b"\x6a\x05\x6a\x10"
        call_va = start + len(prefix)
        body = prefix + b"\xe8" + struct.pack("<i", target - (call_va + 5))
        pe_data, section_va = one_section_pe(body)
        self.assertEqual(start, section_va)
        pe = census.parse_pe(pe_data)
        row = {column: "" for column in census.SOURCE_COLUMNS}
        row.update({
            "siteKey": "fixture", "siteVa": f"0x{start:08x}", "siteRva": "0x00001000",
            "fileOffset": "0x00000200", "canonicalRelativePath": "fixture.cpp",
            "pathPushBytes": body[:5].hex(), "lineValue": "7",
            "firstDirectCallVa": f"0x{call_va:08x}", "firstDirectCallTargetVa": f"0x{target:08x}",
            "plateClass": "PRIMARY_ALLOC_SOURCE_PLATE", "plateStartVa": f"0x{start:08x}",
            "plateEndExclusiveVa": f"0x{start + len(body):08x}", "plateBytesSha256": hashlib.sha256(body).hexdigest(),
            "pathOwnerKind": "FUNCTION", "pathOwnerEntityKey": "owner",
            "pathOwnerIntervalStartVa": f"0x{start:08x}", "pathFunctionEntryVa": f"0x{start:08x}",
            "pathFunctionName": "Fixture", "callOwnerKind": "FUNCTION", "callOwnerEntityKey": "owner",
            "ownerBoundaryCrossing": "False",
        })
        with mock.patch.object(census, "PRIMARY_TARGETS", frozenset({target})):
            result = census.derive_sites(pe_data, pe, [row], [f"T{i}" for i in range(129)])
        self.assertEqual(5, result[0]["typeValue"])
        self.assertEqual(16, result[0]["sizeValue"])
        row["plateBytesSha256"] = "0" * 64
        with mock.patch.object(census, "PRIMARY_TARGETS", frozenset({target})):
            with self.assertRaisesRegex(census.CensusError, "plate hash differs"):
                census.derive_sites(pe_data, pe, [row], [f"T{i}" for i in range(129)])

    def test_real_ready_replays_when_local_evidence_is_present(self) -> None:
        root = Path(__file__).resolve().parents[1]
        bundle = root / "local-lab" / "source-allocation-census-v1-ready"
        specimen = root / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
        if not bundle.is_dir() or not specimen.is_file():
            self.skipTest("ignored maintainer evidence is not present")
        result = census.verify(bundle, specimen)
        self.assertEqual(census.STATUS, result["status"])
        self.assertEqual(census.EXPECTED_COUNTS, result["counts"])

    def test_structural_attacks_need_no_local_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            owner_attack = synthetic_bundle(
                temporary_root / "owner",
                owner=MODULE_PATH.read_bytes() + b"# self-restamped mutation\n",
            )
            with self.assertRaisesRegex(census.CensusError, "bundled owner differs"):
                census.verify(owner_attack, temporary_root / "unused-specimen")

            directory_attack = synthetic_bundle(temporary_root / "directory")
            (directory_attack / "undeclared").mkdir()
            with self.assertRaisesRegex(census.CensusError, "root entry set differs"):
                census.validate_bundle_tree(directory_attack)

            canonical_attack = synthetic_bundle(temporary_root / "canonical", ready=b"{}")
            with self.assertRaisesRegex(census.CensusError, "not canonical JSON"):
                census.verify(canonical_attack, temporary_root / "unused-specimen")

    @unittest.skipUnless(os.name == "nt" and hasattr(Path, "is_junction"), "Windows junctions unavailable")
    def test_cli_rejects_root_junction_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            target = synthetic_bundle(temporary_root / "target")
            junction = temporary_root / "bundle-junction"
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            if created.returncode != 0 or not junction.is_junction():
                self.skipTest(f"cannot create a test junction: {created.stderr.strip()}")
            try:
                result = subprocess.run(
                    [sys.executable, "-B", str(MODULE_PATH), "verify", "--bundle", str(junction),
                     "--specimen", str(temporary_root / "unused-specimen")],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(2, result.returncode)
                self.assertIn("reparse point", result.stderr)
            finally:
                os.rmdir(junction)


if __name__ == "__main__":
    unittest.main(verbosity=2)
