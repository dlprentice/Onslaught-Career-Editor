#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Author-only world index and move-workflow controls."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import content_catalog_tests as fixtures
import world_edit_move as move
import world_resources_encode as encoder
import world_thing_index as index


class IndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.body = fixtures.world_body()

    def test_exact_body_metadata_and_serialized_ordinals(self) -> None:
        report = index.report_for(self.body)
        self.assertTrue(report["generatedRetailDerived"])
        self.assertEqual(report["schema"], index.SCHEMA)
        self.assertEqual(report["baseline"]["sha256"], hashlib.sha256(self.body).hexdigest())
        self.assertTrue(report["baseline"]["roundTripExact"])
        self.assertEqual(report["pagination"]["thingCount"], 5)
        self.assertEqual([row["ordinal"] for row in report["things"]], [0, 1, 2, 3, 4])
        first = report["things"][0]
        self.assertEqual((first["objectId"], first["serializedKind"], first["name"], first["definition"]),
                         (8, "unit", "Tank 1", "Tank"))
        self.assertEqual([x["value"] for x in first["position"]], [10.0, 20.0, 0.0])
        self.assertTrue(all(x["finite"] for x in first["position"]))
        self.assertIn("not runtime slots", report["scope"])
        self.assertEqual(json.loads(index.report_bytes(self.body)), report)
        self.assertEqual(index.report_bytes(self.body), index.report_bytes(self.body))

    def test_pagination_returns_original_ordinals_without_silently_losing_rows(self) -> None:
        page0 = index.report_for(self.body, start=0, limit=2)
        page1 = index.report_for(self.body, start=2, limit=2)
        page2 = index.report_for(self.body, start=4, limit=2)
        self.assertEqual([r["ordinal"] for page in (page0, page1, page2) for r in page["things"]],
                         list(range(5)))
        self.assertEqual([page["pagination"]["nextOrdinal"] for page in (page0, page1, page2)], [2, 4, None])
        self.assertEqual(index.report_for(self.body, start=5)["things"], [])
        for start, limit in ((-1, 1), (6, 1), (0, 0), (0, 129), (True, 1), (0, True)):
            with self.subTest(start=start, limit=limit), self.assertRaises(index.WorldIndexError):
                index.report_for(self.body, start=start, limit=limit)

    def test_signed_zero_and_nonfinite_bits_are_truthful(self) -> None:
        model = encoder.read_world_model(self.body)
        model["things"][0]["init"]["position"] = [-0.0, {"f32bits": "0100c07f"}, 5.5]
        body = encoder.write_world_body(model)
        positions = index.report_for(body)["things"][0]["position"]
        self.assertEqual([x["float32LittleEndianHex"] for x in positions], ["00000080", "0100c07f", "0000b040"])
        self.assertEqual([x["finite"] for x in positions], [True, False, True])
        self.assertIsNone(positions[1]["value"])
        self.assertIn(b'"value": -0.0', index.report_bytes(body))
        self.assertNotIn(b"NaN", index.report_bytes(body))

    def test_non_ascii_name_bytes_use_a_bounded_mapping_not_a_display_claim(self) -> None:
        model = encoder.read_world_model(self.body)
        model["things"][0]["init"]["name"] = "authored-\x80"
        body = encoder.write_world_body(model)
        report = index.report_for(body, start=0, limit=1)
        self.assertEqual(report["things"][0]["name"], "authored-\x80")
        self.assertIn("non-ASCII game display encoding is not established", report["nameEncoding"])
        self.assertIn(b"authored-\\u0080", index.report_bytes(body))

    def test_opaque_world_and_script_payloads_are_not_reported(self) -> None:
        model = encoder.read_world_model(self.body)
        model["scripts"][0]["code"]["symbols"][0]["value"] = "private-script-marker"
        model["influenceMap"]["nodes"] = 1
        model["influenceMap"]["nodeBytes"] = encoder.blob(b"opaqueSECRET")
        body = encoder.write_world_body(model)
        self.assertIn(b"private-script-marker", body)
        self.assertIn(b"opaqueSECRET", body)
        report = index.report_bytes(body)
        self.assertNotIn(b"private-script-marker", report)
        self.assertNotIn(b"opaqueSECRET", report)
        self.assertNotIn(b"nodeBytes", report)

    def test_selected_ordinal_and_hash_feed_the_existing_move_preview(self) -> None:
        report = index.report_for(self.body, start=0, limit=1)
        row = report["things"][0]
        self.assertEqual(row["name"], "Tank 1")
        _model, move_report = move.prepare_move(self.body, row["ordinal"], ["12.5", "-40", "3"])
        self.assertEqual(move_report["preview"]["baseline"]["sha256"], report["baseline"]["sha256"])
        self.assertTrue(move_report["reviewRequired"])

    def test_unread_or_inexact_bodies_are_refused(self) -> None:
        with self.assertRaises(index.WorldIndexError):
            index.report_for(self.body + b"\0")
        with mock.patch.object(encoder, "write_world_body", return_value=self.body + b"x"):
            with self.assertRaisesRegex(index.WorldIndexError, "does-not-round-trip"):
                index.report_for(self.body)
        with mock.patch.object(index.preview, "MAX_BODY_BYTES", len(self.body) - 1):
            with self.assertRaisesRegex(index.WorldIndexError, "input-byte-limit"):
                index.report_for(self.body)

    def test_more_than_supported_thing_count_is_refused(self) -> None:
        with mock.patch.object(index, "MAX_THINGS", 4):
            with self.assertRaisesRegex(index.WorldIndexError, "thing-count-over-editor-limit"):
                index.report_for(self.body)


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="authored-world-index-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.world = self.root / "authored.wrd"
        self.body = fixtures.world_body()
        self.world.write_bytes(self.body)

    def run_main(self, args: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = index.main(args)
            except SystemExit as error:
                rc = error.code
        return rc, out.getvalue(), err.getvalue()

    def test_selected_body_hash_pin_and_refused_legacy_output(self) -> None:
        digest = hashlib.sha256(self.body).hexdigest()
        args = [str(self.world), "--stdout", "--baseline-sha256", digest]
        rc, output, error = self.run_main(args)
        self.assertEqual(rc, 0, error)
        self.assertEqual(output.encode(), index.report_bytes(self.body))
        for extra in (["--baseline-sha256", "0" * 64], ["--out", str(self.root / "new.json")]):
            rc, output, _ = self.run_main(args + extra)
            self.assertNotEqual(rc, 0)
            self.assertEqual(output, "")
        self.assertFalse((self.root / "new.json").exists())
        self.assertEqual(self.body, self.world.read_bytes())

    def test_stdout_flag_is_explicit_and_paths_are_no_follow(self) -> None:
        rc, output, _ = self.run_main([str(self.world)])
        self.assertNotEqual(rc, 0)
        self.assertEqual(output, "")
        link = self.root / "alias.wrd"
        link.symlink_to(self.world.name)
        for source in (link, self.root / ".." / self.root.name / self.world.name):
            rc, output, _ = self.run_main([str(source), "--stdout"])
            self.assertNotEqual(rc, 0)
            self.assertEqual(output, "")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO required")
    def test_fifo_input_refuses_without_blocking(self) -> None:
        pipe = self.root / "pipe.wrd"
        os.mkfifo(pipe)
        result = subprocess.run([sys.executable, str(Path(index.__file__)), str(pipe), "--stdout"],
                                capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_source_changed_after_read_refuses_before_emitting(self) -> None:
        original = index.report_bytes
        old = self.root / "before-change.wrd"
        def replace(*args, **kwargs):
            payload = original(*args, **kwargs)
            self.world.rename(old)
            self.world.write_bytes(self.body)
            return payload
        with mock.patch.object(index, "report_bytes", side_effect=replace):
            rc, output, _ = self.run_main([str(self.world), "--stdout"])
        self.assertNotEqual(rc, 0)
        self.assertEqual(output, "")

    def test_actual_process_performs_no_write_open_with_negative_control(self) -> None:
        wrapper = """
import os, runpy, sys
def audit(event, args):
    if event == "open":
        _path, mode, flags = args
        if ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
            (isinstance(flags, int) and
             ((flags & os.O_ACCMODE) != os.O_RDONLY or flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND)))):
            raise RuntimeError("unexpected write-open")
sys.addaudithook(audit)
if os.environ.get("WORLD_INDEX_AUDIT_NEGATIVE"):
    os.open(os.environ["WORLD_INDEX_AUDIT_NEGATIVE"], os.O_WRONLY | os.O_CREAT, 0o600)
script, body = sys.argv[1:]
sys.argv = [script, body, "--stdout"]
sys.path.insert(0, os.path.dirname(script))
runpy.run_path(script, run_name="__main__")
"""
        command = [sys.executable, "-c", wrapper, str(Path(index.__file__)), str(self.world)]
        env = dict(os.environ)
        env.pop("WORLD_INDEX_AUDIT_NEGATIVE", None)
        env.pop("PYTHONDONTWRITEBYTECODE", None)  # CLI itself must suppress import bytecode writes.
        before = {p.relative_to(self.root) for p in self.root.rglob("*")}
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.encode(), index.report_bytes(self.body))
        self.assertEqual(before, {p.relative_to(self.root) for p in self.root.rglob("*")})
        target = self.root / "should-not-be-created"
        env["WORLD_INDEX_AUDIT_NEGATIVE"] = str(target)
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected write-open", result.stderr)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
