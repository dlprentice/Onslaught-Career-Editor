#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen30 SEH/segment-resolve instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen30_seh_segment_resolve.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen30_seh_segment_resolve", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN30 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation30-msvc-table-mix-20260805-v1"
    / "generation-30-residual-terminal-msvc-table-mix"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen30-seh-segment-resolve-20260805-v1"
HAS_LAB = GEN30.is_dir() and SPECIMEN.is_file()


class UnitSehTests(unittest.TestCase):
    def test_seh_stub_exact(self) -> None:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs

        mass_spec = importlib.util.spec_from_file_location(
            "mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
        )
        assert mass_spec and mass_spec.loader
        mass = importlib.util.module_from_spec(mass_spec)
        mass_spec.loader.exec_module(mass)
        inb_spec = importlib.util.spec_from_file_location(
            "inb", ROOT / "tools" / "re_open_dark_still_open_inbound.py"
        )
        assert inb_spec and inb_spec.loader
        inb = importlib.util.module_from_spec(inb_spec)
        inb_spec.loader.exec_module(inb)
        mu_spec = importlib.util.spec_from_file_location(
            "mu", ROOT / "tools" / "re_open_residual_gen19_multi_unit.py"
        )
        assert mu_spec and mu_spec.loader
        mu = importlib.util.module_from_spec(mu_spec)
        mu_spec.loader.exec_module(mu)
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        # push [ebp-0x14]; call $+0x1f; pop ecx; ret
        blob = bytes.fromhex("ff75ece81a00000059c3")
        rec = mod.seh_compose(blob, 0x401000, md, mass, inb, mu)
        self.assertIsNotNone(rec)
        assert rec is not None
        self.assertEqual(rec["lane"], "SEH_FILTER_STUB")

    def test_seh_plus_one_insn(self) -> None:
        from capstone import CS_ARCH_X86, CS_MODE_32, Cs

        mass_spec = importlib.util.spec_from_file_location(
            "mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
        )
        assert mass_spec and mass_spec.loader
        mass = importlib.util.module_from_spec(mass_spec)
        mass_spec.loader.exec_module(mass)
        inb_spec = importlib.util.spec_from_file_location(
            "inb", ROOT / "tools" / "re_open_dark_still_open_inbound.py"
        )
        assert inb_spec and inb_spec.loader
        inb = importlib.util.module_from_spec(inb_spec)
        inb_spec.loader.exec_module(inb)
        mu_spec = importlib.util.spec_from_file_location(
            "mu", ROOT / "tools" / "re_open_residual_gen19_multi_unit.py"
        )
        assert mu_spec and mu_spec.loader
        mu = importlib.util.module_from_spec(mu_spec)
        mu_spec.loader.exec_module(mu)
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        # seh + mov esp, [ebp-0x18]
        blob = bytes.fromhex("ff75ece81a00000059c38b65e8")
        rec = mod.seh_compose(blob, 0x401000, md, mass, inb, mu)
        self.assertIsNotNone(rec)
        assert rec is not None
        self.assertEqual(rec["lane"], "SEH_PLUS_EXACT_INSN")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabSehSegmentTests(unittest.TestCase):
    def test_build_verify_ready_4(self) -> None:
        pre = hashlib.sha256((GEN30 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN30),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN30 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 4)
        self.assertEqual(pack["n_open_dark_input"], 30)
        self.assertEqual(pack.get("n_police_hold"), 20)
        self.assertTrue(pack.get("hold_generation_apply"))
        lanes = pack["recoveryLaneCounts"]
        self.assertIn("SEH_PLUS_EXACT_INSN", lanes)
        self.assertIn("SEGMENT_RESOLVE", lanes)
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN30),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)


if __name__ == "__main__":
    unittest.main()
