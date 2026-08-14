#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUTATOR = ROOT / "tools/GhidraApplyCrtEhParentRange.java"
MANIFEST = ROOT / (
    "reverse-engineering/binary-analysis/"
    "crt-eh-parent-range-repair-2026-08-14.tsv"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CrtEhParentRangeMutatorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = MUTATOR.read_text(encoding="utf-8")
        with MANIFEST.open(encoding="utf-8", newline="") as stream:
            cls.rows = list(csv.DictReader(stream, delimiter="\t"))

    def test_frozen_mutator_and_manifest_identities(self) -> None:
        self.assertEqual(MUTATOR.stat().st_size, 49382)
        self.assertEqual(
            sha256_file(MUTATOR),
            "bc9f18ff6e67d1cb7c41b9c5b5d108732af5598a062425ef36c53f93f2aba1e9",
        )
        self.assertEqual(MANIFEST.stat().st_size, 464)
        self.assertEqual(
            sha256_file(MANIFEST),
            "272062f47b6ef2c45a29e1bbe07a0f186ac1ae6ad8259bfd4f0a3d33edcf8831",
        )

    def test_exact_current_pre_and_measured_post_are_frozen(self) -> None:
        for name, value in (
            ("PRE_FUNCTIONS", 8327),
            ("PRE_BODY_RANGES", 8458),
            ("PRE_OWNED_BYTES", 1811418),
            ("PRE_INSTRUCTIONS", 551133),
            ("PRE_REFERENCES", 234478),
            ("POST_FUNCTIONS", 8327),
            ("POST_BODY_RANGES", 8457),
            ("POST_OWNED_BYTES", 1811443),
            ("POST_INSTRUCTIONS", 551143),
            ("POST_REFERENCES", 234478),
            ("TARGET_COUNT", 1),
            ("REPAIR_BYTES", 25),
            ("REPAIR_INSTRUCTIONS", 10),
        ):
            self.assertRegex(self.source, rf"{name}\s*=\s*{value}")
        self.assertIn('"bea.ghidra.crt-eh-parent-range-repair.v1"', self.source)
        self.assertIn('private static final String POLICY = "LIVE_FORBIDDEN";', self.source)

    def test_only_existing_parent_body_and_bounded_listing_are_mutated(self) -> None:
        for token in (
            "createFunction(",
            "setName(",
            "setComment(",
            "setRepeatableComment(",
            "addTag(",
            "setCallingConvention(",
            "replaceParameters(",
            "setReturnType(",
            "createData(",
            "setBytes(",
            "addMemoryReference(",
            "removeFunction(",
        ):
            self.assertNotIn(token, self.source)
        self.assertEqual(self.source.count("owner.setBody(target.postBody);"), 1)
        self.assertEqual(self.source.count("listing.clearCodeUnits("), 1)
        self.assertIn("target.repair.contains(", self.source)
        self.assertIn(
            "disassembler.disassemble(new AddressSet(seed, seed), target.repair, true)",
            self.source,
        )
        self.assertIn("instructionCoverage(target.repair).hasSameAddresses", self.source)

    def test_manifest_is_one_exact_parent_repair(self) -> None:
        self.assertEqual(
            self.rows,
            [
                {
                    "entry": "0x005d0a9f",
                    "current_name": "CRT__LongJmpProbe_NoOp",
                    "pre_body_ranges": "0x005d0a9f-0x005d0ad6;0x005d0aef-0x005d0b04",
                    "repair_ranges": "0x005d0ad6-0x005d0aef",
                    "post_body_ranges": "0x005d0a9f-0x005d0b04",
                    "repair_bytes": "25",
                    "repair_sha256": "e4be71ffc2e3b62db42a6ae7cedc791eaeb8f7c8c05e986bf0ece195613f414a",
                    "repair_instruction_count": "10",
                    "repair_instruction_layout_sha256": "4b9994ab4ef5418af4737cf919d43132d4b072bd96a585ba52da834e1dfacc1c",
                    "mutation_scope": "BODY_RANGE_AND_BOUNDED_DISASSEMBLY_ONLY",
                }
            ],
        )
        self.assertIn('"0x005d0ad6", "0x005d0aea"', self.source)

    def test_collateral_state_guards_are_explicit(self) -> None:
        for marker in (
            'equal("target metadata at "',
            'equal("non-target function at "',
            'equal("instructions outside repair"',
            'equal("references outside repair"',
            'equal("defined data"',
            'equal("stored non-function symbols"',
            'equal("comments"',
            'equal("memory"',
        ):
            self.assertIn(marker, self.source)
        self.assertIn('"newFunctionsAuthorized\\": false', self.source)
        self.assertIn('"namesSignaturesCommentsTagsDataAuthorized\\": false', self.source)

    def test_modes_containment_and_restore_requirement_are_explicit(self) -> None:
        for mode in ("dry", "probe-after-one", "probe-after-all", "apply", "readback"):
            self.assertIn(f'"{mode}"', self.source)
        self.assertIn("requireNewOutput(packageRoot, args[1]", self.source)
        self.assertIn("requireNewOutput(packageRoot, args[2]", self.source)
        self.assertIn("StandardOpenOption.CREATE_NEW", self.source)
        self.assertIn("output.toPath().startsWith(packageRoot.toPath())", self.source)
        self.assertIn("RESTORE_VERIFIED_SCRATCH_BASE_REQUIRED", self.source)


if __name__ == "__main__":
    unittest.main()
