#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen28 open-dark unit-split generation reducer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen28_open_dark_unit_split_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen28_open_dark_unit_split_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

PARENT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation27-tiny-fragment-20260805-v1"
    / "generation-27-residual-terminal-tiny-fragment"
)
OUT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation28-open-dark-unit-split-20260805-v1"
    / "generation-28-residual-terminal-open-dark-unit-split"
)
PACK = (
    ROOT
    / "local-lab"
    / "open-residual-gen27-open-dark-unit-split-20260805-v1"
    / "FORMAL-PACK.json"
)
HAS_LAB = PARENT.is_dir()


class ConstantsTests(unittest.TestCase):
    def test_partition(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 24)
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 58)
        self.assertEqual(mod.EXPECTED_AMBIG, 968)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGen28Tests(unittest.TestCase):
    def test_apply_verify_parent_unmutated(self) -> None:
        pre = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        # ensure pack exists
        if not PACK.is_file():
            inst = importlib.util.spec_from_file_location(
                "inst",
                ROOT / "tools" / "re_open_residual_gen27_open_dark_unit_split.py",
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
        self.assertEqual(ready["generation"], 28)
        self.assertEqual(ready["counts"]["residualOpenDark"], 58)
        self.assertEqual(ready["counts"]["openDarkClosedThisGeneration"], 24)
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
        post2 = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post2)


if __name__ == "__main__":
    unittest.main()
