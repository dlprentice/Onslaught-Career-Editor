#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/GhidraApplyD3dxGapBoundaries.java"
MANIFEST = (
    ROOT
    / "reverse-engineering/binary-analysis/"
    "d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv"
)
RECONCILIATION = (
    ROOT
    / "reverse-engineering/binary-analysis/"
    "d3dx-gap-cohort-current-reconciliation-2026-08-14.tsv"
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def range_digest(text: str) -> str:
    digest = hashlib.sha256()
    for item in text.split(";"):
        start, end = (int(value, 0) for value in item.split("-"))
        digest.update(f"{start:08x}:{end - 1:08x};".encode("ascii"))
    return digest.hexdigest()


class GhidraD3dxGapBoundaryMutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.manifest = rows(MANIFEST)
        cls.reconciliation = {
            row["pcStart"]: row for row in rows(RECONCILIATION)
        }

    def test_manifest_is_exact_two_boundary_projection(self) -> None:
        self.assertEqual(len(self.manifest), 2)
        self.assertEqual(
            [row["entry"] for row in self.manifest],
            ["0x00595fc9", "0x00596028"],
        )
        self.assertEqual(sum(int(row["expectedBodyBytes"]) for row in self.manifest), 248)
        self.assertEqual(
            sum(int(row["expectedInstructionCount"]) for row in self.manifest), 92
        )
        self.assertTrue(
            all(
                row["currentState"] == "ABSENT_FROM_CURRENT_8280_FUNCTION_CENSUS"
                and row["promotionLane"] == "D3DX_GAP_TWO_SCRATCH_ONLY"
                for row in self.manifest
            )
        )
        self.assertEqual(MANIFEST.stat().st_size, 608)
        self.assertEqual(
            hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            "2d8f16415206538d0377fafe70c210bf8de65b442e2162ad5f5909d01c21fefd",
        )

    def test_every_structural_field_matches_current_reconciliation(self) -> None:
        for manifest in self.manifest:
            current = self.reconciliation[manifest["entry"]]
            self.assertEqual(current["currentDisposition"],
                             "STATIC_BOUNDARY_REPRODUCED_NOT_ADMITTED")
            self.assertEqual(manifest["expectedBodyBytes"], current["bytes"])
            self.assertEqual(
                manifest["expectedInstructionCount"], current["instructionCount"]
            )
            self.assertEqual(manifest["expectedBodyBytesSha256"], current["bodySha256"])
            self.assertEqual(manifest["expectedRangeDigest"],
                             range_digest(manifest["expectedRanges"]))
            start, end = manifest["expectedRanges"].split("-")
            self.assertEqual(start, manifest["entry"])
            self.assertEqual(end, current["pcEndExclusive"])

    def test_source_pins_exact_current_pre_and_measured_post(self) -> None:
        for declaration in (
            "PRE_FUNCTIONS = 8280", "POST_FUNCTIONS = 8282",
            "PRE_INSTRUCTIONS = 550991", "POST_INSTRUCTIONS = 550991",
            "PRE_REFERENCES = 234495", "POST_REFERENCES = 234495",
            "TARGET_COUNT = 2", "MANIFEST_BYTES = 608",
        ):
            self.assertIn(declaration, self.source)
        self.assertIn(
            "2d8f16415206538d0377fafe70c210bf8de65b442e2162ad5f5909d01c21fefd",
            self.source,
        )
        self.assertIn('Set.of("0x00595fc9", "0x00596028")', self.source)
        self.assertIn("validatePostSnapshot(before, targets)", self.source)
        self.assertIn("validateInstructionDelta(instructionsBeforeSnapshot", self.source)
        self.assertIn("validateReferenceDelta(referencesBeforeSnapshot", self.source)

    def test_mutation_is_structural_and_body_bounded_only(self) -> None:
        for forbidden in (
            ".setName(", ".setSignature(", ".setComment(",
            ".setRepeatableComment(", ".setCallingConvention(",
            ".setReturnType(", ".setParameters(", ".addTag(",
            "createData(", "removeData(", "clearListing(",
        ):
            self.assertNotIn(forbidden, self.source, forbidden)
        self.assertIn("manager.createFunction(", self.source)
        self.assertIn("body.contains(", self.source)
        self.assertIn("SourceType.DEFAULT", self.source)
        self.assertIn("authorizedBodies.contains(", self.source)

    def test_outputs_and_adverse_modes_fail_closed(self) -> None:
        self.assertIn("requireNewOutput", self.source)
        self.assertIn("Files.createLink", self.source)
        self.assertIn(
            "receipts must stay inside this repository's local-lab tree",
            self.source,
        )
        self.assertRegex(
            self.source,
            re.compile(r'"probe-after-one".*"probe-post-inner"', re.S),
        )
        self.assertIn("D3DX_GAP_BOUNDARIES_MUTATION_TAINTED", self.source)
        self.assertIn("OUTER_ROLLBACK_AND_SEPARATE_READBACK_REQUIRED", self.source)
        self.assertIn("RESTORE_VERIFIED_SCRATCH_BASE", self.source)


if __name__ == "__main__":
    unittest.main()
