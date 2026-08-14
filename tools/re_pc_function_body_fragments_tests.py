#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/re_pc_function_body_fragments.py"
MANIFEST = ROOT / (
    "reverse-engineering/binary-analysis/"
    "pc-function-body-fragment-repairs-2026-08-14.tsv"
)

sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOL.parent))
import re_pc_function_body_fragments as proof


class PcFunctionBodyFragmentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with MANIFEST.open(encoding="utf-8", newline="") as stream:
            cls.rows = list(csv.DictReader(stream, delimiter="\t"))

    def test_frozen_prover_and_manifest_identities(self) -> None:
        self.assertEqual(TOOL.stat().st_size, 28787)
        self.assertEqual(
            proof.sha256_file(TOOL),
            "a9e5f02e8dddfa64f50aca7821e3afed483de6c349e6ad0ada06ba77e59020ed",
        )
        self.assertEqual(MANIFEST.stat().st_size, 2878)
        self.assertEqual(
            proof.sha256_file(MANIFEST),
            "c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0",
        )

    def test_exact_five_existing_function_repairs_are_frozen(self) -> None:
        expected = (
            ("0x00462640", "0x0046282b-0x00462b64", 825, 217),
            ("0x0046ff10", "0x004700da-0x004700f0", 22, 4),
            ("0x00482590", "0x00482725-0x00482741", 28, 8),
            ("0x004be420", "0x004be82d-0x004be93d", 272, 60),
            ("0x00559410", "0x0055954c-0x005595bb", 111, 36),
        )
        actual = tuple(
            (
                row["entry"],
                row["repair_ranges"],
                int(row["repair_bytes"]),
                int(row["repair_instruction_count"]),
            )
            for row in self.rows
        )
        self.assertEqual(actual, expected)
        self.assertEqual(sum(row[2] for row in actual), 1258)
        self.assertEqual(sum(row[3] for row in actual), 325)
        self.assertEqual(
            {row["mutation_scope"] for row in self.rows},
            {"BODY_RANGE_AND_BOUNDED_DISASSEMBLY_ONLY"},
        )

    def test_prover_candidates_and_manifest_rows_match(self) -> None:
        self.assertEqual(len(proof.FRAGMENTS), 5)
        self.assertEqual(len(self.rows), 5)
        for fragment, row in zip(proof.FRAGMENTS, self.rows, strict=True):
            self.assertEqual(row["entry"], proof.va(fragment.owner))
            self.assertEqual(row["current_name"], fragment.name)
            self.assertEqual(
                row["repair_ranges"], proof.canonical_ranges((fragment.repair,))
            )
            self.assertEqual(
                row["post_body_ranges"], proof.canonical_ranges(fragment.post_ranges)
            )
            self.assertEqual(row["runtime_grade"], fragment.runtime_grade)

    def test_four_repairs_bridge_components_and_fep_excludes_twelve_nops(self) -> None:
        bridged = sum(
            len(fragment.pre_ranges) - len(fragment.post_ranges)
            for fragment in proof.FRAGMENTS
        )
        self.assertEqual(bridged, 4)
        fep = proof.FRAGMENTS[0]
        self.assertEqual(fep.repair_end, 0x00462B64)
        self.assertEqual(fep.envelope_end, 0x00462B70)
        self.assertEqual(fep.envelope_end - fep.repair_end, 12)
        self.assertEqual(self.rows[0]["post_body_ranges"], "0x00462640-0x00462b64")
        source = TOOL.read_text(encoding="utf-8")
        self.assertIn(
            'require(padding == b"\\x90" * 12, '
            '"FEP trailing alignment is not exact NOP padding")',
            source,
        )

    def test_merge_ranges_joins_only_touching_or_overlapping_components(self) -> None:
        self.assertEqual(
            proof.merge_ranges(((1, 3), (3, 5), (8, 10))),
            ((1, 5), (8, 10)),
        )
        with self.assertRaisesRegex(proof.ProofError, "empty range"):
            proof.merge_ranges(((3, 3),))


if __name__ == "__main__":
    unittest.main()
