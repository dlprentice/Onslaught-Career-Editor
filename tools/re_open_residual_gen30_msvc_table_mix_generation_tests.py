#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen30 MSVC table-mix generation reducer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen30_msvc_table_mix_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen30_msvc_table_mix_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

PARENT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation29-pad-peel-sandwich-20260805-v1"
    / "generation-29-residual-terminal-pad-peel-sandwich"
)
OUT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation30-msvc-table-mix-20260805-v1"
    / "generation-30-residual-terminal-msvc-table-mix"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen29-msvc-table-mix-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = PARENT.is_dir()


class ConstantsTests(unittest.TestCase):
    def test_partition(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 10)
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 30)
        self.assertEqual(mod.EXPECTED_AMBIG, 996)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGen30Tests(unittest.TestCase):
    def test_apply_verify_parent_unmutated(self) -> None:
        pre = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        if not PACK.is_file():
            inst = importlib.util.spec_from_file_location(
                "inst", ROOT / "tools" / "re_open_residual_gen29_msvc_table_mix.py"
            )
            assert inst and inst.loader
            m = importlib.util.module_from_spec(inst)
            inst.loader.exec_module(m)
            m.main(
                [
                    "build",
                    "--campaign",
                    str(PARENT),
                    "--specimen",
                    str(
                        ROOT
                        / "local-lab"
                        / "safe-copy-bea-pristine"
                        / "BEA.exe.original.backup"
                    ),
                    "--out",
                    str(PACK.parent),
                ]
            )
        rc = mod.main(
            [
                "apply",
                "--parent",
                str(PARENT),
                "--formal-pack",
                str(PACK),
                "--out",
                str(OUT),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((OUT / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 30)
        self.assertEqual(ready["counts"]["residualOpenDark"], 30)
        self.assertEqual(ready["counts"]["openDarkClosedThisGeneration"], 10)
        rc2 = mod.main(
            [
                "verify",
                "--campaign",
                str(OUT),
                "--formal-pack",
                str(PACK),
                "--parent",
                str(PARENT),
            ]
        )
        self.assertEqual(rc2, 0)


if __name__ == "__main__":
    unittest.main()
