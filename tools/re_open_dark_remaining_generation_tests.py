#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_remaining_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_remaining_generation.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_remaining_generation", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN14 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation14-code-envelope-20260805-v1"
    / "generation-14-residual-terminal-code-envelope"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-dark-remaining-frontier-gen14-20260805-v1"
    / "FORMAL-PACK.json"
)
GEN15 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation15-open-dark-remaining-20260805-v1"
    / "generation-15-residual-terminal-open-dark-remaining"
)
HAS_LAB = GEN14.is_dir() and PACK.is_file()


@unittest.skipUnless(HAS_LAB, "local-lab Gen14/pack unavailable")
class OpenDarkRemainingGenerationTests(unittest.TestCase):
    def test_build_gen15_no_parent_mutation(self) -> None:
        pre = hashlib.sha256((GEN14 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gen15"
            receipt = mod.build_generation(
                parent=GEN14, formal_pack=PACK, out=out
            )
            self.assertEqual(receipt["status"], "APPLIED")
            self.assertEqual(receipt["generation"], 15)
            c = receipt["counts"]
            self.assertEqual(c["residualTerminalsAddedThisGeneration"], 32)
            self.assertEqual(c["terminalBoundedAmbiguityAddedThisGeneration"], 32)
            self.assertEqual(c["questionsClosedThisGeneration"], 32)
            self.assertEqual(c["residualOpenDark"], 381)
            self.assertEqual(c["residualTerminalBoundedAmbiguity"], 609)
            self.assertEqual(c["residualTerminalPadding"], 4996)
            self.assertEqual(c["residualTerminalData"], 23)
            self.assertEqual(c["residualOpenExecuted"], 108)
            self.assertEqual(
                pre,
                hashlib.sha256((GEN14 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
            )
            result = mod.verify_generation(out, PACK, GEN14, verify_parent=False)
            self.assertEqual(result["status"], "CAMPAIGN_VERIFIED")

    def test_published_gen15_if_present(self) -> None:
        if not (GEN15 / "campaign.ready.json").is_file():
            self.skipTest("published Gen15 missing")
        ready = json.loads((GEN15 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 15)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 32)
        parent_sha = ready["parentCampaign"]["residualsSha256"]
        live = hashlib.sha256((GEN14 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(parent_sha, live)
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN15),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(GEN14),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
