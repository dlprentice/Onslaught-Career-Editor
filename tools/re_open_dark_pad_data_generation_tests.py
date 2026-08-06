#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_pad_data_generation.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_pad_data_generation.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_pad_data_generation", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN12 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation12-mixed-shape-20260805-v1"
    / "generation-12-residual-terminal-mixed-shape"
)
PACK = ROOT / "local-lab" / "open-dark-pad-data-formal-pack-20260805-v1" / "FORMAL-PACK.json"
GEN13 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation13-open-dark-pad-data-20260805-v1"
    / "generation-13-residual-terminal-open-dark-pad-data"
)
HAS_LAB = GEN12.is_dir() and PACK.is_file()


@unittest.skipUnless(HAS_LAB, "local-lab Gen12/pack unavailable")
class PadDataGenerationLabTests(unittest.TestCase):
    def test_build_gen13_no_parent_mutation(self) -> None:
        pre_res = hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        pre_ready = hashlib.sha256((GEN12 / "campaign.ready.json").read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gen13"
            receipt = mod.build_generation(
                parent=GEN12, formal_pack=PACK, out=out
            )
            self.assertEqual(receipt["status"], "APPLIED")
            self.assertEqual(receipt["generation"], 13)
            c = receipt["counts"]
            self.assertEqual(c["residualTerminalsAddedThisGeneration"], 12)
            self.assertEqual(c["terminalPaddingAddedThisGeneration"], 10)
            self.assertEqual(c["terminalDataAddedThisGeneration"], 2)
            self.assertEqual(c["questionsClosedThisGeneration"], 12)
            self.assertEqual(c["residualOpenDark"], 655)
            self.assertEqual(c["residualOpenExecuted"], 108)
            self.assertEqual(c["residualTerminalPadding"], 4996)
            self.assertEqual(c["residualTerminalData"], 23)
            self.assertEqual(c["residualTerminalBoundedAmbiguity"], 335)
            ready = json.loads((out / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(ready["generation"], 13)
            self.assertEqual(ready["advance"]["kind"], "RESIDUAL_TERMINAL_OPEN_DARK_PAD_DATA")
            # parent immutability
            self.assertEqual(
                pre_res,
                hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                pre_ready,
                hashlib.sha256((GEN12 / "campaign.ready.json").read_bytes()).hexdigest(),
            )
            # verify without nested parent (temp out still valid for local checks)
            result = mod.verify_generation(
                out, PACK, GEN12, verify_parent=False
            )
            self.assertEqual(result["status"], "CAMPAIGN_VERIFIED")
            self.assertEqual(result["nProofs"], 12)

    def test_published_gen13_if_present(self) -> None:
        if not (GEN13 / "campaign.ready.json").is_file():
            self.skipTest("published Gen13 missing")
        ready = json.loads((GEN13 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 13)
        self.assertEqual(ready["counts"]["residualTerminalsAddedThisGeneration"], 12)
        # parent unmutated
        parent_sha = ready["parentCampaign"]["residualsSha256"]
        live = hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(parent_sha, live)
        rc = mod.main(
            [
                "verify",
                "--campaign",
                str(GEN13),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(GEN12),
                "--skip-parent-verify",
            ]
        )
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
