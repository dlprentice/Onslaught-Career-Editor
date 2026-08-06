#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen32 large-island resolve instrument."""

from __future__ import annotations

import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen32_large_island_resolve.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen32_large_island_resolve", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN32 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation32-deep-segment-resolve-20260805-v1"
    / "generation-32-residual-terminal-deep-segment-resolve"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen32-large-island-resolve-20260805-v1"
HAS_LAB = GEN32.is_dir() and SPECIMEN.is_file()


class UnitWalkTests(unittest.TestCase):
    def test_ptr_run_and_slack(self) -> None:
        ptr = (0x00401000).to_bytes(4, "little")
        self.assertEqual(mod.ptr_run(ptr * 3), 12)
        self.assertEqual(mod.ptr_run(b"\x00\x00" + ptr * 2), 0)
        self.assertTrue(mod.slack_ok(b""))
        self.assertTrue(mod.slack_ok(ptr[:2]))  # incomplete image ptr
        self.assertFalse(mod.slack_ok(b"\xff" * 4))

    def test_no_early_byte_table_on_large_random(self) -> None:
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
        # high-entropy 200B should not full-cover
        blob = bytes((i * 37 + 11) % 256 for i in range(200))
        self.assertFalse(mod.walk_cover(blob, mass, inb, None))


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabLargeIslandTests(unittest.TestCase):
    def test_build_verify_ready_4(self) -> None:
        out = PLATE / "_scratch"
        if out.exists():
            import shutil

            shutil.rmtree(out)
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN32),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(out),
            ]
        )
        self.assertEqual(rc, 0)
        pack = json.loads((out / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 4)
        self.assertEqual(pack["n_police_hold"], 20)
        self.assertEqual(pack["n_hard_mismatches"], 0)
        starts = {p["startVa"].lower() for p in pack["proofs"]}
        self.assertIn("0x005c9c69", starts)
        self.assertIn("0x005925e9", starts)
        self.assertIn("0x00455d9b", starts)
        self.assertIn("0x0052a6f2", starts)
        rc2 = mod.main(["verify", "--plate", str(out)])
        self.assertEqual(rc2, 0)


if __name__ == "__main__":
    unittest.main()
