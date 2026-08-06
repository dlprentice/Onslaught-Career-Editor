#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_residual_padding_classify.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
RESIDUALS = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
    / "campaign-residuals.tsv"
)


class ResidualPaddingClassifyTests(unittest.TestCase):
    @unittest.skipUnless(SPECIMEN.is_file() and RESIDUALS.is_file(), "local evidence missing")
    def test_all_padding_dark_are_terminal_on_pristine(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--specimen",
                str(SPECIMEN),
                "--residuals-tsv",
                str(RESIDUALS),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("RESIDUAL_PADDING_CLASSIFY_PASS", completed.stdout)
        payload = json.loads(
            completed.stdout.split("RESIDUAL_PADDING_CLASSIFY_")[0].strip()
        )
        self.assertEqual(5012, payload["n_total_padding_dark"])
        self.assertEqual(5012, payload["n_terminal_pure_padding"])
        self.assertEqual(4970, payload["counts"]["NOP_PADDING"])
        self.assertEqual(42, payload["counts"]["INT3_PADDING"])
        self.assertEqual(39210, payload["bytes_classified"])


if __name__ == "__main__":
    unittest.main()
