#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen27 OPEN_DARK unit-split instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen27_open_dark_unit_split.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen27_open_dark_unit_split", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN27 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation27-tiny-fragment-20260805-v1"
    / "generation-27-residual-terminal-tiny-fragment"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen27-open-dark-unit-split-20260805-v1"
HAS_LAB = GEN27.is_dir() and SPECIMEN.is_file()


class ConstantsTests(unittest.TestCase):
    def test_expected(self) -> None:
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 82)
        self.assertEqual(mod.EXPECTED_OPEN_EXECUTED, 0)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabOpenDarkUnitSplitTests(unittest.TestCase):
    def test_build_verify_ready_24(self) -> None:
        pre = hashlib.sha256((GEN27 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN27),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN27 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 24)
        self.assertEqual(pack["n_open_dark_input"], 82)
        self.assertTrue(pack.get("hold_generation_apply"))
        lanes = pack["recoveryLaneCounts"]
        self.assertEqual(lanes.get("JMP_OVER_FRAGMENT"), 23)
        self.assertEqual(lanes.get("SWITCH_CASE_ENTRY"), 1)
        self.assertGreaterEqual(pack.get("n_police_envelope_hold", 0), 17)
        # no envelope-only proofs
        for p in pack["proofs"]:
            self.assertIn(
                p["recoveryLane"],
                {"JMP_OVER_FRAGMENT", "PREV_INSN_SPAN", "SWITCH_CASE_ENTRY"},
            )
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN27),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)
        post2 = hashlib.sha256((GEN27 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post2)


if __name__ == "__main__":
    unittest.main()
