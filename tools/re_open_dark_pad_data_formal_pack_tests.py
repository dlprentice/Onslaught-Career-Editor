#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_pad_data_formal_pack.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_pad_data_formal_pack.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_pad_data_formal_pack", TOOL)
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
CANDS = (
    ROOT
    / "local-lab"
    / "residual-open-dark-frontier-gen12-20260805-v1"
    / "formal-pack-eligible-pad-data.tsv"
)
DEEPER = (
    ROOT
    / "local-lab"
    / "residual-open-dark-frontier-gen12-20260805-v1"
    / "deeper-rows.json"
)
PLATE = ROOT / "local-lab" / "open-dark-pad-data-formal-pack-20260805-v1"
HAS_LAB = GEN12.is_dir() and SPECIMEN.is_file() and CANDS.is_file() and DEEPER.is_file()


class KindPolicyTests(unittest.TestCase):
    def test_envelope_forbidden(self) -> None:
        self.assertIn("STATIC_CODE_DECODE_ENVELOPE", mod.FORBIDDEN_KINDS)
        self.assertNotIn("STATIC_CODE_DECODE_ENVELOPE", mod.ALLOWED_KINDS)

    def test_proposed_pad_vs_data(self) -> None:
        pad = mod.proposed_for_kind("TINY_PAD_GAP")
        self.assertEqual(pad["terminalState"], "TERMINAL_PADDING")
        data = mod.proposed_for_kind("CODE_ADDRESS_TABLE_PREFIX")
        self.assertEqual(data["terminalState"], "TERMINAL_DATA")


@unittest.skipUnless(HAS_LAB, "local-lab inputs unavailable")
class LabFormalPackTests(unittest.TestCase):
    def test_build_exactly_12_no_mutation(self) -> None:
        pre = hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        pack = mod.build_pack(
            specimen=SPECIMEN,
            candidates_tsv=CANDS,
            deeper_rows_json=DEEPER,
            campaign=GEN12,
        )
        self.assertEqual(pack["n_proofs"], 12)
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_hard_mismatches"], 0)
        kinds = {p["kind"] for p in pack["proofs"]}
        self.assertTrue(kinds <= mod.ALLOWED_KINDS)
        self.assertNotIn("STATIC_CODE_DECODE_ENVELOPE", kinds)
        # 10 pad + 2 code address tables expected
        self.assertEqual(pack["kindCounts"].get("TINY_PAD_GAP"), 10)
        self.assertEqual(pack["kindCounts"].get("CODE_ADDRESS_TABLE_PREFIX"), 2)
        self.assertEqual(pack["proposedTerminalStateCounts"].get("TERMINAL_PADDING"), 10)
        self.assertEqual(pack["proposedTerminalStateCounts"].get("TERMINAL_DATA"), 2)
        self.assertEqual(
            pre,
            hashlib.sha256((GEN12 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
        )

    def test_write_verify_roundtrip(self) -> None:
        pack = mod.build_pack(
            specimen=SPECIMEN,
            candidates_tsv=CANDS,
            deeper_rows_json=DEEPER,
            campaign=GEN12,
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "plate"
            mod.write_plate(pack, out, campaign=GEN12, specimen=SPECIMEN)
            for name in (
                "FORMAL-PACK.json",
                "SUMMARY.json",
                "INTEGRITY.json",
                "proofs.tsv",
                "README.md",
            ):
                self.assertTrue((out / name).is_file(), name)
            integrity = json.loads((out / "INTEGRITY.json").read_text(encoding="utf-8"))
            self.assertTrue(all(integrity["checks"].values()))
            rc = mod.main(
                [
                    "verify",
                    "--plate",
                    str(out),
                    "--campaign",
                    str(GEN12),
                    "--specimen",
                    str(SPECIMEN),
                ]
            )
            self.assertEqual(rc, 0)

    def test_published_plate_if_present(self) -> None:
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("published plate missing")
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


if __name__ == "__main__":
    unittest.main()
