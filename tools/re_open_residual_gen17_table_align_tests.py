#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen17_table_align.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen17_table_align.py"
SPEC = importlib.util.spec_from_file_location("re_open_residual_gen17_table_align", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN17 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation17-still-open-inbound-20260805-v1"
    / "generation-17-residual-terminal-still-open-inbound"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PROLOGUE = ROOT / "local-lab" / "ttd-call-context-prologue-like-20260805-v1"
PLATE = ROOT / "local-lab" / "open-residual-gen17-table-align-20260805-v1"
HAS_LAB = GEN17.is_dir() and SPECIMEN.is_file() and PROLOGUE.is_dir()


class PolicyTests(unittest.TestCase):
    def test_expected_inputs(self) -> None:
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 285)
        self.assertEqual(mod.EXPECTED_OPEN_EXECUTED, 108)
        self.assertEqual(
            mod.ADVANCE_KIND, "RESIDUAL_TERMINAL_OPEN_TABLE_ALIGN_EXECUTED.v1"
        )

    def test_proposed_terminals(self) -> None:
        t = mod.proposed_table(["MSVC_ALIGN_NOP_RUN", "CODE_ADDRESS_TABLE_PREFIX"])
        self.assertEqual(t["terminalState"], "TERMINAL_BOUNDED_AMBIGUITY")
        e = mod.proposed_exec()
        self.assertEqual(e["terminalState"], "TERMINAL_BOUNDED_AMBIGUITY")
        self.assertTrue(e["requiresQuestionSupersession"])


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabPlateTests(unittest.TestCase):
    def test_published_plate(self) -> None:
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("plate missing")
        pre = hashlib.sha256((GEN17 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN17),
                "--specimen",
                str(SPECIMEN),
                "--prologue-dir",
                str(PROLOGUE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN17 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_open_dark_input"], 285)
        self.assertEqual(pack["n_open_executed_input"], 108)
        self.assertGreaterEqual(pack["n_table_align_proofs"], 20)
        self.assertEqual(pack["n_executed_prologue_proofs"], 7)
        self.assertEqual(pack["n_hard_mismatches"], 0)
        for p in pack["proofs"]:
            self.assertEqual(p["proposed"]["terminalState"], "TERMINAL_BOUNDED_AMBIGUITY")


if __name__ == "__main__":
    unittest.main()
