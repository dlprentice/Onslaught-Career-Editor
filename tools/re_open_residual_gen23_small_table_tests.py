#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_residual_gen23_small_table.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen23_small_table.py"
SPEC = importlib.util.spec_from_file_location("re_open_residual_gen23_small_table", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN23 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation23-partial-data-20260805-v1"
    / "generation-23-residual-terminal-partial-data"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen23-small-table-20260805-v1"
HAS_LAB = GEN23.is_dir() and SPECIMEN.is_file()


class PolicyTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 125)
        self.assertEqual(mod.EXPECTED_OPEN_EXECUTED, 4)
        self.assertEqual(mod.MIN_TABLE_BYTES, 16)
        self.assertEqual(mod.MAX_TABLE_BYTES_EXCL, 32)
        self.assertEqual(mod.ADVANCE_KIND, "RESIDUAL_TERMINAL_OPEN_SMALL_TABLE.v1")


class ComposeUnitTests(unittest.TestCase):
    def test_code_ptr_run_min_basic(self) -> None:
        # four .text dwords at align 0
        blob = b"".join(
            (0x401000 + i * 0x10).to_bytes(4, "little") for i in range(4)
        )
        got = mod.code_ptr_run_min(blob, min_dwords=4)
        self.assertEqual(got, (0, 16))

    def test_code_ptr_rejects_non_text(self) -> None:
        blob = b"\x00\x00\x00\x00" * 4
        self.assertIsNone(mod.code_ptr_run_min(blob, min_dwords=4))

    def test_code_ptr_rejects_short(self) -> None:
        blob = b"".join((0x401000 + i).to_bytes(4, "little") for i in range(3))
        self.assertIsNone(mod.code_ptr_run_min(blob, min_dwords=4))

    def test_index_after_small_table_rejects_bulk_remainder(self) -> None:
        """rest > max(cpr,32) must not compose even if index_full would accept."""
        import types

        table = b"".join((0x401000 + i * 4).to_bytes(4, "little") for i in range(5))  # 20B
        bulk = bytes([0x01] * 100)
        blob = table + bulk
        # fake pd_mod that always accepts index / rejects short tail / pad
        class PD:
            @staticmethod
            def index_full_or_none(rest, md, mass):
                return len(rest) == 100

            @staticmethod
            def short_data_tail_ok(rest, md, mass):
                return False

            @staticmethod
            def compose_partial_data(*a, **k):
                return None

        class DS:
            @staticmethod
            def compose_data_shape(*a, **k):
                return None

            @staticmethod
            def leading_pad_len(rest, mass, inb):
                return 0

        class Mass:
            @staticmethod
            def is_pure_pad(b):
                return False

        class Inb:
            @staticmethod
            def is_full_align_nop_run(b):
                return False

        class Large:
            pass

        class Md:
            pass

        got = mod.compose_small_table(
            blob, 0x401000, Md(), Mass(), Inb(), Large(), DS(), PD()
        )
        self.assertIsNone(got)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabPlateTests(unittest.TestCase):
    def test_published_plate_file_pins(self) -> None:
        """Historical Gen24 plate pins; rebuild may drop INDEX-bulk after gate harden."""
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("plate missing")
        pre = hashlib.sha256((GEN23 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_hard_mismatches"], 0)
        self.assertEqual(pack["n_proofs"], 47)
        self.assertEqual(pack["n_executed_proofs"], 0)
        terms = pack["proposedTerminalStateCounts"]
        self.assertEqual(terms.get("TERMINAL_DATA"), 2)
        self.assertEqual(terms.get("TERMINAL_BOUNDED_AMBIGUITY"), 45)
        for p in pack["proofs"]:
            self.assertIn(
                p["proposed"]["terminalState"],
                {"TERMINAL_DATA", "TERMINAL_BOUNDED_AMBIGUITY"},
            )
            self.assertEqual(p["sourceState"], "OPEN_DARK_RESIDUAL")
            tb = int(p.get("tableBytes") or 0)
            self.assertGreaterEqual(tb, 16)
            self.assertLess(tb, 32)
        post = hashlib.sha256((GEN23 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)


if __name__ == "__main__":
    unittest.main()
