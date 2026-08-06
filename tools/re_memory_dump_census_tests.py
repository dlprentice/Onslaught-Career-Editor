#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the strict Level 100 memory-dump census owner."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


TOOL = Path(__file__).with_name("re_memory_dump_census.py")
SPEC = importlib.util.spec_from_file_location("re_memory_dump_census", TOOL)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_memory_types() -> list[str]:
    return [f"Type {index:03d}" for index in range(MODULE.EXPECTED_MEMORY_TYPES)]


def make_dump(
    trace: str,
    heap_blocks: list[list[tuple[int, int, int, int, int, int, str, int]]],
    *,
    memory_types: list[str] | None = None,
    num_tags: int = 0,
) -> bytes:
    types = memory_types or make_memory_types()
    lines = ["#Trace name", trace, "#MemTypes", str(len(types)), *types]
    lines.extend(["#Heaps", str(len(heap_blocks))])
    for heap_index, blocks in enumerate(heap_blocks):
        lines.extend([
            f"# Heap {heap_index}",
            f"Heap {heap_index}",
            "# Size",
            str(1024 * (heap_index + 1)),
            "# NumBlocks",
            str(len(blocks)),
        ])
        for offset, fields in enumerate(blocks):
            lines.append(f"# Heap {heap_index} Block {len(blocks) + offset}")
            lines.extend(str(value) for value in fields)
    lines.extend(["# NumTags", str(num_tags)])
    return ("\n".join(lines) + "\n").encode("ascii")


def make_memstats(memory_types: list[str], values: dict[int, tuple[int, int]] | None = None) -> bytes:
    values = values or {}
    rows = [(name, *values.get(index, (0, 0))) for index, name in enumerate(memory_types)]
    used = sum(row[1] for row in rows)
    total = max(4096, used)
    lines = [
        f"Used: {used} bytes",
        f"Free: {total - used} bytes",
        f"Total: {total} bytes",
        "",
    ]
    # MemStats is size-ranked rather than memory-type ordered in the preserved file.
    for name, byte_count, block_count in sorted(rows, key=lambda row: (-row[1], row[0])):
        lines.append(f"{name:<32} : {byte_count:15d} bytes : {block_count:15d} blocks")
    return ("\n".join(lines) + "\n").encode("ascii")


