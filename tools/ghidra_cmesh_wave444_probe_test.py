#!/usr/bin/env python3
"""Unit tests for the Wave444 CMesh focused probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cmesh_wave444_probe as probe


class Wave444ProbeTests(unittest.TestCase):
    def test_target_count_matches_wave_scope(self) -> None:
        self.assertEqual(len(probe.TARGETS), 11)
        self.assertIn("0x004aa630", probe.TARGETS)
        self.assertIn("0x004aa940", probe.TARGETS)

    def test_normalize_address(self) -> None:
        self.assertEqual(probe.normalize_address("004aa630"), "0x004aa630")
        self.assertEqual(probe.normalize_address("0x4aa630"), "0x004aa630")
        self.assertEqual(probe.normalize_address("<none>"), "<none>")

    def test_parse_summary(self) -> None:
        text = "SUMMARY updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
        self.assertEqual(probe.parse_summary(text), probe.EXPECTED_VERIFY_DRY)

    def test_missing_base_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            status, failures = probe.run_checks(missing)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("base directory missing" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
