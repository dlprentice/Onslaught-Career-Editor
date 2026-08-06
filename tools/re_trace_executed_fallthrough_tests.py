#!/usr/bin/env python3
"""Tests for tools/re_trace_executed_fallthrough.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from re_trace_executed_fallthrough import PRISTINE_SHA256, analyze  # noqa: E402


class FallthroughTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidates = [
            ROOT
            / "local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe",
            ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup",
        ]
        cls.spec = next((p for p in candidates if p.is_file()), None)
        cls.join = (
            ROOT
            / "local-lab/residual-executed-trace-callback-join-20260805-v1/JOIN.json"
        )
        if cls.spec is None or not cls.join.is_file():
            raise unittest.SkipTest("specimen/join missing")

    def test_classify_86(self):
        r = analyze(self.spec, self.join)
        self.assertEqual(r["specimen_sha256"], PRISTINE_SHA256)
        self.assertEqual(r["n_candidates"], 86)
        self.assertEqual(r["gradeCounts"].get("PROLOGUE_LIKE"), 7)
        pro = [c for c in r["candidates"] if c["fallthroughGrade"] == "PROLOGUE_LIKE"]
        self.assertTrue(all(c["shape"]["first"]["mnem"] == "sub" for c in pro))


if __name__ == "__main__":
    unittest.main()
