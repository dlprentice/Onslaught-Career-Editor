#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_remaining_frontier.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_remaining_frontier.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_remaining_frontier", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN14 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation14-code-envelope-20260805-v1"
    / "generation-14-residual-terminal-code-envelope"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-dark-remaining-frontier-gen14-20260805-v1"
HAS_LAB = GEN14.is_dir() and SPECIMEN.is_file()


class PolicyTests(unittest.TestCase):
    def test_pad_vs_code_proposal(self) -> None:
        pad = mod.proposed_for_kinds(["TINY_PAD_GAP"])
        self.assertEqual(pad["terminalState"], "TERMINAL_PADDING")
        code = mod.proposed_for_kinds(["STATIC_CODE_DECODE_ENVELOPE"])
        self.assertEqual(code["terminalState"], "TERMINAL_BOUNDED_AMBIGUITY")
        mixed = mod.proposed_for_kinds(
            ["CODE_ADDRESS_TABLE_PREFIX", "ALIGN_PAD_PREFIX"]
        )
        self.assertEqual(mixed["terminalState"], "TERMINAL_BOUNDED_AMBIGUITY")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabFrontierTests(unittest.TestCase):
    def test_published_plate(self) -> None:
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("plate missing")
        pre = hashlib.sha256((GEN14 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN14),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc, 0)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertGreaterEqual(pack["n_proofs"], 8)
        # all 8 original multi present
        starts = {p["startVa"].lower() for p in pack["proofs"]}
        for va in (
            "0x005351c4",
            "0x005885d6",
            "0x0059f161",
            "0x005aa424",
            "0x005afc88",
            "0x005b0c97",
            "0x005b37a5",
            "0x005b42d7",
        ):
            self.assertIn(va.lower(), starts)
        # no pad terminal with code envelope kind
        for p in pack["proofs"]:
            if p["proposed"]["terminalState"] == "TERMINAL_PADDING":
                self.assertNotIn("STATIC_CODE_DECODE_ENVELOPE", p.get("subspanKinds") or "")
        self.assertEqual(
            pre,
            hashlib.sha256((GEN14 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
        )
        integrity = json.loads((PLATE / "INTEGRITY.json").read_text(encoding="utf-8"))
        self.assertTrue(all(integrity["checks"].values()))


if __name__ == "__main__":
    unittest.main()
