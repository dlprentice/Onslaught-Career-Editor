#!/usr/bin/env python3
"""Tests for tools/re_slot_consumer_static.py against pristine specimen."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from re_slot_consumer_static import (  # noqa: E402
    CANDIDATE,
    DISPATCH_REMAP,
    PRISTINE_SHA256,
    analyze,
)


class SlotConsumerStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidates = [
            ROOT
            / "local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe",
            ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup",
        ]
        cls.spec = next((p for p in candidates if p.is_file()), None)
        if cls.spec is None:
            raise unittest.SkipTest("pristine BEA not available")

    def test_dispatch_callback_contract(self):
        r = analyze(self.spec)
        self.assertEqual(r["specimen_sha256"], PRISTINE_SHA256)
        self.assertEqual(r["candidateVa"], f"0x{CANDIDATE:08x}")
        self.assertTrue(r["residualHead"]["movEaxAbs"])
        self.assertIsNotNone(r["dispatchCallThrough"])
        self.assertEqual(r["dispatchCallThrough"]["bytes"], "ff542418")
        self.assertGreaterEqual(r["nPushImmProducers"], 20)
        self.assertGreaterEqual(r["nProducersCallingDispatchRemap"], 10)
        self.assertEqual(r["staticGrade"], "STATIC_CALLBACK_ARG_TO_DISPATCH_REMAP")
        # at least one producer targets DispatchRemap
        hits = [p for p in r["producers"] if p.get("callsDispatchRemap")]
        self.assertTrue(any(p["callTarget"] == f"0x{DISPATCH_REMAP:08x}" for p in hits))


if __name__ == "__main__":
    unittest.main()
