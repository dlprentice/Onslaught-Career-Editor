# SPDX-License-Identifier: GPL-3.0-only
"""Authored compiled-script fixtures only; never reads game assets or runs a VM."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import mission_script_inspect as ms


def i32(*values):
    return struct.pack("<" + "i" * len(values), *values)


def text(value):
    return i32(len(value)) + value


def symbol(name, kind=3, value=b"literal event text", index=0):
    body = b"" if kind == 0 else text(value) if kind == 3 else value
    return text(name) + i32(kind) + body + i32(kind, index, 0x12345678)


def script(*, instructions=((5, 0), (23, 0)), names=None, events=None, functions=None, unknown=(37, -99)):
    names = [symbol(b"event_name")] if names is None else names
    events = [0] + [-1] * 12 if events is None else events
    functions = [(1, [0])] if functions is None else functions
    return (i32(len(instructions)) + b"".join(i32(*row) for row in instructions) + i32(*events)
            + i32(len(names)) + b"".join(names) + i32(len(names), len(functions))
            + b"".join(i32(pc, len(params), *params) for pc, params in functions) + i32(*unknown))


def inspect(data, **kwargs):
    offset = kwargs.get("offset", 0)
    length = kwargs.get("length", len(data) - offset)
    return ms.inspect_script(data, source_sha256=hashlib.sha256(data).hexdigest(),
                             record_sha256=hashlib.sha256(data[offset:offset+length]).hexdigest(), **kwargs)


class ScriptInspectionTests(unittest.TestCase):
    def test_complete_structure_and_custom_event_symbol_join(self):
        raw = script()
        row = inspect(raw)
        self.assertEqual(row["status"], "complete")
        self.assertEqual((row["declaredInstructionCount"], row["supportedInstructionCount"]), (2, 2))
        self.assertEqual(row["opcodeCounts"], {"5": 1, "23": 1})
        self.assertEqual(len(row["eventEntryPcs"]), 13)
        self.assertEqual(row["symbols"][0]["name"]["identifier"], "event_name")
        ref = row["eventFunctions"][0]["parameterReferences"][0]
        self.assertEqual((ref["status"], ref["symbolOrdinal"]), ("resolved-string", 0))
        self.assertEqual(ref["eventNameIdentity"]["sha256"], hashlib.sha256(b"literal event text").hexdigest())
        self.assertEqual(row["unparsedRange"]["length"], 0)
        self.assertEqual(row["findings"], [])

    def test_exact_selected_record_range_is_not_found_by_scanning(self):
        raw = b"AUTHORED_PREFIX" + script() + b"AUTHORED_SUFFIX"
        row = inspect(raw, offset=15, length=len(script()))
        self.assertEqual(row["status"], "complete")
        self.assertEqual(row["recordIdentity"]["offset"], 15)
        self.assertEqual(row["parsedRange"], row["recordIdentity"])

    def test_literal_values_operands_and_payload_arrays_are_not_emitted(self):
        secret = b"AUTHORED_LITERAL_SENTINEL_MUST_NOT_APPEAR"
        raw = script(names=[symbol(b"event_name", value=secret)])
        encoded = json.dumps(inspect(raw))
        self.assertNotIn(secret.decode(), encoded)
        self.assertNotIn("attribute", encoded)

    def test_unknown_trailing_words_preserve_exact_range_hash(self):
        raw = script(unknown=(-100, 888))
        row = inspect(raw)
        unknown = row["unknownFields"][0]
        self.assertEqual((unknown["offset"], unknown["length"]), (len(raw)-8, 8))
        self.assertEqual(unknown["sha256"], hashlib.sha256(i32(-100, 888)).hexdigest())

    def test_nonempty_suffix_is_explicit_not_silently_accepted(self):
        raw = script() + b"opaque extension"
        row = inspect(raw)
        self.assertEqual(row["status"], "trailing-data")
        self.assertEqual(row["unparsedRange"]["sha256"], hashlib.sha256(b"opaque extension").hexdigest())

    def test_unknown_opcode_preserves_unparsed_identity_without_guessing(self):
        raw = script(instructions=((5, 0), (77, 123)))
        row = inspect(raw)
        self.assertEqual(row["status"], "unsupported")
        self.assertEqual(row["supportedInstructionCount"], 1)
        self.assertEqual(row["unparsedRange"]["offset"], 12)
        self.assertEqual(row["findings"][-1]["code"], "unknown-opcode-layout")

    def test_unknown_value_layout_stops_at_type_word(self):
        raw = script(names=[text(b"mystery") + i32(99) + b"unknown value"])
        row = inspect(raw)
        self.assertEqual(row["status"], "unsupported")
        self.assertEqual(row["symbols"], [])
        self.assertEqual(row["findings"][-1]["code"], "unknown-symbol-value-layout")
        self.assertEqual(raw[row["unparsedRange"]["offset"]:][:4], i32(99))

    def test_all_supported_value_types_are_consumed_without_value_conversion(self):
        symbols = [symbol(b"empty", 0), symbol(b"integer", 1, i32(-5)), symbol(b"float", 2, bytes.fromhex("0000c07f")),
                   symbol(b"string", 3, b"authored"), symbol(b"boolean", 4, i32(255)),
                   symbol(b"thing", 5, i32(12345)), symbol(b"position", 6, i32(1, 2, 3))]
        row = inspect(script(names=symbols, functions=[]))
        self.assertEqual(row["status"], "complete")
        self.assertEqual([s["value"]["storedType"] for s in row["symbols"]], list(range(7)))

    def test_duplicate_cstring_names_keep_every_stored_identity(self):
        raw = script(names=[symbol(b"same\0one"), symbol(b"same\0two")])
        row = inspect(raw)
        self.assertEqual(len(row["symbols"]), 2)
        self.assertNotEqual(row["symbols"][0]["name"]["sha256"], row["symbols"][1]["name"]["sha256"])
        self.assertEqual(row["findings"][0], {"code": "duplicate-cstring-symbol-name", "symbolOrdinal": 1, "firstOrdinal": 0})

    def test_nonascii_or_nonidentifier_names_are_preserved_by_hash(self):
        name = b"not identifier\xff"
        row = inspect(script(names=[symbol(name)]))
        meta = row["symbols"][0]["name"]
        self.assertIsNone(meta["identifier"])
        self.assertEqual(meta["sha256"], hashlib.sha256(name).hexdigest())

    def test_invalid_entry_points_and_event_references_are_findings_not_repairs(self):
        row = inspect(script(names=[symbol(b"not_string", 0)], events=[-2] + [-1]*12, functions=[(999, [-1, 0, 50])]))
        self.assertEqual(row["status"], "complete")
        self.assertEqual(row["eventEntryPcs"][0]["entryPc"], -2)
        self.assertEqual([r["status"] for r in row["eventFunctions"][0]["parameterReferences"]],
                         ["invalid-reference", "non-string-value", "invalid-reference"])
        self.assertEqual(len(row["findings"]), 5)

    def test_every_truncated_prefix_is_rejected(self):
        raw = script()
        for length in range(1, len(raw)):
            with self.subTest(length=length):
                self.assertNotEqual(inspect(raw[:length])["status"], "complete")

    def test_negative_and_oversized_counts_are_distinct(self):
        self.assertEqual(inspect(i32(-1))["status"], "malformed")
        row = inspect(i32(2**31-1))
        self.assertEqual(row["status"], "unsupported")
        self.assertEqual(row["findings"][-1]["code"], "profile-limit-instruction-count")

    def test_count_and_string_budgets_refuse_before_unbounded_loops(self):
        row = inspect(script(), limits=ms.Limits(instructions=1))
        self.assertEqual(row["status"], "unsupported")
        row = inspect(script(), limits=ms.Limits(string_bytes=3))
        self.assertEqual(row["status"], "unsupported")
        row = inspect(script(), limits=ms.Limits(total_string_bytes=12))
        self.assertEqual(row["status"], "unsupported")
        row = inspect(script(functions=[(1, [0, 0]), (1, [0])]), limits=ms.Limits(total_parameters=2))
        self.assertEqual(row["status"], "unsupported")

    def test_duplicate_reporting_is_linear_in_symbol_count(self):
        row = inspect(script(names=[symbol(b"same", 0)]*3000, functions=[]))
        self.assertEqual(row["status"], "complete")
        self.assertEqual(len(row["findings"]), 2999)
        self.assertLess(len(json.dumps(row)), 2_500_000)

    def test_identity_limits_and_invocation_checks(self):
        raw = script()
        with self.assertRaises(ms.InspectionError):
            ms.inspect_script(raw, source_sha256="0"*64, record_sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaises(ms.InspectionError):
            ms.inspect_script(raw, source_sha256=hashlib.sha256(raw).hexdigest(), record_sha256="0"*64)
        with self.assertRaises(TypeError):
            ms.inspect_script(bytearray(raw), source_sha256="0"*64, record_sha256="0"*64)
        for kwargs in ({"offset": -1}, {"offset": True}, {"length": 0}, {"length": len(raw)+1}):
            with self.assertRaises((ms.InspectionError, TypeError)):
                inspect(raw, **kwargs)
        with self.assertRaises(ms.InspectionError):
            inspect(raw, limits=ms.Limits(source_bytes=16))
        for kwargs in ({"instructions": 65537}, {"symbols": True}):
            with self.assertRaises(ValueError):
                ms.Limits(**kwargs)


class HeldSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "脚本.bin"
        self.raw = script()
        self.path.write_bytes(self.raw)
        self.kwargs = dict(source_sha256=hashlib.sha256(self.raw).hexdigest(), record_sha256=hashlib.sha256(self.raw).hexdigest())

    def test_regular_unicode_source(self):
        self.assertEqual(ms.inspect_file(self.path, **self.kwargs)["status"], "complete")

    def test_final_and_ancestor_links_and_fifo_are_refused(self):
        link = self.root / "link"
        link.symlink_to(self.path)
        directory = self.root / "alias"
        directory.symlink_to(self.root)
        fifo = self.root / "fifo"
        os.mkfifo(fifo)
        for path in (link, directory/self.path.name, fifo):
            with self.subTest(path=path), self.assertRaises((OSError, ms.InspectionError)):
                ms.inspect_file(path, **self.kwargs)

    def test_cap_is_checked_before_payload_read(self):
        with patch.object(ms.os, "read", side_effect=AssertionError("must not read")):
            with self.assertRaises(ms.InspectionError):
                ms.inspect_file(self.path, limits=ms.Limits(source_bytes=1), **self.kwargs)

    def test_changed_source_during_parse_is_refused(self):
        original = ms.inspect_script
        before = self.path.stat()
        def change(*args, **kwargs):
            result = original(*args, **kwargs)
            self.path.write_bytes(self.raw[:-1] + b"X")
            os.utime(self.path, ns=(before.st_atime_ns, before.st_mtime_ns))
            return result
        with patch.object(ms, "inspect_script", side_effect=change), self.assertRaises(ms.InspectionError):
            ms.inspect_file(self.path, **self.kwargs)

    def test_cli_reports_complete_trailing_and_identity_refusal_without_writing(self):
        arguments = [str(self.path), "--source-sha256", self.kwargs["source_sha256"],
                     "--record-sha256", self.kwargs["record_sha256"]]
        names_before = sorted(p.name for p in self.root.iterdir())
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(ms.main(arguments), 0)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "complete")
        self.path.write_bytes(self.raw + b"extension")
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(ms.main([str(self.path), "--source-sha256", digest, "--record-sha256", digest]), 1)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "trailing-data")
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(ms.main(arguments), 2)
        self.assertIn("identity-mismatch", stderr.getvalue())
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), names_before)

    def test_same_bytes_path_replacement_is_refused(self):
        original = ms.inspect_script
        replacement = self.root / "replacement"
        replacement.write_bytes(self.raw)
        def change(*args, **kwargs):
            result = original(*args, **kwargs)
            replacement.replace(self.path)
            return result
        with patch.object(ms, "inspect_script", side_effect=change), self.assertRaises(ms.InspectionError):
            ms.inspect_file(self.path, **self.kwargs)


if __name__ == "__main__":
    unittest.main()
