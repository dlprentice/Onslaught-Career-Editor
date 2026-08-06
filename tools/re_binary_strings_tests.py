#!/usr/bin/env python3
"""Focused can-fail tests for the specimen-bound binary-string corpus."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_binary_strings.py"
SPEC = importlib.util.spec_from_file_location("re_binary_strings", TOOL)
assert SPEC is not None and SPEC.loader is not None
corpus = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = corpus
SPEC.loader.exec_module(corpus)


def pe_fixture() -> bytes:
    data = bytearray(0x300)
    data[:2] = b"MZ"
    pe_offset = 0x80
    struct.pack_into("<I", data, 0x3C, pe_offset)
    data[pe_offset : pe_offset + 4] = b"PE\0\0"
    struct.pack_into("<H", data, pe_offset + 6, 1)
    struct.pack_into("<H", data, pe_offset + 20, 0xE0)
    optional = pe_offset + 24
    struct.pack_into("<H", data, optional, 0x10B)
    struct.pack_into("<I", data, optional + 28, 0x00400000)
    struct.pack_into("<I", data, optional + 60, 0x200)
    section = optional + 0xE0
    data[section : section + 8] = b".text\0\0\0"
    struct.pack_into("<IIII", data, section + 8, 0x80, 0x1000, 0x100, 0x200)
    return bytes(data)


def stamp(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


class PeAndScanTests(unittest.TestCase):
    def test_pe_offsets_map_to_headers_section_and_overlay(self) -> None:
        image = corpus.parse_pe(pe_fixture())
        self.assertEqual(("Headers", 0x00400100), image.locate(0x100))
        self.assertEqual((".text", 0x00401020), image.locate(0x220))
        self.assertEqual(("Overlay", None), image.locate(0x500))

    def test_bad_pe_signatures_and_pe32_plus_are_refused(self) -> None:
        bad_dos = bytearray(pe_fixture())
        bad_dos[:2] = b"NZ"
        with self.assertRaisesRegex(corpus.CorpusError, "DOS/PE"):
            corpus.parse_pe(bytes(bad_dos))
        bad_magic = bytearray(pe_fixture())
        struct.pack_into("<H", bad_magic, 0x80 + 24, 0x20B)
        with self.assertRaisesRegex(corpus.CorpusError, "PE32"):
            corpus.parse_pe(bytes(bad_magic))

    def test_ascii_and_western_wide_candidates_are_kept(self) -> None:
        data = b"\0HELLO\0\0" + "Caf\N{LATIN SMALL LETTER E WITH ACUTE}".encode("utf-16le") + b"\0\0"
        image = corpus.PeImage(0x00400000, 0, (corpus.Section("blob", 0, len(data), 0, len(data)),))
        rows = corpus.scan_raw_strings(data, image, minimum=4)
        values = {(row.encoding, row.value, row.nul_terminated) for row in rows}
        self.assertIn(("ascii", "HELLO", True), values)
        self.assertIn(("utf-16le", "Caf\N{LATIN SMALL LETTER E WITH ACUTE}", True), values)

    def test_arbitrary_cjk_byte_pairs_are_not_promoted_to_wide_strings(self) -> None:
        data = struct.pack("<HHHHH", 0x4E00, 0x4E01, 0x4E02, 0x4E03, 0)
        image = corpus.PeImage(0x00400000, 0, (corpus.Section("blob", 0, len(data), 0, len(data)),))
        self.assertFalse(any(row.encoding == "utf-16le" for row in corpus.scan_raw_strings(data, image)))

    def test_too_small_minimum_is_refused(self) -> None:
        with self.assertRaisesRegex(corpus.CorpusError, "at least two"):
            corpus.scan_raw_strings(b"TEXT", corpus.PeImage(0, 0, ()), minimum=1)


class DefinedInputTests(unittest.TestCase):
    def write_fixture(self, root: Path) -> tuple[Path, Path]:
        value = "ShowCmds"
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        header = (
            "address\tfile_offset\tsection\tdata_type\tchar_count\tbyte_length\t"
            "value_utf8_sha256\txref_count\tcode_xref_count\tfunction_entries\tvalue_json\n"
        )
        row = f"00624fd8\t0x00224fd8\t.data\t/string\t8\t9\t{digest}\t3\t3\t00429ef0\t{json.dumps(value)}\n"
        table = root / "defined.tsv"
        table.write_text(header + row, encoding="utf-8", newline="")
        ready = root / "defined.ready.json"
        receipt = {
            "schema": "bea.re.ghidra-defined-strings.v1",
            "status": "READY",
            "executableSha256": corpus.EXPECTED_SPECIMEN_SHA256,
            "definedStringRows": 1,
            "output": {
                "bytes": table.stat().st_size,
                "sha256": hashlib.sha256(table.read_bytes()).hexdigest(),
            },
        }
        ready.write_text(json.dumps(receipt), encoding="utf-8")
        return table, ready

    def test_defined_table_is_hash_and_value_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            table, ready = self.write_fixture(Path(temporary))
            rows, _ = corpus.load_defined_strings(table, ready)
            self.assertEqual("ShowCmds", rows[0]["value"])
            table.write_text(table.read_text(encoding="utf-8").replace("ShowCmds", "ShowVars"), encoding="utf-8")
            with self.assertRaisesRegex(corpus.CorpusError, "does not match"):
                corpus.load_defined_strings(table, ready)

    def test_wrong_specimen_receipt_is_refused_even_if_table_hash_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            table, ready = self.write_fixture(Path(temporary))
            receipt = json.loads(ready.read_text(encoding="utf-8"))
            receipt["executableSha256"] = "0" * 64
            ready.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(corpus.CorpusError, "wrong specimen"):
                corpus.load_defined_strings(table, ready)


class ReadyVerificationTests(unittest.TestCase):
    def test_ready_rehashes_every_named_artifact_and_detects_poison(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            specimen = root / "fixture.exe"
            specimen.write_bytes(pe_fixture())
            input_file = root / "input.tsv"
            output_file = root / "output.tsv"
            input_file.write_text("input\n", encoding="utf-8")
            output_file.write_text("output\n", encoding="utf-8")
            expected = hashlib.sha256(specimen.read_bytes()).hexdigest()
            old_expected = corpus.EXPECTED_SPECIMEN_SHA256
            corpus.EXPECTED_SPECIMEN_SHA256 = expected
            try:
                ready = root / "READY.json"
                ready.write_text(
                    json.dumps(
                        {
                            "schema": corpus.SCHEMA,
                            "status": "READY",
                            "specimen": stamp(specimen),
                            "counts": {"joinedOccurrences": 1},
                            "inputs": {
                                "source": stamp(input_file),
                                "definedReadyIdentity": {"schema": "fixture"},
                            },
                            "outputs": {"table": stamp(output_file)},
                        }
                    ),
                    encoding="utf-8",
                )
                self.assertEqual(0, corpus.verify(argparse.Namespace(ready=ready)))
                output_file.write_text("poison\n", encoding="utf-8")
                with self.assertRaisesRegex(corpus.CorpusError, "does not match"):
                    corpus.verify(argparse.Namespace(ready=ready))
            finally:
                corpus.EXPECTED_SPECIMEN_SHA256 = old_expected


class RenderingTests(unittest.TestCase):
    def test_markdown_cell_escapes_html_and_table_separators(self) -> None:
        rendered = corpus.markdown_code("<tag>|value")
        self.assertEqual('<code>"&lt;tag&gt;&#124;value"</code>', rendered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
