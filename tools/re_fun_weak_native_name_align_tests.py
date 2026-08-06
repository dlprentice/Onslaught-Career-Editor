#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for WEAK FUN native name align (script-table-144)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_fun_weak_native_name_align.py"
SPEC = importlib.util.spec_from_file_location("re_fun_weak_native_name_align", TOOL)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

TABLE = ROOT / "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv"
PARENT = (
    ROOT
    / "local-lab"
    / "function-native-name-align-generation34-20260805-v1"
    / "generation-34-function-native-name-align"
)
HAS_LAB = TABLE.is_file() and PARENT.is_dir()


class UnitWeakTests(unittest.TestCase):
    def test_none_rejected(self) -> None:
        self.assertFalse(mod.is_real_native_name("None"))
        self.assertTrue(mod.is_real_native_name("Damage"))

    def test_table_load_structure(self) -> None:
        if not TABLE.is_file():
            self.skipTest("table missing")
        t = mod.load_script_table(TABLE)
        self.assertEqual(len(t), 144)
        self.assertIn("0x005348c0", t)
        self.assertEqual(t["0x005348c0"]["shippedName"], "Damage")


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabWeakTests(unittest.TestCase):
    def test_build_ready_15(self) -> None:
        out = ROOT / "local-lab" / "fun-weak-native-name-align-20260805-v1"
        rc = mod.main(
            ["build", "--campaign", str(PARENT), "--table", str(TABLE), "--out", str(out)]
        )
        self.assertEqual(rc, 0)
        self.assertEqual(mod.main(["verify", "--plate", str(out)]), 0)


if __name__ == "__main__":
    unittest.main()
