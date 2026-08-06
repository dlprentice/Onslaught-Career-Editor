#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen31 deep segment-resolve instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen31_deep_segment_resolve.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen31_deep_segment_resolve", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN31 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation31-seh-segment-resolve-20260805-v1"
    / "generation-31-residual-terminal-seh-segment-resolve"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen31-deep-segment-resolve-20260805-v1"
HAS_LAB = GEN31.is_dir() and SPECIMEN.is_file()


class UnitDeepTests(unittest.TestCase):
    def test_index_glue_before_table(self) -> None:
        # Small-int prefix (≤0x20 / nop / int3), up to 16B, stops at code-ptr.
        # 0x08 0x07 + four 0x00 = six glue bytes (no .text dword to stop early).
        self.assertEqual(mod.index_glue(b"\x08\x07" + b"\x00" * 4), 6)
        # With a real code-ptr after 2B glue, stop before the table.
        ptr = (0x00401000).to_bytes(4, "little")
        self.assertEqual(mod.index_glue(b"\x08\x07" + ptr), 2)
        self.assertEqual(mod.index_glue(b"\xff\xff"), 0)

    def test_deep_mtm_with_glue(self) -> None:
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
        mtm_spec = importlib.util.spec_from_file_location(
            "mtm", ROOT / "tools" / "re_open_residual_gen29_msvc_table_mix.py"
        )
        assert mtm_spec and mtm_spec.loader
        mtm = importlib.util.module_from_spec(mtm_spec)
        mtm_spec.loader.exec_module(mtm)

        # 2-byte glue + 3 code ptrs + pure pad trail
        glue = b"\x08\x07"
        table = b"".join((0x401000 + i * 0x10).to_bytes(4, "little") for i in range(3))
        trail = b"\x90" * 4
        blob = glue + table + trail
        rec = mod.compose_deep_mtm(blob, 0x401000, mass, inb, large, mtm)
        self.assertIsNotNone(rec)
        assert rec is not None
        self.assertEqual(rec["lane"], "DEEP_MTM")
        self.assertEqual(rec["tableBytes"], 12)
        self.assertGreaterEqual(rec["indexLikeBytes"], 2)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabDeepSegmentTests(unittest.TestCase):
    def test_build_verify_ready_2(self) -> None:
        pre = hashlib.sha256((GEN31 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN31),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN31 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 2)
        self.assertEqual(pack["n_open_dark_input"], 26)
        self.assertEqual(pack.get("n_police_hold"), 20)
        self.assertTrue(pack.get("hold_generation_apply"))
        lanes = pack["recoveryLaneCounts"]
        self.assertEqual(sum(lanes.values()), 2)
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN31),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)


if __name__ == "__main__":
    unittest.main()
