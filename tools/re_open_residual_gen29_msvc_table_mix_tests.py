#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen29 MSVC multi-table-mix instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen29_msvc_table_mix.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen29_msvc_table_mix", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN29 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation29-pad-peel-sandwich-20260805-v1"
    / "generation-29-residual-terminal-pad-peel-sandwich"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen29-msvc-table-mix-20260805-v1"
HAS_LAB = GEN29.is_dir() and SPECIMEN.is_file()


class UnitComposeTests(unittest.TestCase):
    def test_tiny_nop_plus_three_ptrs(self) -> None:
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
        large_spec = importlib.util.spec_from_file_location(
            "large", ROOT / "tools" / "re_large_mixed_blob_classify.py"
        )
        assert large_spec and large_spec.loader
        large = importlib.util.module_from_spec(large_spec)
        large_spec.loader.exec_module(large)

        # nop + three .text dwords
        blob = b"\x90" + b"".join(
            (0x401000 + i * 0x10).to_bytes(4, "little") for i in range(3)
        )
        rec = mod.compose_msvc_table_mix(blob, 0x401000, mass, inb, large)
        self.assertIsNotNone(rec)
        assert rec is not None
        self.assertEqual(rec["lane"], "MSVC_MULTI_TABLE_MIX")
        self.assertEqual(rec["tableBytes"], 12)

    def test_index_cannot_exceed_table(self) -> None:
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
        large_spec = importlib.util.spec_from_file_location(
            "large", ROOT / "tools" / "re_large_mixed_blob_classify.py"
        )
        assert large_spec and large_spec.loader
        large = importlib.util.module_from_spec(large_spec)
        large_spec.loader.exec_module(large)
        # 8B table + 20B index-like -> idx > table -> refuse
        table = b"".join((0x401000 + i * 4).to_bytes(4, "little") for i in range(2))
        idx = bytes([0x01] * 20)
        rec = mod.compose_msvc_table_mix(table + idx, 0x401000, mass, inb, large)
        self.assertIsNone(rec)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabMsvcTableMixTests(unittest.TestCase):
    def test_build_verify_ready_10(self) -> None:
        pre = hashlib.sha256((GEN29 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN29),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN29 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 10)
        self.assertEqual(pack["n_open_dark_input"], 40)
        self.assertEqual(pack.get("n_police_hold"), 20)
        self.assertTrue(pack.get("hold_generation_apply"))
        self.assertEqual(pack["recoveryLaneCounts"].get("MSVC_MULTI_TABLE_MIX"), 10)
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN29),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)


if __name__ == "__main__":
    unittest.main()
