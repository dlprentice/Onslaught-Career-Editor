#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_text_gap_boundary_scratch_authority as authority


class TextGapBoundaryScratchAuthorityTests(unittest.TestCase):
    def test_preserved_formal_campaign_reproduces_semantically(self) -> None:
        if not authority.LANE.is_dir():
            self.skipTest("ignored saved scratch evidence is absent")
        self.assertEqual(
            authority.verify_campaign(),
            {
                "targets": 31,
                "bodyBytes": 14049,
                "preFunctions": 8170,
                "postFunctions": 8201,
                "preInstructions": 549872,
                "postInstructions": 550982,
                "newInstructions": 1110,
                "preReferences": 234357,
                "postReferences": 234537,
                "newReferences": 180,
                "preservedPreFunctionRows": 8170,
                "replicas": 2,
                "adverseControls": 2,
                "externalPathPreflights": 2,
            },
        )

    def test_explicit_verify_still_requires_saved_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.ready.json"
            with mock.patch.object(authority, "READY", missing):
                with self.assertRaisesRegex(authority.AuthorityError, "invalid JSON"):
                    authority.verify()

    def test_full_pre_row_gate_checks_every_field(self) -> None:
        header = "address\tname\tsignature\n"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.tsv"
            after = root / "after.tsv"
            before.write_text(header + "0x1\tname\tvoid f(void)\n", encoding="utf-8")
            after.write_text(header + "0x1\tname\tint f(void)\n", encoding="utf-8")
            with (
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 1),
            ):
                with self.assertRaisesRegex(authority.AuthorityError, "full PRE row drift"):
                    authority.verify_full_pre_rows_equal(before, after, "fixture")

    def test_receipt_paths_are_repository_relative_posix(self) -> None:
        authority.verify_portable_path("local-lab/run/output.tsv", "local-lab/run/output.tsv", "fixture")
        for value in ("C:/absolute/output.tsv", "local-lab\\run\\output.tsv", "/root/output.tsv"):
            with self.assertRaises(authority.AuthorityError):
                authority.verify_portable_path(value, value, "fixture")

    def test_program_parser_rejects_duplicate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "program.tsv"
            path.write_text("metric\tvalue\nfunctions\t8170\nfunctions\t8201\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "bad program row"):
                authority.program_rows(path)

    def test_exact_stamp_rejects_one_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "artifact.bin"
            path.write_bytes(b"exact")
            expected = (path.stat().st_size, authority.sha256_file(path))
            authority.verify_stamp(path, expected, "fixture")
            path.write_bytes(b"drift")
            with self.assertRaisesRegex(authority.AuthorityError, "SHA-256 drift"):
                authority.verify_stamp(path, expected, "fixture")

    def test_payload_keeps_live_and_tracked_mutation_unauthorized(self) -> None:
        with (
            mock.patch.object(authority, "verify_campaign", return_value={"targets": 31}),
            mock.patch.object(authority, "artifact_tree", return_value={"fileCount": 1}),
            mock.patch.object(
                authority,
                "stamp",
                return_value={"path": "fixture", "bytes": 1, "sha256": "0" * 64},
            ),
        ):
            payload = authority.build_payload("2026-08-14T00:00:00Z")
        self.assertEqual(payload["verdict"], "SCRATCH_ADMISSION_READY_LIVE_NOT_AUTHORIZED")
        self.assertIs(payload["liveMutationAuthorized"], False)
        self.assertIs(payload["trackedGhidraMutationAuthorized"], False)

    def test_authority_pins_exact_db_18611(self) -> None:
        self.assertEqual(
            authority.DB_18611,
            (
                68288512,
                "6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce",
            ),
        )


if __name__ == "__main__":
    unittest.main()
