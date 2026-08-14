#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_jpeg_callback_boundary_scratch_authority as authority


class JpegCallbackBoundaryScratchAuthorityTests(unittest.TestCase):
    def test_preserved_formal_campaign_reproduces_semantically(self) -> None:
        if not authority.LANE.is_dir():
            self.skipTest("ignored saved scratch evidence is absent")
        self.assertEqual(
            authority.verify_campaign(),
            {
                "targets": 24,
                "bodyBytes": 14817,
                "bodyRanges": 38,
                "externalInstructions": 4497,
                "ghidraBodyInstructions": 4497,
                "cfgEdges": 4745,
                "demoNormalizedTwins": 24,
                "demoRawTwins": 14,
                "preFunctions": 8280,
                "postFunctions": 8304,
                "preservedPreFunctionRows": 8280,
                "instructionDelta": 41,
                "referenceDelta": -11,
                "replicas": 2,
                "adverseControls": 2,
                "externalPathPreflights": 2,
                "readonlyRestoreProofs": 1,
                "current8280OverlapBytes": 0,
                "pairwiseOverlapBytes": 0,
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
        authority.verify_portable_path("local-lab/run/output.tsv", "fixture")
        for value in (
            "C:/absolute/output.tsv",
            "local-lab\\run\\output.tsv",
            "/root/output.tsv",
            "local-lab/../output.tsv",
        ):
            with self.assertRaisesRegex(authority.AuthorityError, "repository-relative POSIX"):
                authority.verify_portable_path(value, "fixture")

    def test_program_parser_rejects_duplicate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "program.tsv"
            path.write_text("metric\tvalue\nfunctions\t8280\nfunctions\t8304\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "invalid or duplicate"):
                authority.program_rows(path)

    def test_full_pre_row_gate_checks_every_field(self) -> None:
        header = (
            "address\tname\tnameSource\tsigSource\tbodyBytes\tbodyRanges\tinstrCount\t"
            "paramCount\tisThunk\tnoReturn\tcommentPresent\trepeatableCommentPresent\t"
            "tagCount\tsignature\n"
        )
        before_row = "0x00401000\tFUN_00401000\tDEFAULT\tDEFAULT\t5\t1\t2\t0\tfalse\tfalse\tfalse\tfalse\t0\tvoid f(void)\n"
        created_row = "0x005b6800\tFUN_005b6800\tDEFAULT\tDEFAULT\t646\t1\t203\t0\tfalse\tfalse\tfalse\tfalse\t0\tvoid f(void)\n"
        manifest = [{
            "retail_va": "0x005B6800",
            "body_bytes": "646",
            "body_range_count": "1",
            "instruction_count": "203",
        }]
        with tempfile.TemporaryDirectory() as temporary:
            lane = Path(temporary)
            before = lane / "runs/base-inventory/functions.tsv"
            after = lane / "runs/formal-replica-a-readback/functions.tsv"
            before.parent.mkdir(parents=True)
            after.parent.mkdir(parents=True)
            before.write_text(header + before_row, encoding="utf-8")
            after.write_text(header + before_row + created_row, encoding="utf-8")
            with (
                mock.patch.object(authority, "LANE", lane),
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 2),
                mock.patch.object(authority, "verify_stamp"),
            ):
                authority.verify_function_preservation(manifest)
                after.write_text(
                    header + before_row.replace("void f(void)", "int f(void)") + created_row,
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(authority.AuthorityError, "PRE function row changed"):
                    authority.verify_function_preservation(manifest)

    def test_payload_pins_correction_project_and_mutation_boundary(self) -> None:
        generic_stamp = {"path": "fixture", "bytes": 1, "sha256": "0" * 64}
        with (
            mock.patch.object(authority, "verify_campaign", return_value={"targets": 24}),
            mock.patch.object(authority, "artifact_tree", return_value={"fileCount": 1}),
            mock.patch.object(authority, "stamp", return_value=generic_stamp),
        ):
            payload = authority.build_payload("2026-08-14T00:00:00Z")
            authority.verify_payload(payload)
            for field, replacement, message in (
                ("correction", {**payload["correction"], "fixedPointIsData": True}, "correction"),
                ("preProject", {**payload["preProject"], "files": 18}, "PRE project"),
                ("preDatabase", {**payload["preDatabase"], "name": "db.18612.gbf"}, "PRE database"),
            ):
                changed = copy.deepcopy(payload)
                changed[field] = replacement
                with self.assertRaisesRegex(authority.AuthorityError, message):
                    authority.verify_payload(changed)
        self.assertEqual(payload["verdict"], "SCRATCH_READY_LIVE_FORBIDDEN")
        self.assertIs(payload["liveMutationAuthorized"], False)
        self.assertIs(payload["trackedGhidraMutationAuthorized"], False)

    def test_authority_pins_exact_current_project_and_db(self) -> None:
        self.assertEqual(
            authority.BASE_PROJECT,
            (
                19,
                186960773,
                "ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2",
            ),
        )
        self.assertEqual(
            authority.DB_18613,
            (
                68337664,
                "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
            ),
        )


if __name__ == "__main__":
    unittest.main()
