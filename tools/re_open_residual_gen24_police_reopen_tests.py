#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen25 police reopen tool."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen24_police_reopen.py"
SPEC = importlib.util.spec_from_file_location("re_open_residual_gen24_police_reopen", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN24 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation24-small-table-20260805-v1"
    / "generation-24-residual-terminal-small-table"
)
GEN25 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation25-police-reopen-20260805-v1"
    / "generation-25-residual-terminal-police-reopen"
)
HAS_LAB = GEN24.is_dir() and (GEN24 / "campaign.ready.json").is_file()


class CollectTests(unittest.TestCase):
    def test_collect_includes_index_and_envelopes(self) -> None:
        if not mod.GEN16_RECOVERY.is_file() or not mod.DEEPER.is_file():
            self.skipTest("recovery/deeper missing")
        targets = mod.collect_reopen_starts()
        starts = {t["startVa"].lower() for t in targets}
        self.assertIn("0x004f5ac5", starts)
        self.assertIn("0x005344fc", starts)
        self.assertGreaterEqual(len(targets), 21)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGen25Tests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN25 / "campaign.ready.json").is_file():
            self.skipTest("Gen25 not applied")
        pre = hashlib.sha256((GEN24 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(["verify", "--campaign", str(GEN25), "--parent", str(GEN24)])
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN24 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN25 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 25)
        self.assertEqual(ready["counts"]["residualReopenedThisGeneration"], 21)
        self.assertEqual(ready["counts"]["residualOpenDark"], 99)
        self.assertEqual(ready["counts"]["residualOpenExecuted"], 4)


if __name__ == "__main__":
    unittest.main()