def make_source_paths(rows: list[tuple[int, str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(MODULE.SOURCE_PATH_COLUMNS),
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for ordinal, (va, raw_path, canonical_key) in enumerate(rows):
        writer.writerow({
            "pathStringKey": f"PATH:{ordinal}",
            "stringVa": f"0x{va:08x}",
            "stringRva": f"0x{va - 0x400000:08x}",
            "fileOffset": f"0x{va - 0x400000:08x}",
            "sectionName": ".data",
            "rawPath": raw_path,
            "canonicalPathKey": canonical_key,
            "canonicalWindowsPath": raw_path.lower(),
            "canonicalRelativePath": Path(raw_path).name.lower(),
            "pathKind": "CPP",
            "extension": ".cpp",
            "canonicalAliasCount": 1,
            "pushSiteCount": 1,
            "primaryPlateSiteCount": 1,
            "unwindFreePlateSiteCount": 0,
            "mappedFunctionSiteCount": 1,
            "residualSiteCount": 0,
        })
    return output.getvalue().encode("utf-8")


def make_source_ready(source_paths: bytes) -> bytes:
    return MODULE.canonical_json({
        "schema": "bea.re.source-unit-census.v1",
        "status": "READY",
        "specimen": {"sha256": MODULE.EXPECTED_SPECIMEN_SHA256},
        "outputs": {
            "source-path-strings.tsv": {
                "bytes": len(source_paths),
                "sha256": digest(source_paths),
            }
        },
    })


class Fixture:
    def __init__(self, root: Path, *, substring_trace: bool = False):
        self.root = root
        self.memory_types = make_memory_types()
        source_va = 0x00600000
        trace = f"prefix{source_va}suffix" if substring_trace else "Before"
        existing = (1, 32, 48, 0x00001000, 3, 0, "Unknown", 0)
        changed_before = (1, 64, 80, 0x00002000, 4, 1, "Unknown", 0)
        changed_after = (1, 96, 112, 0x00002000, 5, 0, "Unknown", 0)
        added = (1, 16, 32, 0x00003000, 6, 0, "Unknown", 0)
        self.before = make_dump(trace, [[], [], [], [existing, changed_before]], memory_types=self.memory_types)
        self.after = make_dump("After", [[], [], [], [existing, changed_after, added]], memory_types=self.memory_types)
        self.memstats = make_memstats(self.memory_types)
        self.source_paths = make_source_paths([
            (source_va, r"C:\dev\ONSLAUGHT2\One.cpp", "SOURCE:ONE"),
            (source_va + 0x100, r"C:\dev\ONSLAUGHT2\Alias.cpp", "SOURCE:ONE"),
        ])
        self.source_ready = make_source_ready(self.source_paths)
        payloads = {
            "beforeDump": ("before.mem", self.before),
            "afterDump": ("after.mem", self.after),
            "memStats": ("memstats.txt", self.memstats),
            "sourcePaths": ("source-paths.tsv", self.source_paths),
            "sourceReady": ("source.ready.json", self.source_ready),
        }
        self.paths: dict[str, Path] = {}
        self.pins: dict[str, str] = {}
        for role, (name, data) in payloads.items():
            path = root / name
            path.write_bytes(data)
            self.paths[role] = path
            self.pins[role] = digest(data)


class MemoryDumpCensusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="memory-dump-census-test-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def fixture(self, *, substring_trace: bool = False) -> Fixture:
        return Fixture(self.temp, substring_trace=substring_trace)

    def build(self, fixture: Fixture, name: str = "bundle") -> Path:
        bundle = self.temp / name
        MODULE.build_bundle(
            bundle,
            TOOL,
            fixture.paths,
            input_pins=fixture.pins,
            expected_outcomes=None,
        )
        return bundle

    def verify(self, fixture: Fixture, bundle: Path) -> dict[str, object]:
        return MODULE.verify_bundle(
            bundle,
            TOOL,
            fixture.paths,
            input_pins=fixture.pins,
            expected_outcomes=None,
        )

    def test_exact_dump_parser_preserves_eight_fields_and_zero_tags(self) -> None:
        fixture = self.fixture()
        parsed = MODULE.parse_dump(fixture.before, "before")
        self.assertEqual(129, len(parsed.memory_types))
        self.assertEqual(4, len(parsed.heaps))
        self.assertEqual(2, len(parsed.blocks))
        self.assertEqual(0, parsed.num_tags)
        block = parsed.blocks[0]
        self.assertEqual((1, 32, 48, 0x1000, 3, 0, "Unknown", 0), (
            block.record_state,
            block.payload_bytes,
            block.accounted_bytes,
            block.address,
            block.memory_type_index,
            block.reported_flag,
            block.reported_label,
            block.reported_line,
        ))

    def test_round_trip_is_exact_and_replayable(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        ready = self.verify(fixture, bundle)
        self.assertEqual("READY", ready["status"])
        self.assertEqual(2, ready["counts"]["beforeBlocks"])
        self.assertEqual(3, ready["counts"]["afterBlocks"])
        self.assertEqual(1, ready["counts"]["addedAddresses"])
        self.assertEqual(1, ready["counts"]["changedAddresses"])
        self.assertEqual(1, ready["counts"]["unchangedAddresses"])
        self.assertEqual("REFUTED_IN_TWO_BOUND_DUMPS", ready["sourcePathHypothesis"]["verdict"])
        self.assertEqual(set(MODULE.OUTPUT_NAMES) | {"READY.json"}, {p.name for p in bundle.iterdir()})

    def test_two_publications_are_byte_identical(self) -> None:
        fixture = self.fixture()
        first = self.build(fixture, "first")
        second = self.build(fixture, "second")
        for name in set(MODULE.OUTPUT_NAMES) | {"READY.json"}:
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)

    def test_block_serial_renumbering_is_not_a_false_change(self) -> None:
        fixture = self.fixture()
        outputs, summary = MODULE.derive_from_paths(
            fixture.paths, input_pins=fixture.pins, expected_outcomes=None
        )
        self.assertEqual(1, summary["counts"]["unchangedAddresses"])
        rows = list(csv.DictReader(
            io.StringIO(outputs["address-delta.tsv"].decode("utf-8")), delimiter="\t"
        ))
        existing = next(row for row in rows if row["addressHex"] == "0x00001000")
        self.assertEqual("UNCHANGED", existing["disposition"])
        self.assertNotEqual(existing["beforeBlockSerial"], existing["afterBlockSerial"])

    def test_memstats_zero_categories_still_expose_dump_cohorts(self) -> None:
        fixture = self.fixture()
        outputs, summary = MODULE.derive_from_paths(
            fixture.paths, input_pins=fixture.pins, expected_outcomes=None
        )
        self.assertGreater(summary["counts"]["beforeMemStatsJoin"]["MEMSTATS_ZERO_DUMP_NONZERO"], 0)
        rows = list(csv.DictReader(
            io.StringIO(outputs["memstats-join.tsv"].decode("utf-8")), delimiter="\t"
        ))
        type_three = next(row for row in rows if row["memoryTypeIndex"] == "3")
        self.assertEqual("0", type_three["memStatsBlockCount"])
        self.assertEqual("1", type_three["beforeBlockCount"])
        self.assertEqual("MEMSTATS_ZERO_DUMP_NONZERO", type_three["beforeJoinDisposition"])

    def test_decimal_substrings_are_not_source_hits(self) -> None:
        fixture = self.fixture(substring_trace=True)
        _, summary = MODULE.derive_from_paths(
            fixture.paths, input_pins=fixture.pins, expected_outcomes=None
        )
        self.assertEqual(0, summary["sourcePathHypothesis"]["exactDecimalLineHits"])
        self.assertEqual("REFUTED_IN_TWO_BOUND_DUMPS", summary["sourcePathHypothesis"]["verdict"])

    def test_each_source_instrument_can_make_the_hypothesis_survive(self) -> None:
        fixture = self.fixture()
        source_va = 0x44434241  # little-endian bytes are the strict-ASCII text ABCD
        raw_path = r"C:\dev\ONSLAUGHT2\Observable.cpp"
        fixture.before = fixture.before.replace(
            b"#Trace name\nBefore\n",
            f"#Trace name\n{source_va}\n".encode("ascii"),
            1,
        )
        fixture.after = fixture.after.replace(
            b"#Trace name\nAfter\n",
            f"#Trace name\nABCD {raw_path}\n".encode("ascii"),
            1,
        )
        fixture.source_paths = make_source_paths([(source_va, raw_path, "SOURCE:OBSERVABLE")])
        fixture.source_ready = make_source_ready(fixture.source_paths)
        replacements = {
            "beforeDump": fixture.before,
            "afterDump": fixture.after,
            "sourcePaths": fixture.source_paths,
            "sourceReady": fixture.source_ready,
        }
        for role, data in replacements.items():
            fixture.paths[role].write_bytes(data)
            fixture.pins[role] = digest(data)
        _, summary = MODULE.derive_from_paths(
            fixture.paths, input_pins=fixture.pins, expected_outcomes=None
        )
        hypothesis = summary["sourcePathHypothesis"]
        self.assertGreater(hypothesis["littleEndianVaHits"], 0)
        self.assertGreater(hypothesis["exactDecimalLineHits"], 0)
        self.assertGreater(hypothesis["fullPathTextHits"], 0)
        self.assertEqual("SURVIVED", hypothesis["verdict"])

    def test_non_sixteen_reported_delta_is_refused_before_publication(self) -> None:
        fixture = self.fixture()
        poisoned = fixture.before.replace(b"\n32\n48\n4096\n", b"\n32\n47\n4096\n", 1)
        fixture.paths["beforeDump"].write_bytes(poisoned)
        fixture.pins["beforeDump"] = digest(poisoned)
        out = self.temp / "must-not-publish"
        with self.assertRaisesRegex(MODULE.CensusError, "reported 16-byte delta"):
            MODULE.build_bundle(
                out,
                TOOL,
                fixture.paths,
                input_pins=fixture.pins,
                expected_outcomes=None,
            )
        self.assertFalse(out.exists())
        self.assertFalse(any(path.name.startswith(".must-not-publish-") for path in self.temp.iterdir()))

    def test_parser_refuses_format_poisons(self) -> None:
        fixture = self.fixture()
        cases = {
            "crlf": fixture.before.replace(b"\n", b"\r\n"),
            "missing-terminal-lf": fixture.before[:-1],
            "wrong-type-count": fixture.before.replace(b"#MemTypes\n129\n", b"#MemTypes\n128\n", 1),
            "wrong-heaps": fixture.before.replace(b"#Heaps\n4\n", b"#Heaps\n3\n", 1),
            "nonzero-tags": fixture.before[:-2] + b"1\n",
            "trailing-line": fixture.before + b"poison\n",
            "duplicate-address": fixture.before.replace(b"\n8192\n4\n", b"\n4096\n4\n", 1),
        }
        for name, data in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(MODULE.CensusError):
                    MODULE.parse_dump(data, name)

    def test_source_ready_must_authenticate_the_exact_tsv(self) -> None:
        fixture = self.fixture()
        poisoned = fixture.source_paths.replace(b"One.cpp", b"Two.cpp", 1)
        fixture.paths["sourcePaths"].write_bytes(poisoned)
        fixture.pins["sourcePaths"] = digest(poisoned)
        with self.assertRaisesRegex(MODULE.CensusError, "attestation differs"):
            MODULE.derive_from_paths(
                fixture.paths, input_pins=fixture.pins, expected_outcomes=None
            )

    def test_input_pin_defeats_ready_restamping(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        poisoned = fixture.before.replace(b"Before", b"Poison", 1)
        fixture.paths["beforeDump"].write_bytes(poisoned)
        ready_path = bundle / "READY.json"
        ready = json.loads(ready_path.read_text(encoding="utf-8"))
        ready["inputs"]["beforeDump"] = {"bytes": len(poisoned), "sha256": digest(poisoned)}
        ready_path.write_bytes(MODULE.canonical_json(ready))
        with self.assertRaisesRegex(MODULE.CensusError, "beforeDump SHA-256 differs"):
            self.verify(fixture, bundle)

    def test_self_restamped_output_is_rederived_and_refused(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        output = bundle / "memory-types.tsv"
        poisoned = output.read_bytes() + b"poison\n"
        output.write_bytes(poisoned)
        ready_path = bundle / "READY.json"
        ready = json.loads(ready_path.read_text(encoding="utf-8"))
        ready["outputs"]["memory-types.tsv"] = {
            "bytes": len(poisoned), "sha256": digest(poisoned)
        }
        ready_path.write_bytes(MODULE.canonical_json(ready))
        with self.assertRaisesRegex(MODULE.CensusError, "READY semantics differ"):
            self.verify(fixture, bundle)

    def test_frozen_owner_must_equal_executed_owner(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        alternate = self.temp / "alternate-owner.py"
        alternate.write_bytes(TOOL.read_bytes() + b"\n# poison\n")
        with self.assertRaisesRegex(MODULE.CensusError, "frozen owner differs"):
            MODULE.verify_bundle(
                bundle,
                alternate,
                fixture.paths,
                input_pins=fixture.pins,
                expected_outcomes=None,
            )

    def test_exact_tree_refuses_extra_and_missing_members(self) -> None:
        fixture = self.fixture()
        extra_bundle = self.build(fixture, "extra")
        (extra_bundle / "extra.txt").write_text("poison", encoding="utf-8")
        with self.assertRaisesRegex(MODULE.CensusError, "bundle members differ"):
            self.verify(fixture, extra_bundle)
        missing_bundle = self.build(fixture, "missing")
        (missing_bundle / "size-cohorts.tsv").unlink()
        with self.assertRaisesRegex(MODULE.CensusError, "bundle members differ"):
            self.verify(fixture, missing_bundle)

    def test_symlinked_member_is_refused(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        member = bundle / "memory-types.tsv"
        target = self.temp / "outside.tsv"
        target.write_bytes(member.read_bytes())
        member.unlink()
        try:
            os.symlink(target, member)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(MODULE.CensusError, "not a plain file"):
            self.verify(fixture, bundle)

    def test_duplicate_json_key_in_ready_is_refused(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        ready = (bundle / "READY.json").read_bytes()
        poisoned = ready.replace(b'{\n  "censusSchema"', b'{\n  "status": "READY",\n  "censusSchema"', 1)
        (bundle / "READY.json").write_bytes(poisoned)
        with self.assertRaisesRegex(MODULE.CensusError, "duplicate JSON key"):
            self.verify(fixture, bundle)

    def test_existing_output_is_never_overwritten(self) -> None:
        fixture = self.fixture()
        bundle = self.build(fixture)
        before = {path.name: digest(path.read_bytes()) for path in bundle.iterdir()}
        with self.assertRaisesRegex(MODULE.CensusError, "output already exists"):
            MODULE.build_bundle(
                bundle,
                TOOL,
                fixture.paths,
                input_pins=fixture.pins,
                expected_outcomes=None,
            )
        self.assertEqual(before, {path.name: digest(path.read_bytes()) for path in bundle.iterdir()})

    def test_publication_failure_cleans_staging_and_publishes_nothing(self) -> None:
        fixture = self.fixture()
        out = self.temp / "atomic-boundary"
        with mock.patch.object(MODULE.os, "replace", side_effect=OSError("injected")):
            with self.assertRaisesRegex(OSError, "injected"):
                MODULE.build_bundle(
                    out,
                    TOOL,
                    fixture.paths,
                    input_pins=fixture.pins,
                    expected_outcomes=None,
                )
        self.assertFalse(out.exists())
        self.assertFalse(any(path.name.startswith(".atomic-boundary-") for path in self.temp.iterdir()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
