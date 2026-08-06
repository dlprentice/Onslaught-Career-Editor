#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen19_multi_unit_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen19_multi_unit_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen19_multi_unit_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN19 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation19-code-envelope-20260805-v1"
    / "generation-19-residual-terminal-code-envelope"
)
GEN20 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation20-multi-unit-20260805-v1"
    / "generation-20-residual-terminal-multi-unit"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen19-multi-unit-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN19.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 68)
        self.assertEqual(mod.EXPECTED_DARK, 64)
        self.assertEqual(mod.EXPECTED_EXEC, 4)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN20 / "campaign.ready.json").is_file():
            self.skipTest("Gen20 not applied yet")
        pre = hashlib.sha256((GEN19 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN20),
                "--parent",
                str(GEN19),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN19 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN20 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 20)
        self.assertEqual(ready["counts"]["residualOpenDark"], 171)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 5)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 856)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 68)


if __name__ == "__main__":
    unittest.main()
