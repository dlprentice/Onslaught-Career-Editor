"""Unit test: ledger integrity tool rejects missing falsifiers and accepts Gen10."""
from __future__ import annotations
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_campaign_ledger_integrity.py"
CAMPAIGN = ROOT / (
    "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
    "generation-10-ttd-call-context-observation-v2"
)

@unittest.skipUnless(CAMPAIGN.is_dir(), "Gen10 campaign not present on this machine")
class CampaignLedgerIntegrityTests(unittest.TestCase):
    def test_gen10_passes_integrity_gate(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(TOOL), str(CAMPAIGN)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("PASS campaign ledger integrity", completed.stdout)

    def test_missing_falsifier_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for name in (
                "campaign-functions.tsv",
                "campaign-residuals.tsv",
                "campaign-contracts.tsv",
                "campaign-questions.tsv",
            ):
                shutil.copy(CAMPAIGN / name, tdp / name)
            path = tdp / "campaign-functions.tsv"
            lines = path.read_text(encoding="utf-8").splitlines()
            header_i = next(i for i, line in enumerate(lines) if line and not line.startswith("#"))
            header = lines[header_i].split("\t")
            fi = header.index("cheapestFalsifier")
            for i in range(header_i + 1, len(lines)):
                if lines[i].strip():
                    cols = lines[i].split("\t")
                    cols[fi] = ""
                    lines[i] = "\t".join(cols)
                    break
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-B", str(TOOL), str(tdp)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("missing cheapestFalsifier", completed.stdout + completed.stderr)

if __name__ == "__main__":
    unittest.main()
