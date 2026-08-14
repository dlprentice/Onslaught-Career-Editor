#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUTATOR = ROOT / "tools/GhidraApplyTextGapBoundaries.java"


class TextGapBoundaryMutatorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = MUTATOR.read_text(encoding="utf-8")

    def test_only_structural_admission_mutations_are_present(self) -> None:
        forbidden = (
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
        )
        for token in forbidden:
            self.assertNotIn(token, self.source)
        self.assertEqual(self.source.count("manager.createFunction("), 1)
        self.assertEqual(self.source.count("manager.removeFunction("), 1)
        self.assertIn('"namesAuthorized\\\": false', self.source)
        self.assertIn('"metadataAuthorized\\\": false', self.source)

    def test_manifest_and_current_pre_are_frozen(self) -> None:
        self.assertIn(
            "afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586",
            self.source,
        )
        self.assertIn(
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
            self.source,
        )
        for name, value in (
            ("PRE_FUNCTIONS", 8170),
            ("POST_FUNCTIONS", 8201),
            ("PRE_INSTRUCTIONS", 549872),
            ("POST_INSTRUCTIONS", 550982),
            ("PRE_REFERENCES", 234357),
            ("POST_REFERENCES", 234537),
            ("TARGET_COUNT", 31),
        ):
            self.assertRegex(self.source, rf"{name}\s*=\s*{value}")

    def test_half_open_ranges_and_restricted_disassembly_are_explicit(self) -> None:
        self.assertIn(
            "Bounded disassembly is authorized only inside", self.source
        )
        self.assertNotIn("No disassembly, name", self.source)
        self.assertIn("endExclusive.subtract(1)", self.source)
        self.assertIn("body.getMaxAddress().add(1)", self.source)
        self.assertIn(
            "disassembler.disassemble(seeds, target.body, true)", self.source
        )
        self.assertIn("instructionCoverage(target.body).hasSameAddresses", self.source)
        self.assertIn("new instruction escaped admitted bodies", self.source)
        self.assertIn("new reference escaped admitted bodies", self.source)

    def test_failure_modes_and_compensation_are_explicit(self) -> None:
        for mode in (
            "dry",
            "probe-after-one",
            "probe-post-inner",
            "apply",
            "readback",
        ):
            self.assertIn(f'"{mode}"', self.source)
        for marker in (
            "TEXT_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "TEXT_GAP_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE",
            "TEXT_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE",
            "TEXT_GAP_BOUNDARIES_MUTATION_TAINTED",
        ):
            self.assertIn(marker, self.source)
        self.assertIn("clearNewInstructions(instructionsBeforeSnapshot)", self.source)
        self.assertIn("referencesBeforeSnapshot, referenceSnapshot()", self.source)

    def test_receipts_are_create_new_and_local_lab_contained(self) -> None:
        self.assertIn("requireNewOutput(args[1]", self.source)
        self.assertIn("requireNewOutput(args[2]", self.source)
        self.assertIn("StandardOpenOption.CREATE_NEW", self.source)
        self.assertIn('new File(repository, "local-lab")', self.source)
        self.assertIn("output.toPath().startsWith(labRoot.toPath())", self.source)
        self.assertIn("ready.toPath().startsWith(labRoot.toPath())", self.source)
        self.assertIn('"bea.ghidra.text-gap-boundaries.v2"', self.source)
        self.assertIn("relativePosix(repository, tool)", self.source)
        self.assertIn("relativePosix(repository, manifest)", self.source)
        self.assertIn("relativePosix(repository, output)", self.source)
        self.assertIn(".replace(File.separatorChar, '/')", self.source)


if __name__ == "__main__":
    unittest.main()
