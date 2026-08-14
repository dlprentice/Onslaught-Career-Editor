#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_crt_p0_boundary_scratch_authority_v2 as authority


class GhidraCrtP0BoundaryScratchAuthorityV2Tests(unittest.TestCase):
    def test_corrected_formal_campaign_reproduces_semantically(self) -> None:
        if not (authority.LANE / "main-8b9-compatibility.json").is_file():
            self.skipTest("ignored completed v2 campaign is absent")
        self.assertEqual(
            authority.verify_campaign(),
            {
                "demoNormalizedCfgTwins": 23,
                "demoRawTwins": 6,
                "demoEntryDeltaRows": 23,
                "demoEntryDeltaProjectionBytes": 4672,
                "demoEntryDeltaProjectionSha256":
                    "abcdeea9ed0d8db95075bc0d7e6bd0869f0331a70c42958ef909f98e4265907a",
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

    def test_every_retained_boundary_column_is_semantically_checked(self) -> None:
        if not authority.LANE.is_dir():
            self.skipTest("ignored v2 evidence is absent")
        manifest, _ = authority.verify_inputs()
        source = authority.LANE / "runs/formal-replica-a-readback/boundaries.tsv"
        rows = authority.read_tsv(source)
        self.assertEqual(tuple(rows[0]), authority.BOUNDARY_COLUMNS)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "boundaries.tsv"
            for column in authority.BOUNDARY_COLUMNS:
                changed = [dict(row) for row in rows]
                changed[0][column] = "HOSTILE_FIELD_DRIFT"
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=authority.BOUNDARY_COLUMNS,
                                            delimiter="\t", lineterminator="\n")
                    writer.writeheader()
                    writer.writerows(changed)
                with self.assertRaises(authority.AuthorityError, msg=column):
                    authority.verify_boundaries(path, "readback", manifest)

    def test_ready_receipt_rejects_extra_or_changed_fields(self) -> None:
        if not authority.LANE.is_dir():
            self.skipTest("ignored v2 evidence is absent")
        run = "formal-replica-a-readback"
        source = authority.LANE / "runs" / run / "boundaries.ready.json"
        value = authority.read_json(source)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ready.json"
            for mutation in (
                {**value, "borrowedDemoClaim": True},
                {**value, "bodyBytes": 1132},
                {**value, "counts": {**value["counts"], "targets": 22}},
            ):
                path.write_text(json.dumps(mutation), encoding="utf-8")
                with self.assertRaises(authority.AuthorityError):
                    authority.verify_ready(path, "readback", run,
                                           authority.READBACK_EXPORTS["boundaries.tsv"])

    def test_v1_evidence_is_preserved_exactly(self) -> None:
        if not authority.V1_LANE.is_dir():
            self.skipTest("ignored v1 evidence is absent")
        self.assertEqual(authority.tree_identity(authority.V1_LANE), authority.V1_TREE)

    def test_explicit_verify_requires_saved_v2_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.ready.json"
            with mock.patch.object(authority, "READY", missing):
                with self.assertRaisesRegex(authority.AuthorityError,
                                            "saved authority receipt missing"):
                    authority.verify()

    def test_authority_pins_v2_schema_and_mutation_boundary(self) -> None:
        self.assertEqual(authority.SCHEMA,
                         "bea.ghidra.crt-p0-boundary-scratch-authority.v2")
        self.assertEqual(authority.COMPATIBLE_COMMIT,
                         "8b9e376e86c543ec5f8fce554b8a3e3b09579484")
        self.assertEqual(authority.DEMO_PROJECTION, (
            4672,
            "abcdeea9ed0d8db95075bc0d7e6bd0869f0331a70c42958ef909f98e4265907a",
        ))
        self.assertIn("borrowed JPEG", authority.CLAIMS[1])
        self.assertIn("Live and tracked Ghidra promotion remain forbidden",
                      authority.CLAIMS[-1])


if __name__ == "__main__":
    unittest.main()
