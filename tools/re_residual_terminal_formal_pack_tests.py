#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK = (
    ROOT
    / "local-lab"
    / "residual-terminal-formal-pack-padding-20260805-v1"
    / "FORMAL-PACK.json"
)
SUMMARY = PACK.with_name("SUMMARY.json")


@unittest.skipUnless(PACK.is_file(), "formal pack plate missing")
class ResidualTerminalFormalPackTests(unittest.TestCase):
    def test_pack_ready_for_generation(self) -> None:
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        self.assertEqual("READY_FOR_GENERATION", pack["status"])
        self.assertEqual(5012, pack["n_proofs"])
        self.assertEqual(0, pack["n_mismatches"])
        self.assertEqual(4997, pack["n_require_question_supersession"])
        self.assertEqual(15, pack["n_already_clean"])
        self.assertTrue(pack["specimen_sha256"].startswith("74154bfae14ddc8e"))
        p0 = pack["proofs"][0]
        self.assertEqual(64, len(p0["peBytesSha256"]))
        self.assertIn(p0["kind"], {"NOP_PADDING", "INT3_PADDING", "ZERO_PADDING"})

    def test_summary_matches_pack(self) -> None:
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(pack["n_proofs"], summary["n_proofs"])
        self.assertEqual(pack["status"], summary["status"])


if __name__ == "__main__":
    unittest.main()
