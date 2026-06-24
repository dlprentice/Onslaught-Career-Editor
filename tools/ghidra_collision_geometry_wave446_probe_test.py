#!/usr/bin/env python3
"""Unit tests for the Wave446 collision/geometry focused probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_collision_geometry_wave446_probe as probe


class Wave446ProbeTests(unittest.TestCase):
    def test_target_count_matches_wave_scope(self) -> None:
        self.assertEqual(len(probe.TARGETS), 8)
        self.assertIn("0x00477ba0", probe.TARGETS)
        self.assertIn("0x004ac6e0", probe.TARGETS)
        self.assertIn("0x004ad830", probe.TARGETS)

    def test_vec3_magnitude_squared_supersedes_stale_name(self) -> None:
        spec = probe.TARGETS["0x00477ba0"]
        self.assertEqual(spec["name"], "Vec3__MagnitudeSquared")
        self.assertIn("renamed", spec["tags"])
        self.assertIn("Geometry__NoOpHook", spec["commentTokens"])

    def test_normalize_address(self) -> None:
        self.assertEqual(probe.normalize_address("00477ba0"), "0x00477ba0")
        self.assertEqual(probe.normalize_address("0x4ad830"), "0x004ad830")
        self.assertEqual(probe.normalize_address("<no_function>"), "<no_function>")

    def test_parse_summary(self) -> None:
        text = "SUMMARY updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
        self.assertEqual(probe.parse_summary(text), probe.EXPECTED_VERIFY_DRY)

    def test_missing_base_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status, failures = probe.run_checks(Path(tmp) / "missing")
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("base directory missing" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
