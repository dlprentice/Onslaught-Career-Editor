#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen17_table_align_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen17_table_align_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen17_table_align_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN17 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation17-still-open-inbound-20260805-v1"
    / "generation-17-residual-terminal-still-open-inbound"
)
GEN18 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation18-table-align-executed-20260805-v1"
    / "generation-18-residual-terminal-table-align-executed"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen17-table-align-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN17.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_expected_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 37)
        self.assertEqual(mod.EXPECTED_TABLE, 30)
        self.assertEqual(mod.EXPECTED_EXEC, 7)
        self.assertEqual(mod.ADVANCE_KIND, "RESIDUAL_TERMINAL_OPEN_TABLE_ALIGN_EXECUTED")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN18 / "campaign.ready.json").is_file():
            self.skipTest("Gen18 not applied yet")
        pre = hashlib.sha256((GEN17 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN18),
                "--parent",
                str(GEN17),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN17 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN18 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 18)
        self.assertEqual(ready["counts"]["residualOpenDark"], 255)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 101)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 676)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 37)


if __name__ == "__main__":
    unittest.main()
