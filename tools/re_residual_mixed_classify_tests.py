#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_residual_mixed_classify.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
RESIDUALS = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
    / "campaign-residuals.tsv"
)


class ResidualMixedClassifyTests(unittest.TestCase):
    @unittest.skipUnless(SPECIMEN.is_file() and RESIDUALS.is_file(), "local evidence missing")
    def test_mixed_counts_and_executed_terminal(self) -> None:
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
        self.assertIn("RESIDUAL_MIXED_CLASSIFY_OK", completed.stdout)
        payload = json.loads(completed.stdout.split("RESIDUAL_MIXED_CLASSIFY_OK")[0].strip())
        self.assertEqual(1105, payload["n_total"])
        self.assertEqual(
            108, payload["counts"].get("EXECUTED_CODE_SPAN_OPEN_BOUNDARY", 0)
        )
        # EXECUTED is explicitly non-terminal (open boundary)
        self.assertLess(payload["n_terminal"], payload["n_total"] - 100)
        self.assertTrue(payload["capstone"])
        # Conservative: most mixed rows stay open
        self.assertGreater(payload["n_open"], 700)
        self.assertGreaterEqual(payload["counts"].get("STATIC_CODE_DECODE_ENVELOPE", 0), 200)


if __name__ == "__main__":
    unittest.main()
