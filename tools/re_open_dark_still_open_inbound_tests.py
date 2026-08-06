#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_still_open_inbound.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_still_open_inbound.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_still_open_inbound", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN16 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation16-code-like-mass-20260805-v1"
    / "generation-16-residual-terminal-code-like-mass"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-dark-still-open-inbound-gen16-20260805-v1"
HAS_LAB = GEN16.is_dir() and SPECIMEN.is_file()


class PolicyTests(unittest.TestCase):
    def test_align_nop_patterns(self) -> None:
        self.assertTrue(mod.is_full_align_nop_run(bytes.fromhex("8d4900")))
        self.assertTrue(mod.is_full_align_nop_run(bytes.fromhex("8bff")))
        self.assertTrue(
            mod.is_full_align_nop_run(bytes.fromhex("8da424000000008bff"))
        )
        self.assertTrue(mod.is_full_align_nop_run(bytes.fromhex("90cc00")))
        self.assertFalse(mod.is_full_align_nop_run(bytes.fromhex("8d4900e8")))
        self.assertFalse(mod.is_full_align_nop_run(b""))

    def test_proposed_is_padding(self) -> None:
        prop = mod.proposed_align_nop()
        self.assertEqual(prop["terminalState"], "TERMINAL_PADDING")
        self.assertTrue(prop["requiresQuestionSupersession"])
        self.assertNotIn("REBUILD", prop["terminalState"])


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabInboundTests(unittest.TestCase):
    def test_published_or_buildable(self) -> None:
        pre = hashlib.sha256((GEN16 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("plate missing")
        rc = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN16),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN16 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_open_dark_input"], 335)
        self.assertGreaterEqual(pack["n_proofs"], 40)
        self.assertEqual(pack["n_hard_mismatches"], 0)
        pad_n = sum(
            1
            for p in pack["proofs"]
            if p["proposed"]["terminalState"] == "TERMINAL_PADDING"
        )
        self.assertEqual(pad_n, pack["n_proofs"])


if __name__ == "__main__":
    unittest.main()
