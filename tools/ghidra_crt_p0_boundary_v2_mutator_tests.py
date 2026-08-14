#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/GhidraApplyCrtP0BoundariesV2.java"
MANIFEST = ROOT / "reverse-engineering/binary-analysis/crt-runtime-p0-function-boundaries-2026-08-14.tsv"
SOURCE_COHORT_SHA256 = "bc16df601740afec41bdba306d7e02996171da1cc10d3491da38d6d022bdbf5a"


class GhidraCrtP0BoundaryV2MutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE.read_text(encoding="utf-8")
        with MANIFEST.open("r", encoding="utf-8", newline="") as stream:
            cls.rows = list(csv.DictReader(stream, delimiter="\t"))

    def test_manifest_is_exact_23_row_boundary_only_cohort(self) -> None:
        self.assertEqual(len(self.rows), 23)
        entries = [row["entry"] for row in self.rows]
        self.assertEqual(entries, sorted(entries))
        self.assertEqual(len(set(entries)), 23)
        self.assertEqual(sum(int(row["expectedBodyBytes"]) for row in self.rows), 1131)
        self.assertEqual(sum(len(row["expectedRanges"].split(";")) for row in self.rows), 24)
        self.assertEqual(sum(int(row["expectedInstructionCount"]) for row in self.rows), 312)
        self.assertTrue(all(row["contractIds"] == "BOUNDARY_ONLY" for row in self.rows))
        self.assertTrue(all(row["promotionLane"] == "CRT22_P0_SCRATCH_ONLY" for row in self.rows))
        self.assertEqual(
            hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            "c60359ecfd58e7c97c45a45e1b83d034e6cc104c222781f6f611e158b459d7df",
        )

    def test_protected_entries_and_thunk_are_pinned(self) -> None:
        entries = {row["entry"] for row in self.rows}
        for entry in ("0x00542720", "0x005d0ad6", "0x005d0aea", "0x005b8500"):
            self.assertNotIn(entry, entries)
            self.assertIn(entry, self.source.lower())
        thunk = next(row for row in self.rows if row["entry"] == "0x0045ac20")
        self.assertEqual(thunk["expectedIsThunk"], "true")
        self.assertEqual(thunk["expectedThunkTarget"], "0x0045ac30")
        self.assertIn('getThunkedFunction(false)', self.source)
        self.assertIn('equals("0x0045ac30")', self.source)

    def test_source_pins_run_c_and_exact_pre_post_counts(self) -> None:
        self.assertIn('"bea.ghidra.crt-p0-boundaries.v2"', self.source)
        self.assertIn(SOURCE_COHORT_SHA256, self.source)
        for declaration in (
            "PRE_FUNCTIONS = 8280", "POST_FUNCTIONS = 8303",
            "PRE_RANGES = 8400", "POST_RANGES = 8424",
            "BODY_BYTES = 1131", "BODY_RANGES = 24",
            "EXTERNAL_INSTRUCTIONS = 312", "GHIDRA_BODY_INSTRUCTIONS = 312",
        ):
            self.assertIn(declaration, self.source)
        self.assertIn("validatePostSnapshot(before, targets)", self.source)
        self.assertIn("validateInstructionDelta(instructionsBeforeSnapshot, authorizedBodies)", self.source)
        self.assertIn("validateReferenceDelta(referencesBeforeSnapshot, authorizedBodies)", self.source)

    def test_no_semantic_or_data_definition_mutator_is_present(self) -> None:
        forbidden_calls = (
            ".setName(", ".setSignature(", ".setComment(",
            ".setRepeatableComment(", ".setCallingConvention(",
            ".setReturnType(", ".setParameters(", ".addTag(",
            "createData(", "clearListing(", "removeData(",
        )
        for call in forbidden_calls:
            self.assertNotIn(call, self.source, call)
        self.assertIn("manager.createFunction(", self.source)
        self.assertIn("listing.clearCodeUnits(", self.source)
        self.assertIn("target.body.contains(", self.source)
        self.assertIn("SourceType.DEFAULT", self.source)

    def test_structural_receipt_has_no_borrowed_jpeg_evidence_columns(self) -> None:
        for field in (
            "providerIdentity", "identityGrade", "sourceFile", "sourceLine",
            "cfgEdgeCount", "cfgSha256", "normalizedSha256", "demoEntry",
            "demoDelta", "demoRawEqual", "terminalKinds", "peerEntryTransfers",
        ):
            self.assertNotIn(field, self.source)
        for field in (
            "expectedIsThunk", "actualIsThunk", "expectedThunkTarget",
            "actualThunkTarget", "forbiddenEntries", "residualEntityKey",
            "contractId", "promotionLane",
        ):
            self.assertIn(field, self.source)

    def test_create_new_local_lab_publication_and_failure_modes_are_required(self) -> None:
        self.assertIn("requireNewOutput", self.source)
        self.assertIn("Files.createLink", self.source)
        self.assertIn("receipts must stay inside this repository's local-lab tree", self.source)
        self.assertRegex(self.source, re.compile(r'"probe-after-one".*"probe-post-inner"', re.S))
        self.assertIn("CRT_P0_BOUNDARIES_MUTATION_TAINTED", self.source)


if __name__ == "__main__":
    unittest.main()
