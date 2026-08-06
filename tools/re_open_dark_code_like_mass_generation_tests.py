#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_code_like_mass_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_code_like_mass_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_dark_code_like_mass_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN15 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation15-open-dark-remaining-20260805-v1"
    / "generation-15-residual-terminal-open-dark-remaining"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-dark-code-like-mass-gen15-20260805-v1"
    / "FORMAL-PACK.json"
)
GEN16 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation16-code-like-mass-20260805-v1"
    / "generation-16-residual-terminal-code-like-mass"
)
HAS_LAB = GEN15.is_dir() and PACK.is_file()


@unittest.skipUnless(HAS_LAB, "local-lab Gen15/pack unavailable")
class CodeLikeMassGenerationTests(unittest.TestCase):
    def test_build_gen16_no_parent_mutation(self) -> None:
        pre = hashlib.sha256((GEN15 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gen16"
            receipt = mod.build_generation(
                parent=GEN15, formal_pack=PACK, out=out
            )
            self.assertEqual(receipt["status"], "APPLIED")
            self.assertEqual(receipt["generation"], 16)
            c = receipt["counts"]
            self.assertEqual(c["residualTerminalsAddedThisGeneration"], 46)
            self.assertEqual(c["terminalPaddingAddedThisGeneration"], 16)
            self.assertEqual(c["terminalBoundedAmbiguityAddedThisGeneration"], 30)
            self.assertEqual(c["questionsClosedThisGeneration"], 46)
            self.assertEqual(c["residualOpenDark"], 335)
            self.assertEqual(c["residualTerminalPadding"], 5012)
            self.assertEqual(c["residualTerminalBoundedAmbiguity"], 639)
            self.assertEqual(c["residualTerminalData"], 23)
            self.assertEqual(c["residualOpenExecuted"], 108)
            self.assertEqual(
                pre,
                hashlib.sha256((GEN15 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
            )
            result = mod.verify_generation(out, PACK, GEN15, verify_parent=False)
            self.assertEqual(result["status"], "CAMPAIGN_VERIFIED")

    def test_published_gen16_if_present(self) -> None:
        if not (GEN16 / "campaign.ready.json").is_file():
            self.skipTest("published Gen16 missing")
        ready = json.loads((GEN16 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 16)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 46)
        parent_sha = ready["parentCampaign"]["residualsSha256"]
        live = hashlib.sha256((GEN15 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(parent_sha, live)
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN16),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(GEN15),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
