#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen26 tiny OPEN_DARK fragment instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen26_tiny_fragment.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen26_tiny_fragment", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN26 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation26-unit-split-20260805-v1"
    / "generation-26-residual-terminal-unit-split"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen26-tiny-fragment-20260805-v1"
HAS_LAB = GEN26.is_dir() and SPECIMEN.is_file()


class UnitExactInsnTests(unittest.TestCase):
    def test_exact_xor_two_byte(self) -> None:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs

        mass_spec = importlib.util.spec_from_file_location(
            "mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
        )
        assert mass_spec and mass_spec.loader
        mass = importlib.util.module_from_spec(mass_spec)
        mass_spec.loader.exec_module(mass)
        # synthetic: only exact-seq path needs real PE for mass.span — skip if no lab
        if not SPECIMEN.is_file():
            self.skipTest("no specimen")
        data = SPECIMEN.read_bytes()
        ib, secs = mass.pe_map(data)
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        # known Gen26 tiny: 0x416119 xor edi,edi
        got = mod.try_exact_insn_seq(
            data, 0x00416119, 0x0041611B, ib, secs, md, mass
        )
        self.assertIsNotNone(got)
        assert got is not None
        self.assertEqual(got["lane"], "EXACT_INSN")
        self.assertEqual(got["insns"][0]["mnemonic"], "xor")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabTinyFragmentTests(unittest.TestCase):
    def test_build_verify_ready(self) -> None:
        pre = hashlib.sha256((GEN26 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN26),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN26 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_tiny_input"], 16)
        self.assertGreaterEqual(pack["n_proofs"], 15)
        self.assertTrue(pack.get("hold_generation_apply"))
        self.assertEqual(pack["n_open_dark_input"], 98)
        self.assertEqual(pack["n_open_executed_input"], 0)
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN26),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)
        post2 = hashlib.sha256((GEN26 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post2)


if __name__ == "__main__":
    unittest.main()
