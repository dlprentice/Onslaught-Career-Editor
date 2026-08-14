#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/ghidra_crt_eh_parent_range_scratch_authority.py"
PACKAGE = ROOT / "local-lab/crt-eh-parent-repair-db18616-20260814-v1/formal"
RECEIPT = PACKAGE / "authority/scratch-authority.ready.json"
MANIFEST = ROOT / (
    "reverse-engineering/binary-analysis/"
    "crt-eh-parent-range-repair-2026-08-14.tsv"
)
REPORT = ROOT / (
    "reverse-engineering/binary-analysis/"
    "crt-eh-parent-range-ghidra-scratch-admission-2026-08-14.md"
)

sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOL.parent))
import ghidra_crt_eh_parent_range_scratch_authority as authority


class CrtEhParentRangeScratchAuthorityTests(unittest.TestCase):
    def test_frozen_authority_identity_and_contract(self) -> None:
        self.assertEqual(TOOL.stat().st_size, 29882)
        self.assertEqual(
            authority.sha256_file(TOOL),
            "05ba09c84968caeee677feb4a6162ec1697c0706c2a2495cd17c187f3e777c0c",
        )
        self.assertEqual(
            authority.MANIFEST_SHA256,
            "272062f47b6ef2c45a29e1bbe07a0f186ac1ae6ad8259bfd4f0a3d33edcf8831",
        )
        self.assertEqual(authority.PRE_COUNTS["functions"], 8327)
        self.assertEqual(authority.POST_COUNTS["bodyRanges"], 8457)
        self.assertEqual(authority.POST_COUNTS["ownedBytes"], 1811443)
        self.assertEqual(authority.POST_COUNTS["references"], 234478)
        self.assertEqual(authority.DEFAULT_PACKAGE, PACKAGE)

    def test_tracked_manifest_reproduces_the_frozen_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "static/final-a/fragment-manifest.tsv"
            destination.parent.mkdir(parents=True)
            destination.write_bytes(MANIFEST.read_bytes())
            result = authority.validate_manifest(root)
            self.assertEqual(result["bytes"], 464)
            self.assertEqual(result["sha256"], authority.MANIFEST_SHA256)

    def test_saved_campaign_and_sealed_receipt_reproduce(self) -> None:
        if not PACKAGE.is_dir():
            self.skipTest("ignored saved CRT EH scratch evidence is absent")
        self.assertEqual(RECEIPT.stat().st_size, 3877)
        self.assertEqual(
            authority.sha256_file(RECEIPT),
            "3d472b734d4a3eeb19a896e713e1f2d2cc1dfbac5befcd66ef8c39ad0618eb82",
        )
        value = authority.verify_receipt(PACKAGE)
        self.assertEqual(
            value["tree"],
            {
                "bytes": 1518299333,
                "files": 283,
                "sha256": "bd7545cd76571ec9a6c20f6a981a0f7933e0a9d629ad7867ecdddf8c0c6a8a49",
            },
        )
        self.assertEqual(value["claims"]["unchangedFunctionRows"], 8326)
        self.assertFalse(value["claims"]["liveMutationAuthorized"])

    def test_receipt_claims_are_structural_not_semantic_promotion(self) -> None:
        if not RECEIPT.is_file():
            self.skipTest("ignored sealed authority receipt is absent")
        value = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(value["status"], "SEALED_SCRATCH_READY_LIVE_FORBIDDEN")
        self.assertEqual(value["policy"], "LIVE_FORBIDDEN")
        self.assertEqual(value["claims"]["newFunctionEntriesAuthorized"], 0)
        self.assertEqual(value["claims"]["forbiddenEntries"], ["0x005d0ad6", "0x005d0aea"])

    def test_report_binds_scope_receipt_and_limits(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for marker in (
            "3d472b734d4a3eeb19a896e713e1f2d2cc1dfbac5befcd66ef8c39ad0618eb82",
            "bd7545cd76571ec9a6c20f6a981a0f7933e0a9d629ad7867ecdddf8c0c6a8a49",
            "0x0060C170",
            "0x0060D170",
            "8,326",
            "LIVE_FORBIDDEN",
            "does not settle the parent's\nsignature debt",
        ):
            self.assertIn(marker, report)


if __name__ == "__main__":
    unittest.main()
