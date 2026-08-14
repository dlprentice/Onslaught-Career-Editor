#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUTATOR = ROOT / "tools/GhidraApplyExternalTableGapBoundaries.java"


class ExternalTableGapBoundaryMutatorSourceTests(unittest.TestCase):
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
        self.assertNotIn("manager.removeFunction(", self.source)
        self.assertIn('"namesAuthorized\\\": false', self.source)
        self.assertIn('"metadataAuthorized\\\": false', self.source)

    def test_manifest_and_current_pre_are_frozen(self) -> None:
        self.assertIn(
            "4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f",
            self.source,
        )
        self.assertIn(
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
            self.source,
        )
        for name, value in (
            ("PRE_FUNCTIONS", 8201),
            ("POST_FUNCTIONS", 8280),
            ("PRE_INSTRUCTIONS", 550982),
            ("PRE_REFERENCES", 234537),
            ("TARGET_COUNT", 79),
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
            "EXTERNAL_TABLE_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "EXTERNAL_TABLE_GAP_BOUNDARIES_POST_INNER_ROLLBACK_REQUESTED",
            "EXTERNAL_TABLE_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE",
            "EXTERNAL_TABLE_GAP_BOUNDARIES_MUTATION_TAINTED",
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
        self.assertIn('"bea.ghidra.external-table-gap-boundaries.v2"', self.source)
        self.assertIn("relativePosix(repository, tool)", self.source)
        self.assertIn("relativePosix(repository, manifest)", self.source)
        self.assertIn("relativePosix(repository, output)", self.source)
        self.assertIn("relativePosix(repository, consumedProof)", self.source)
        self.assertIn(".replace(File.separatorChar, '/')", self.source)

    def test_rank_identity_and_consumed_proof_contracts_are_pinned(self) -> None:
        for token in (
            'equal("P0 row count", 12',
            'equal("P1 row count", 20',
            'equal("P2 row count", 47',
            "D3DX_COMPAT__CCodecYUVFamily__SharedScalarDeletingDtor",
            "D3DX_SHARED_YUV_CODEC_DTOR_LINEAGE",
            "D3DX_COMPAT__c_D3DXVec4Cross",
            "alreadyPreparedReceipt",
            "VEC4_RECEIPT_SHA256",
        ):
            self.assertIn(token, self.source)

    def test_formal_post_counts_are_pinned(self) -> None:
        self.assertRegex(self.source, r"POST_INSTRUCTIONS\s*=\s*[1-9][0-9]*")
        self.assertRegex(self.source, r"POST_REFERENCES\s*=\s*[1-9][0-9]*")
        self.assertRegex(self.source, r"POST_COUNTS_PINNED\s*=\s*true")


if __name__ == "__main__":
    unittest.main()
