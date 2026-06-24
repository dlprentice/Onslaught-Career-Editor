#!/usr/bin/env python3
"""Tests for the Goodies scalar-reference summary probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import goodies_scalar_reference_probe as probe


class GoodiesScalarReferenceProbeTests(unittest.TestCase):
    def test_summarizes_known_support_and_candidate_functions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tsv = root / "scalar.tsv"
            out = root / "summary.json"
            tsv.write_text(
                "\n".join(
                    [
                        "value_decimal\tvalue_hex\tinstruction_addr\tfunction_addr\tfunction\tblock\tmnemonic\toperand_index\toperand",
                        "71\t0x47\t0041c500\t0041c470\tCCareer__UpdateGoodieStates\t.text\tPUSH\t0\t0x47",
                        "72\t0x48\t0045cc10\t0045cbb0\tCFEPGoodies__StartLoadingGoody\t.text\tCMP\t1\t0x48",
                        "73\t0x49\t00501234\t00501000\tFEPGoodiesPotentialHiddenSelector\t.text\tMOV\t0\t0x49",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = probe.build_report(tsv)
            out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["rowCount"], 3)
            self.assertEqual(report["candidateRowCount"], 1)
            self.assertEqual(report["candidateFunctionCounts"], {"FEPGoodiesPotentialHiddenSelector": 1})
            self.assertEqual(report["knownSupportRowCount"], 2)
            self.assertEqual(report["literalImmediateCandidateRowCount"], 1)
            self.assertEqual(report["focusedCandidateFunctionCounts"], {"FEPGoodiesPotentialHiddenSelector": 1})

    def test_missing_tsv_is_a_failed_report(self) -> None:
        report = probe.build_report(Path("missing.tsv"))

        self.assertEqual(report["status"], "FAIL")
        self.assertIn("missing scalar TSV", report["failures"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
