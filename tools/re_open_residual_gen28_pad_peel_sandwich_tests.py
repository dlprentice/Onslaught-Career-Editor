#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen28 pad-peel/sandwich instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen28_pad_peel_sandwich.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen28_pad_peel_sandwich", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN28 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation28-open-dark-unit-split-20260805-v1"
    / "generation-28-residual-terminal-open-dark-unit-split"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen28-pad-peel-sandwich-20260805-v1"
HAS_LAB = GEN28.is_dir() and SPECIMEN.is_file()


class UnitPeelTests(unittest.TestCase):
    def test_peel_pad_sides(self) -> None:
        class Mass:
            @staticmethod
            def is_pure_pad(b):
                return bool(b) and all(x in (0x00, 0x90, 0xCC) for x in b)

        class Inb:
            @staticmethod
            def is_full_align_nop_run(b):
                return False

        blob = b"\x90\x90" + b"\x55\xC3" + b"\xCC\xCC\xCC"
        lead, trail, head = mod.peel_pad(blob, Mass(), Inb())
        self.assertEqual(lead, 2)
        self.assertEqual(trail, 3)
        self.assertEqual(head, b"\x55\xC3")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabPadPeelTests(unittest.TestCase):
    def test_build_verify_ready_18(self) -> None:
        pre = hashlib.sha256((GEN28 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN28),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN28 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 18)
        self.assertEqual(pack["n_open_dark_input"], 58)
        self.assertTrue(pack.get("hold_generation_apply"))
        lanes = pack["recoveryLaneCounts"]
        self.assertEqual(lanes.get("PAD_PEEL_SMALL_TABLE"), 7)
        self.assertEqual(lanes.get("PAD_PEEL_DATA_SHAPE"), 1)
        self.assertEqual(lanes.get("SANDWICH_FULL_LINEAR"), 10)
        for p in pack["proofs"]:
            self.assertFalse(
                p.get("police_reopen") and p["recoveryLane"] == "PAD_PEEL_ENVELOPE"
            )
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN28),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)


if __name__ == "__main__":
    unittest.main()
