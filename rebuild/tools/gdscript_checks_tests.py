#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the golden admission in gdscript_checks.py (no Godot needed)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gdscript_checks  # noqa: E402


class GoldenAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = Path(tempfile.mkdtemp(prefix="gdscript-checks-tests-"))
        (self.directory / "a.fixture").write_bytes(b"alpha")
        (self.directory / "b.json").write_bytes(b"{}")
        files = {name: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                 for name, data in (("a.fixture", b"alpha"), ("b.json", b"{}"))}
        manifest = json.dumps({"schema": "onslaught-rebuild-goldens.v1", "generatedFrom": "abc", "files": files}).encode()
        (self.directory / "manifest.json").write_bytes(manifest)
        self.pin = mock.patch.object(gdscript_checks, "GOLDENS_MANIFEST_SHA256", hashlib.sha256(manifest).hexdigest())
        self.pin.start()

    def tearDown(self) -> None:
        self.pin.stop()
        for path in sorted(self.directory.iterdir(), reverse=True):
            path.unlink()
        self.directory.rmdir()

    def test_pinned_goldens_are_admitted(self) -> None:
        self.assertEqual("abc", gdscript_checks.verify_goldens(self.directory)["generatedFrom"])

    def test_changed_manifest_is_refused(self) -> None:
        with (self.directory / "manifest.json").open("ab") as manifest:
            manifest.write(b" ")
        with self.assertRaisesRegex(RuntimeError, "manifest is missing or changed"):
            gdscript_checks.verify_goldens(self.directory)

    def test_same_size_changed_golden_is_refused(self) -> None:
        (self.directory / "a.fixture").write_bytes(b"alphA")
        with self.assertRaisesRegex(RuntimeError, "golden changed"):
            gdscript_checks.verify_goldens(self.directory)

    def test_missing_golden_is_refused(self) -> None:
        (self.directory / "b.json").unlink()
        with self.assertRaisesRegex(RuntimeError, "golden is missing"):
            gdscript_checks.verify_goldens(self.directory)
        (self.directory / "b.json").write_bytes(b"{}")

    def test_linked_golden_is_refused(self) -> None:
        target = self.directory / "b.json"
        target.rename(self.directory / "b.real")
        (self.directory / "b.json").symlink_to(self.directory / "b.real")
        with self.assertRaisesRegex(RuntimeError, "golden is missing"):
            gdscript_checks.verify_goldens(self.directory)
        (self.directory / "b.json").unlink()
        (self.directory / "b.real").rename(target)

    def test_only_the_named_diagnostics_are_expected(self) -> None:
        self.assertEqual({"pause_scene_checks": ("core/io/stream_peer_gzip.cpp",),
                          "world_presentation": ("look_at() failed",)}, gdscript_checks.EXPECTED_ENGINE_ERRORS)


if __name__ == "__main__":
    unittest.main()
