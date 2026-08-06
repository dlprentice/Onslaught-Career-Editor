#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_residual_mixed_shape_generation.py"
GEN12 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation12-mixed-shape-20260805-v1"
    / "generation-12-residual-terminal-mixed-shape"
)
PACK = (
    ROOT
    / "local-lab"
    / "residual-mixed-shape-formal-pack-20260805-v1"
    / "FORMAL-PACK.json"
)
PARENT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation11-padding-xrefclean-20260805-v1"
    / "generation-11-residual-terminal-padding"
)
GEN10 = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
)
PAD_PACK = (
    ROOT
    / "local-lab"
    / "residual-terminal-formal-pack-padding-xrefclean-20260805-v1"
    / "FORMAL-PACK.json"
)


@unittest.skipUnless(PACK.is_file() and PARENT.is_dir(), "local MIXED pack / Gen11 missing")
class ResidualMixedShapeGenerationTests(unittest.TestCase):
    def test_formal_pack_ready(self) -> None:
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        self.assertEqual("READY_FOR_GENERATION", pack["status"])
        self.assertEqual(356, pack["n_proofs"])
        self.assertEqual(356, pack["n_require_question_supersession"])
        self.assertEqual(0, pack["n_hard_mismatches"])
        self.assertEqual(
            "RESIDUAL_TERMINAL_MIXED_SHAPE_BULK.v1",
            pack["advance_kind_proposed"],
        )

    @unittest.skipUnless(GEN12.is_dir(), "Gen12 not built yet")
    def test_ready_generation_12(self) -> None:
        ready = json.loads((GEN12 / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(12, ready["generation"])
        self.assertEqual("RESIDUAL_TERMINAL_MIXED_SHAPE_BULK", ready["advance"]["kind"])
        counts = ready["counts"]
        self.assertEqual(4986, counts["residualTerminalPadding"])
        self.assertEqual(21, counts["residualTerminalData"])
        self.assertEqual(335, counts["residualTerminalBoundedAmbiguity"])
        self.assertEqual(667, counts["residualOpenDark"])
        self.assertEqual(108, counts["residualOpenExecuted"])
        self.assertEqual(356, counts["residualTerminalsAddedThisGeneration"])
        self.assertEqual(356, counts["questionsClosedThisGeneration"])

    @unittest.skipUnless(GEN12.is_dir(), "Gen12 not built yet")
    def test_verify_cli(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "verify",
                "--campaign",
                str(GEN12),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(PARENT),
                "--pad-pack",
                str(PAD_PACK),
                "--gen10",
                str(GEN10),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**dict(**__import__("os").environ), "BEA_REPO_ROOT": str(ROOT)},
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("RESIDUAL_MIXED_SHAPE_GENERATION_VERIFIED", completed.stdout)
        self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)

    @unittest.skipUnless(GEN12.is_dir(), "Gen12 not built yet")
    def test_no_open_questions_on_mixed_terminals(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import re_residual_mixed_shape_generation as gen

        residuals = gen._read_tsv(GEN12 / "campaign-residuals.tsv")
        term = [
            r
            for r in residuals
            if r.get("campaignState")
            in {"TERMINAL_DATA", "TERMINAL_BOUNDED_AMBIGUITY"}
        ]
        self.assertEqual(356, len(term))
        self.assertTrue(all(not (r.get("questionIds") or "").strip() for r in term))
        self.assertTrue(
            all(
                r.get("classificationVerdict") == "FORMAL_STATIC_PROOF_SURVIVED"
                for r in term
            )
        )
        # padding preserved
        pad = [r for r in residuals if r.get("campaignState") == "TERMINAL_PADDING"]
        self.assertEqual(4986, len(pad))


if __name__ == "__main__":
    unittest.main()
