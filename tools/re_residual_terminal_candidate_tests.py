#!/usr/bin/env python3
"""Integrity gates for residual terminal *candidate* plates (do not mutate Gen10)."""
from __future__ import annotations

import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAD = ROOT / "local-lab" / "residual-padding-terminal-ready-20260805-v1"
MIX = ROOT / "local-lab" / "residual-mixed-shape-terminal-ready-20260805-v1"
REVIEW = ROOT / "local-lab" / "opencode-deepseek-residual-padding-20260805-v1"


@unittest.skipUnless(PAD.is_dir() and MIX.is_dir(), "local-lab candidate plates missing")
class ResidualTerminalCandidateTests(unittest.TestCase):
    def test_padding_integrity_ready(self) -> None:
        path = PAD / "INTEGRITY.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("READY", data["status"])
        self.assertEqual(5012, data["n_terminal"])
        self.assertEqual(0, data["mismatches"])
        self.assertTrue(data["specimen_sha256"].startswith("74154bfae14ddc8e"))
        tsv = PAD / "terminal-padding.tsv"
        self.assertEqual(
            hashlib.sha256(tsv.read_bytes()).hexdigest(),
            data["terminal_tsv_sha256"],
        )

    def test_mixed_shape_integrity_ready(self) -> None:
        path = MIX / "INTEGRITY.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("READY", data["status"])
        self.assertEqual(277, data["n_shape_terminal"])
        self.assertEqual(0, data["executed_in_terminal_list"])
        tsv = MIX / "shape-terminal.tsv"
        self.assertEqual(
            hashlib.sha256(tsv.read_bytes()).hexdigest(),
            data["shape_terminal_tsv_sha256"],
        )

    @unittest.skipUnless(
        (REVIEW / "REVIEW-SUMMARY.json").is_file(), "DeepSeek review plate missing"
    )
    def test_deepseek_direct_review_receipts(self) -> None:
        summary = json.loads((REVIEW / "REVIEW-SUMMARY.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["allOk"])
        self.assertEqual(4, len(summary["results"]))
        labels = {row["label"] for row in summary["results"]}
        self.assertEqual(
            {"flash-normal", "flash-adversarial", "pro-normal", "pro-adversarial"},
            labels,
        )


if __name__ == "__main__":
    unittest.main()
