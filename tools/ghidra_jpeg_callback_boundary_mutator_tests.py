#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUTATOR = ROOT / "tools/GhidraApplyJpegCallbackBoundaries.java"


class JpegCallbackBoundaryMutatorSourceTests(unittest.TestCase):
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
            "removeFunction(",
        )
        for token in forbidden:
            self.assertNotIn(token, self.source)
        self.assertEqual(self.source.count("manager.createFunction("), 1)
        self.assertIn('"namesAuthorized\\\": false', self.source)
        self.assertIn('"metadataAuthorized\\\": false', self.source)

    def test_manifest_and_exact_current_pre_are_frozen(self) -> None:
        self.assertIn(
            "6253c29d77e6676f2843ca8adf3d9c52b4b4fa86f088f6086ea00b90dde89fd6",
            self.source,
        )
        self.assertIn(
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
            self.source,
        )
        for name, value in (
            ("PRE_FUNCTIONS", 8280),
            ("POST_FUNCTIONS", 8304),
            ("PRE_INSTRUCTIONS", 550991),
            ("POST_INSTRUCTIONS", 551032),
            ("PRE_REFERENCES", 234495),
            ("POST_REFERENCES", 234484),
            ("TARGET_COUNT", 24),
            ("EXTERNAL_INSTRUCTIONS", 4497),
            ("GHIDRA_BODY_INSTRUCTIONS", 4497),
        ):
            self.assertRegex(self.source, rf"{name}\s*=\s*{value}")
        self.assertRegex(self.source, r"POST_COUNTS_PINNED\s*=\s*true")

    def test_half_open_ranges_and_restricted_disassembly_are_explicit(self) -> None:
        self.assertIn("Bounded disassembly is authorized only inside", self.source)
        self.assertIn("endExclusive.subtract(1)", self.source)
        self.assertIn("body.getMaxAddress().add(1)", self.source)
        self.assertIn("disassembler.disassemble(seeds, target.body, true)", self.source)
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
            "JPEG_CALLBACK_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "JPEG_CALLBACK_BOUNDARIES_POST_INNER_ROLLBACK_REQUESTED",
            "JPEG_CALLBACK_BOUNDARIES_FORCED_POST_INNER_FAILURE",
            "JPEG_CALLBACK_BOUNDARIES_MUTATION_TAINTED",
        ):
            self.assertIn(marker, self.source)
        self.assertIn("outer_rollback_required=true", self.source)
        self.assertIn("validateReferenceDelta(referencesBeforeSnapshot", self.source)

    def test_receipts_are_create_new_and_local_lab_contained(self) -> None:
        self.assertIn("requireNewOutput(args[1]", self.source)
        self.assertIn("requireNewOutput(args[2]", self.source)
        self.assertIn("StandardOpenOption.CREATE_NEW", self.source)
        self.assertIn('new File(repository, "local-lab")', self.source)
        self.assertIn("output.toPath().startsWith(labRoot.toPath())", self.source)
        self.assertIn("ready.toPath().startsWith(labRoot.toPath())", self.source)
        self.assertIn('"bea.ghidra.jpeg-callback-boundaries.v1"', self.source)
        self.assertIn("relativePosix(repository, tool)", self.source)
        self.assertIn("relativePosix(repository, manifest)", self.source)
        self.assertIn("relativePosix(repository, output)", self.source)
        self.assertIn(".replace(File.separatorChar, '/')", self.source)

    def test_correction_and_classifications_are_pinned(self) -> None:
        for token in (
            "LIBJPEG6B__h2v2_smooth_downsample",
            "0x005b6800-0x005b6a86",
            "0x005b68fe",
            "0x005b6900",
            "0fb600",
            "0a80e595125a7d0c3a7315fee988d9135ecdc5c3e1c7183ee123f6822dfafbaf",
            "e61d6a793b42951d4e466a18683567c9011cd840b03559c0cc9e94c761995098",
        ):
            self.assertIn(token, self.source)
        self.assertIn("getDefinedDataContaining(fixedPoint) == null", self.source)
        self.assertIn("getFunctionAt(fixedPoint) == null", self.source)
        self.assertIn("getInstructionAt(fixedPoint) == null", self.source)
        self.assertIn("containing.getMinAddress().equals(instructionStart)", self.source)

    def test_full_pre_rows_and_outside_code_are_protected(self) -> None:
        self.assertIn("validatePostSnapshot(before, targets)", self.source)
        self.assertIn("non-target function changed at", self.source)
        self.assertIn("instruction outside admitted bodies changed at", self.source)
        self.assertIn("reference outside admitted bodies changed", self.source)


if __name__ == "__main__":
    unittest.main()
