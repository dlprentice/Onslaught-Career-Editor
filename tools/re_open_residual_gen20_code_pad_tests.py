#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen20_code_pad.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen20_code_pad.py"
SPEC = importlib.util.spec_from_file_location("re_open_residual_gen20_code_pad", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN20 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation20-multi-unit-20260805-v1"
    / "generation-20-residual-terminal-multi-unit"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen20-code-pad-20260805-v1"
HAS_LAB = GEN20.is_dir() and SPECIMEN.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 171)
        self.assertEqual(mod.EXPECTED_OPEN_EXECUTED, 5)
        self.assertEqual(mod.ADVANCE_KIND, "RESIDUAL_TERMINAL_OPEN_CODE_PAD.v1")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabPlateTests(unittest.TestCase):
    def test_published_plate(self) -> None:
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("plate missing")
        pre = hashlib.sha256((GEN20 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN20),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN20 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_hard_mismatches"], 0)
        self.assertGreaterEqual(pack["n_proofs"], 5)
        self.assertGreaterEqual(pack["n_dark_proofs"], 4)
        self.assertGreaterEqual(pack["n_executed_proofs"], 1)
        for p in pack["proofs"]:
            self.assertEqual(p["proposed"]["terminalState"], "TERMINAL_BOUNDED_AMBIGUITY")
            if p["recoveryLane"] == "SOFT_MULTI_UNIT_EXECUTED":
                self.assertEqual(p["sourceState"], "OPEN_EXECUTED_RESIDUAL")


if __name__ == "__main__":
    unittest.main()
