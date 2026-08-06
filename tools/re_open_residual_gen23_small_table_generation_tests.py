#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen23_small_table_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen23_small_table_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen23_small_table_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN23 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation23-partial-data-20260805-v1"
    / "generation-23-residual-terminal-partial-data"
)
GEN24 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation24-small-table-20260805-v1"
    / "generation-24-residual-terminal-small-table"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen23-small-table-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN23.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 47)
        self.assertEqual(mod.EXPECTED_DATA_ADDED, 2)
        self.assertEqual(mod.EXPECTED_AMBIG_ADDED, 45)
        self.assertEqual(mod.EXPECTED_DARK_CLOSED, 47)
        self.assertEqual(mod.EXPECTED_EXEC_CLOSED, 0)
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 78)
        self.assertEqual(mod.EXPECTED_DATA, 29)
        self.assertEqual(mod.EXPECTED_AMBIG, 944)
        self.assertEqual(mod.ADVANCE_KIND, "RESIDUAL_TERMINAL_OPEN_SMALL_TABLE")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN24 / "campaign.ready.json").is_file():
            self.skipTest("Gen24 not applied yet")
        pre = hashlib.sha256((GEN23 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN24),
                "--parent",
                str(GEN23),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN23 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN24 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 24)
        self.assertEqual(ready["counts"]["residualOpenDark"], 78)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 4)
        self.assertEqual(ready["counts"]["residualTerminalData"], 29)
        self.assertEqual(ready["counts"]["residualTerminalBoundedAmbiguity"], 944)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 47)
        self.assertEqual(ready["counts"]["terminalDataAddedThisGeneration"], 2)
        self.assertEqual(
            ready["counts"]["terminalBoundedAmbiguityAddedThisGeneration"], 45
        )
        self.assertEqual(
            (ready.get("advance") or {}).get("kind"),
            "RESIDUAL_TERMINAL_OPEN_SMALL_TABLE",
        )


if __name__ == "__main__":
    unittest.main()
