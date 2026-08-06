#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen27 tiny-fragment generation reducer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen27_tiny_fragment_generation.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen27_tiny_fragment_generation", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

PARENT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation26-unit-split-20260805-v1"
    / "generation-26-residual-terminal-unit-split"
)
OUT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation27-tiny-fragment-20260805-v1"
    / "generation-27-residual-terminal-tiny-fragment"
)
PACK = ROOT / "local-lab" / "open-residual-gen26-tiny-fragment-20260805-v1" / "FORMAL-PACK.json"
HAS_LAB = PARENT.is_dir() and PACK.is_file() and OUT.is_dir()


class ConstantsTests(unittest.TestCase):
    def test_partition(self) -> None:
        self.assertEqual(mod.EXPECTED_PROOFS, 16)
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 82)
        self.assertEqual(mod.EXPECTED_AMBIG, 944)
        self.assertEqual(mod.EXPECTED_OPEN_EXEC, 0)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabGen27Tests(unittest.TestCase):
    def test_verify_and_parent_unmutated(self) -> None:
        pre = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
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
        self.assertEqual(rc, 0)
        post = hashlib.sha256((PARENT / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        ready = json.loads((OUT / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 27)
        self.assertEqual(ready["counts"]["residualOpenDark"], 82)
        self.assertEqual(ready["counts"]["openDarkClosedThisGeneration"], 16)


if __name__ == "__main__":
    unittest.main()
