#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen26 unit-split generation reducer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen26_unit_split_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen26_unit_split_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

PARENT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation25-police-reopen-20260805-v1"
    / "generation-25-residual-terminal-police-reopen"
)
OUT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation26-unit-split-20260805-v1"
    / "generation-26-residual-terminal-unit-split"
)
PACK = ROOT / "local-lab" / "open-residual-gen26-unit-split-20260805-v1" / "FORMAL-PACK.json"
HAS_LAB = PARENT.is_dir()


class ConstantsTests(unittest.TestCase):
    def test_partition_math(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 5)
        self.assertEqual(mod.EXPECTED_DARK, 1)
        self.assertEqual(mod.EXPECTED_EXEC, 4)
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 98)
        self.assertEqual(mod.EXPECTED_OPEN_EXEC, 0)
        self.assertEqual(mod.EXPECTED_AMBIG, 928)
        self.assertEqual(len(mod.EXPECTED_PROOF_STARTS), 5)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGen26Tests(unittest.TestCase):
    def test_merge_apply_verify_parent_unmutated(self) -> None:
        pre = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "merge-pack",
                "--parent",
                str(PARENT),
                "--out",
                str(PACK),
            ]
        )
        self.assertEqual(rc, 0)
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 5)
        self.assertEqual(pack["n_dark_proofs"], 1)
        self.assertEqual(pack["n_executed_proofs"], 4)

        rc2 = mod.main(
            [
                "apply",
                "--parent",
                str(PARENT),
                "--formal-pack",
                str(PACK),
                "--out",
                str(OUT),
            ]
        )
        self.assertEqual(rc2, 0)
        post = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post, "Gen25 parent must stay unmutated")

        ready = json.loads((OUT / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 26)
        self.assertEqual(ready["counts"]["residualOpenDark"], 98)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 0)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 928)
        self.assertEqual(ready["counts"]["openExecutedClosedThisGeneration"], 4)
        self.assertEqual(ready["counts"]["openDarkClosedThisGeneration"], 1)

        rc3 = mod.main(
            [
                "verify",
                "--campaign",
                str(OUT),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(PARENT),
            ]
        )
        self.assertEqual(rc3, 0)
        post2 = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post2)


if __name__ == "__main__":
    unittest.main()
