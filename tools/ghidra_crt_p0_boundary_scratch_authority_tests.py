#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_crt_p0_boundary_scratch_authority as authority


class GhidraCrtP0BoundaryScratchAuthorityTests(unittest.TestCase):
    def test_preserved_formal_campaign_reproduces_semantically(self) -> None:
        if not authority.LANE.is_dir():
            self.skipTest("ignored saved scratch evidence is absent")
        self.assertEqual(
            authority.verify_campaign(),
            {
                "targets": 23, "bodyRanges": 24, "bodyBytes": 1131,
                "bodyInstructions": 312, "preFunctions": 8280,
                "postFunctions": 8303, "preFunctionRanges": 8400,
                "postFunctionRanges": 8424, "preservedPreFunctionRows": 8280,
                "instructionDelta": 78, "referenceDelta": 11,
                "replicas": 2, "rollbackControls": 2,
                "containmentControls": 2, "readonlyRestoreProofs": 1,
                "current8280OverlapBytes": 0, "pairwiseOverlapBytes": 0,
            },
        )

    def test_explicit_verify_requires_saved_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.ready.json"
            with mock.patch.object(authority, "READY", missing):
                with self.assertRaisesRegex(authority.AuthorityError, "saved authority receipt missing"):
                    authority.verify()

    def test_exact_stamp_rejects_one_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "artifact.bin"
            path.write_bytes(b"exact")
            expected = (path.stat().st_size, authority.sha256_file(path))
            authority.verify_stamp(path, expected, "fixture")
            path.write_bytes(b"drift")
            with self.assertRaisesRegex(authority.AuthorityError, "stamp drift"):
                authority.verify_stamp(path, expected, "fixture")

    def test_receipt_paths_are_repository_relative_posix(self) -> None:
        authority.portable("local-lab/run/output.tsv", "fixture")
        for value in ("C:/output.tsv", "local-lab\\output.tsv", "/root/out", "local-lab/../out"):
            with self.assertRaisesRegex(authority.AuthorityError, "repository-relative POSIX"):
                authority.portable(value, "fixture")

    def test_program_parser_rejects_duplicate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "program.tsv"
            path.write_text("metric\tvalue\nfunctions\t8280\nfunctions\t8303\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "invalid or duplicate"):
                authority.program_rows(path)

    def test_authority_pins_project_database_and_live_forbidden_boundary(self) -> None:
        self.assertEqual(authority.BASE_COMMIT, "1727d94ace29a60430d0982a188548d55aae5d1b")
        self.assertEqual(authority.BASE_PROJECT, (
            19, 186960773,
            "ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2",
        ))
        self.assertEqual(authority.DB_18613, (
            68337664,
            "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
        ))
        self.assertIn("Live and tracked Ghidra promotion remain forbidden", authority.CLAIMS[-1])


if __name__ == "__main__":
    unittest.main()
