#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen20_code_pad_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen20_code_pad_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen20_code_pad_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN20 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation20-multi-unit-20260805-v1"
    / "generation-20-residual-terminal-multi-unit"
)
GEN21 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation21-code-pad-20260805-v1"
    / "generation-21-residual-terminal-code-pad"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen20-code-pad-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN20.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 6)
        self.assertEqual(mod.EXPECTED_DARK, 5)
        self.assertEqual(mod.EXPECTED_EXEC, 1)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN21 / "campaign.ready.json").is_file():
            self.skipTest("Gen21 not applied yet")
        pre = hashlib.sha256((GEN20 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN21),
                "--parent",
                str(GEN20),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN20 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN21 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 21)
        self.assertEqual(ready["counts"]["residualOpenDark"], 166)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 4)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 862)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 6)


if __name__ == "__main__":
    unittest.main()
