#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_executed_residual_join.py"
PLATE = ROOT / "local-lab" / "residual-executed-trace-callback-join-20260805-v1"
SPEC = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
RES = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
    / "campaign-residuals.tsv"
)


@unittest.skipUnless(PLATE.is_dir() and (PLATE / "SUMMARY.json").is_file(), "join plate missing")
class ExecutedResidualJoinPlateTests(unittest.TestCase):
    def test_summary_counts(self) -> None:
        summary = json.loads((PLATE / "SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual("MEASURED", summary["status"])
        self.assertEqual(108, summary["n_executed_residuals"])
        self.assertEqual(108, summary["n_coverage_corroborated"])
        self.assertEqual(0, summary["n_coverage_zero"])
        grades = summary["gradeCounts"]
        self.assertEqual(7, grades.get("CALLBACK_SLOT_INSTALL", 0))
        self.assertEqual(1, grades.get("SLOT_CONSUMER_NEAR_IMM", 0))
        self.assertEqual(8, summary["n_terminal_candidates"])

    def test_integrity_ready(self) -> None:
        integrity = json.loads((PLATE / "INTEGRITY.json").read_text(encoding="utf-8"))
        self.assertEqual("READY", integrity["status"])
        self.assertEqual(108, integrity["n_rows"])

    def test_every_row_has_falsifier(self) -> None:
        join = json.loads((PLATE / "JOIN.json").read_text(encoding="utf-8"))
        for row in join["rows"]:
            self.assertTrue((row.get("cheapestFalsifier") or "").strip())
            self.assertFalse(row.get("namePromotion"))


@unittest.skipUnless(SPEC.is_file() and RES.is_file(), "local specimen/ledger missing")
class ExecutedResidualJoinToolTests(unittest.TestCase):
    def test_cli_smoke_limited_coverage(self) -> None:
        # limited coverage roots keep the unit test bounded
        out = ROOT / "local-lab" / "_tmp_executed_join_smoke" / "JOIN.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--specimen",
                str(SPEC),
                "--campaign-residuals",
                str(RES),
                "--coverage-root",
                str(ROOT / "local-lab"),
                "--coverage-limit",
                "5",
                "--json-out",
                str(out),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("EXECUTED_RESIDUAL_JOIN_OK", completed.stdout)
        summary = json.loads(out.with_name("SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(108, summary["n_executed_residuals"])


if __name__ == "__main__":
    unittest.main()
