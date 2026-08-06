#!/usr/bin/env python3
"""Tests for tools/re_abs_ptr_live_static.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from re_abs_ptr_live_static import PRISTINE_SHA256, analyze  # noqa: E402


class AbsPtrStaticTests(unittest.TestCase):
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
            raise unittest.SkipTest("specimen or join missing")

    def test_classify_14(self):
        r = analyze(self.spec, self.join)
        self.assertEqual(r["specimen_sha256"], PRISTINE_SHA256)
        self.assertEqual(r["n_candidates"], 14)
        self.assertIn("STATIC_JMP_OR_DATA_TABLE_PTR", r["gradeCounts"])
        c = next(x for x in r["candidates"] if x["startVa"] == "0x00454169")
        self.assertEqual(c["staticGrade"], "STATIC_JMP_OR_DATA_TABLE_PTR")
        self.assertEqual(c["hits"][0]["form"], "TEXT_DWORD_TABLE")


if __name__ == "__main__":
    unittest.main()
