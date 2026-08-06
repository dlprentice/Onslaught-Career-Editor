#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen22_partial_data_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen22_partial_data_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen22_partial_data_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN22 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation22-data-shape-20260805-v1"
    / "generation-22-residual-terminal-data-shape"
)
GEN23 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation23-partial-data-20260805-v1"
    / "generation-23-residual-terminal-partial-data"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen22-partial-data-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN22.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 10)
        self.assertEqual(mod.EXPECTED_AMBIG_ADDED, 10)
        self.assertEqual(mod.EXPECTED_DARK_CLOSED, 10)
        self.assertEqual(mod.EXPECTED_EXEC_CLOSED, 0)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN23 / "campaign.ready.json").is_file():
            self.skipTest("Gen23 not applied yet")
        pre = hashlib.sha256((GEN22 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN23),
                "--parent",
                str(GEN22),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN22 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN23 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 23)
        self.assertEqual(ready["counts"]["residualOpenDark"], 125)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 4)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 899)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 10)


if __name__ == "__main__":
    unittest.main()
