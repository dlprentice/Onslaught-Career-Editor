#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_residual_terminal_generation.py"
GEN11 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation11-padding-xrefclean-20260805-v1"
    / "generation-11-residual-terminal-padding"
)
PACK = (
    ROOT
    / "local-lab"
    / "residual-terminal-formal-pack-padding-xrefclean-20260805-v1"
    / "FORMAL-PACK.json"
)
PARENT = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
)


@unittest.skipUnless(GEN11.is_dir() and PACK.is_file() and PARENT.is_dir(), "local generation missing")
class ResidualTerminalGenerationTests(unittest.TestCase):
    def test_ready_generation_11(self) -> None:
        ready = json.loads((GEN11 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(11, ready["generation"])
        self.assertEqual("RESIDUAL_TERMINAL_PADDING_BULK", ready["advance"]["kind"])
        counts = ready["counts"]
        # xref-clean pack: 4986 proofs (5012 - 26 abs-hit exclusions)
        self.assertEqual(4986, counts["residualTerminalPadding"])
        self.assertEqual(1023, counts["residualOpenDark"])
        self.assertEqual(108, counts["residualOpenExecuted"])
        self.assertEqual(4971, counts["residualTerminalsAddedThisGeneration"])
        self.assertEqual(4971, counts["questionsClosedThisGeneration"])

    def test_verify_cli(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "verify",
                "--campaign",
                str(GEN11),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(PARENT),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**dict(**__import__("os").environ), "BEA_REPO_ROOT": str(ROOT)},
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("RESIDUAL_TERMINAL_GENERATION_VERIFIED", completed.stdout)
        self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)

    def test_no_open_questions_on_terminals(self) -> None:
        # drive shipped reader path via generation module
        sys.path.insert(0, str(ROOT / "tools"))
        import re_residual_terminal_generation as gen

        residuals = gen._read_tsv(GEN11 / "campaign-residuals.tsv")
        term = [r for r in residuals if r.get("campaignState") == "TERMINAL_PADDING"]
        self.assertEqual(4986, len(term))
        self.assertTrue(all(not (r.get("questionIds") or "").strip() for r in term))
        self.assertTrue(
            all(r.get("classificationVerdict") == "FORMAL_STATIC_PROOF_SURVIVED" for r in term)
        )


if __name__ == "__main__":
    unittest.main()
