#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_still_open_inbound_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_still_open_inbound_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_dark_still_open_inbound_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN16 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation16-code-like-mass-20260805-v1"
    / "generation-16-residual-terminal-code-like-mass"
)
GEN17 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation17-still-open-inbound-20260805-v1"
    / "generation-17-residual-terminal-still-open-inbound"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-dark-still-open-inbound-gen16-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = GEN16.is_dir() and PACK.is_file()


class PolicyTests(unittest.TestCase):
    def test_expected_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 50)
        self.assertEqual(mod.EXPECTED_PAD_ADDED, 50)
        self.assertEqual(mod.EXPECTED_AMBIG_ADDED, 0)
        self.assertEqual(
            mod.ADVANCE_KIND, "RESIDUAL_TERMINAL_OPEN_DARK_STILL_OPEN_INBOUND"
        )


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGenerationTests(unittest.TestCase):
    def test_verify_if_applied(self) -> None:
        if not (GEN17 / "campaign.ready.json").is_file():
            self.skipTest("Gen17 not applied yet")
        pre = hashlib.sha256((GEN16 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN17),
                "--parent",
                str(GEN16),
                "--formal-pack",
                str(PACK),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256(
            (GEN16 / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((GEN17 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 17)
        self.assertEqual(ready["counts"]["residualOpenDark"], 285)
        self.assertEqual(ready["counts"]["residualTerminalPadding"], 5062)
        self.assertEqual(ready["counts"]["terminalPaddingAddedThisGeneration"], 50)


if __name__ == "__main__":
    unittest.main()
