#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_frontier.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_frontier.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_frontier", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN12 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation12-mixed-shape-20260805-v1"
    / "generation-12-residual-terminal-mixed-shape"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "residual-open-dark-frontier-gen12-20260805-v1"
HAS_LAB = GEN12.is_dir() and SPECIMEN.is_file()


@unittest.skipUnless(HAS_LAB, "local-lab Gen12/specimen unavailable")
class OpenDarkFrontierLabTests(unittest.TestCase):
    def test_build_partition_and_no_mutation(self) -> None:
        pre_res = hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        pre_fn = hashlib.sha256((GEN12 / "campaign-functions.tsv").read_bytes()).hexdigest()
        pre_ready = hashlib.sha256((GEN12 / "campaign.ready.json").read_bytes()).hexdigest()
        summary = mod.build_plate(
            campaign=GEN12,
            specimen=SPECIMEN,
            out_dir=PLATE,
        )
        c = summary["counts"]
        self.assertEqual(c["n_open_dark_input"], 667)
        self.assertEqual(
            c["n_whole_span_terminal"]
            + c["n_partial_subspan_terminal"]
            + c["n_still_fully_open"],
            667,
        )
        self.assertLessEqual(c["formalPackEligiblePadData"], c["n_whole_span_terminal"])
        self.assertEqual(
            c["formalPackEligiblePadData"] + c["codeEnvelopeCandidates"],
            c["n_whole_span_terminal"],
        )
        self.assertEqual(c["formalPackWholeSpanCandidates"], c["formalPackEligiblePadData"])
        self.assertGreaterEqual(c["n_whole_span_terminal"], 1)
        # Envelope quarantine: no STATIC_CODE_DECODE_ENVELOPE may be pack-eligible
        cands = mod._read_tsv(PLATE / "whole-span-terminal-candidates.tsv")
        for row in cands:
            kinds = (row.get("subspanKinds") or "").split(";")
            if "STATIC_CODE_DECODE_ENVELOPE" in kinds:
                self.assertEqual(row.get("formalPackEligible"), "False")
        self.assertEqual(
            pre_res,
            hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            pre_fn,
            hashlib.sha256((GEN12 / "campaign-functions.tsv").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            pre_ready,
            hashlib.sha256((GEN12 / "campaign.ready.json").read_bytes()).hexdigest(),
        )

    def test_verify_published_plate(self) -> None:
        if not (PLATE / "SUMMARY.json").is_file():
            self.skipTest("plate missing")
        rc = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN12),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc, 0)
        integrity = json.loads((PLATE / "INTEGRITY.json").read_text(encoding="utf-8"))
        self.assertTrue(all(integrity["checks"].values()))
        self.assertTrue((PLATE / "open-executed.tsv").is_file())
        # companion executed inventory is 108 rows + header + comment
        lines = [
            ln
            for ln in (PLATE / "open-executed.tsv").read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith("#")
        ]
        # header + 108
        self.assertEqual(len(lines) - 1, 108)

    def test_candidates_are_subset_of_open_dark_vas(self) -> None:
        if not (PLATE / "whole-span-terminal-candidates.tsv").is_file():
            self.skipTest("candidates missing")
        open_dark = mod._read_tsv(PLATE / "open-dark.tsv")
        starts = {r["startVa"].lower() for r in open_dark}
        cands = mod._read_tsv(PLATE / "whole-span-terminal-candidates.tsv")
        for c in cands:
            self.assertIn(c["startVa"].lower(), starts)


if __name__ == "__main__":
    unittest.main()
