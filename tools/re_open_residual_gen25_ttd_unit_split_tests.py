#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen25 OPEN_EXECUTED unit-split instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen25_ttd_unit_split.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen25_ttd_unit_split", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN25 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation25-police-reopen-20260805-v1"
    / "generation-25-residual-terminal-police-reopen"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen25-ttd-unit-split-20260805-v1"
HAS_LAB = GEN25.is_dir() and SPECIMEN.is_file()


class ConstantsTests(unittest.TestCase):
    def test_expected_exec_set(self) -> None:
        self.assertEqual(len(mod.EXPECTED_EXEC_STARTS), 4)
        self.assertIn(0x004AC6B0, mod.EXPECTED_EXEC_STARTS)
        self.assertIn(0x004DA4BE, mod.EXPECTED_EXEC_STARTS)
        self.assertIn(0x004DA89C, mod.EXPECTED_EXEC_STARTS)
        self.assertIn(0x005772C7, mod.EXPECTED_EXEC_STARTS)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabUnitSplitTests(unittest.TestCase):
    def test_static_classifiers_on_known_residuals(self) -> None:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs

        mass_spec = importlib.util.spec_from_file_location(
            "mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
        )
        assert mass_spec and mass_spec.loader
        mass = importlib.util.module_from_spec(mass_spec)
        mass_spec.loader.exec_module(mass)
        data = SPECIMEN.read_bytes()
        ib, secs = mass.pe_map(data)
        md = Cs(CS_ARCH_X86, CS_MODE_32)

        # ret 0x10 imm tail
        r = mod.try_prev_insn_span(
            data, 0x005772C7, 0x005772C9, ib, secs, md, mass
        )
        self.assertIsNotNone(r)
        assert r is not None
        self.assertEqual(r["lane"], "PREV_INSN_SPAN")
        self.assertEqual(r["mnemonic"], "ret")

        # lea interior byte
        r2 = mod.try_prev_insn_span(
            data, 0x004AC6B0, 0x004AC6B1, ib, secs, md, mass
        )
        self.assertIsNotNone(r2)
        assert r2 is not None
        self.assertEqual(r2["lane"], "PREV_INSN_SPAN")

        # jmp-over xor esi,esi
        r3 = mod.try_jmp_over_fragment(
            data, 0x004DA89C, 0x004DA89E, ib, secs, md, mass
        )
        self.assertIsNotNone(r3)
        assert r3 is not None
        self.assertEqual(r3["lane"], "JMP_OVER_FRAGMENT")

        # switch case entry
        r4 = mod.try_switch_case_entry(
            data, 0x004DA4BE, 0x004DA4DA, ib, secs, md, mass
        )
        self.assertIsNotNone(r4)
        assert r4 is not None
        self.assertEqual(r4["lane"], "SWITCH_CASE_ENTRY")

    def test_build_and_verify_four_proofs(self) -> None:
        pre = hashlib.sha256((GEN25 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN25),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN25 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 4)
        self.assertEqual(pack["n_still_open_executed"], 0)
        self.assertTrue(pack.get("hold_generation_apply"))
        lanes = pack["recoveryLaneCounts"]
        self.assertEqual(lanes.get("PREV_INSN_SPAN"), 2)
        self.assertEqual(lanes.get("JMP_OVER_FRAGMENT"), 1)
        self.assertEqual(lanes.get("SWITCH_CASE_ENTRY"), 1)
        starts = {p["startVa"].lower() for p in pack["proofs"]}
        self.assertEqual(
            starts,
            {"0x004ac6b0", "0x004da4be", "0x004da89c", "0x005772c7"},
        )
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN25),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)
        post2 = hashlib.sha256((GEN25 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post2)


if __name__ == "__main__":
    unittest.main()
