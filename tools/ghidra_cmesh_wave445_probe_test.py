#!/usr/bin/env python3
"""Unit tests for the Wave445 CMesh/MeshCollisionVolume focused probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cmesh_wave445_probe as probe


class Wave445ProbeTests(unittest.TestCase):
    def test_target_count_matches_wave_scope(self) -> None:
        self.assertEqual(len(probe.TARGETS), 9)
        self.assertIn("0x004aab90", probe.TARGETS)
        self.assertIn("0x004acde0", probe.TARGETS)
        self.assertIn("0x004ae0d0", probe.TARGETS)

    def test_contact_output_signature_remains_deferred(self) -> None:
        spec = probe.TARGETS["0x004acde0"]
        self.assertEqual(spec["signature"], "undefined CMeshCollisionVolume__InitContactOutputRecord(void)")
        self.assertIn("signature-deferred", spec["tags"])

    def test_normalize_address(self) -> None:
        self.assertEqual(probe.normalize_address("004aab90"), "0x004aab90")
        self.assertEqual(probe.normalize_address("0x4acde0"), "0x004acde0")
        self.assertEqual(probe.normalize_address("<no_function>"), "<no_function>")

    def test_parse_summary(self) -> None:
        text = "SUMMARY updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
        self.assertEqual(probe.parse_summary(text), probe.EXPECTED_VERIFY_DRY)

    def test_missing_base_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            status, failures = probe.run_checks(missing)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("base directory missing" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
