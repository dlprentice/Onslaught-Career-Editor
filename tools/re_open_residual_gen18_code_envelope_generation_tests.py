#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen18_code_envelope_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen18_code_envelope_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen18_code_envelope_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN18 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation18-table-align-executed-20260805-v1"
    / "generation-18-residual-terminal-table-align-executed"
)
GEN19 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation19-code-envelope-20260805-v1"
    / "generation-19-residual-terminal-code-envelope"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen18-code-envelope-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN18.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 112)
        self.assertEqual(mod.EXPECTED_DARK, 20)
        self.assertEqual(mod.EXPECTED_EXEC, 92)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN19 / "campaign.ready.json").is_file():
            self.skipTest("Gen19 not applied yet")
        pre = hashlib.sha256((GEN18 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN19),
                "--parent",
                str(GEN18),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN18 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN19 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 19)
        self.assertEqual(ready["counts"]["residualOpenDark"], 235)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 9)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 788)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 112)


if __name__ == "__main__":
    unittest.main()
