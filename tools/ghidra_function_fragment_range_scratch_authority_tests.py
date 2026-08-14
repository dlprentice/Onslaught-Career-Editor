#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/ghidra_function_fragment_range_scratch_authority.py"
PACKAGE = ROOT / (
    "local-lab/ghidra-function-fragment5-range-scratch-20260814-v1/portable"
)
SEALED = PACKAGE / "authority/sealed-primary.ready.json"
REPORT = ROOT / (
    "reverse-engineering/binary-analysis/"
    "pc-function-body-fragment-ghidra-scratch-admission-2026-08-14.md"
)

sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOL.parent))
import ghidra_function_fragment_range_scratch_authority as authority


class FunctionFragmentRangeScratchAuthorityTests(unittest.TestCase):
    def test_frozen_authority_identity_and_contract(self) -> None:
        self.assertEqual(TOOL.stat().st_size, 24160)
        self.assertEqual(
            authority.sha256_file(TOOL),
            "1eed1350e38c4abbf840b2ae0fc1d444a4a818e154726c3a35ad347057f20678",
        )
        self.assertEqual(
            authority.MANIFEST_SHA256,
            "c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0",
        )
        self.assertEqual(authority.MUTATOR_SHA256, "fe845a9df094eff4a1d9b36c9d4a6b141f049356499016a20a673071d492ec4c")
        self.assertEqual(authority.STATIC_TOOL_SHA256, "a9e5f02e8dddfa64f50aca7821e3afed483de6c349e6ad0ada06ba77e59020ed")

    def test_preserved_formal_campaign_reproduces_semantically(self) -> None:
        if not PACKAGE.is_dir():
            self.skipTest("ignored saved scratch evidence is absent")
        static = authority.verify_static(PACKAGE)
        inventory = authority.verify_inventory_delta(PACKAGE)
        replicas = authority.verify_replicas_and_controls(PACKAGE)
        backup = authority.verify_backup(PACKAGE)
        tools = authority.verify_tools(PACKAGE)
        self.assertEqual(static["manifestRows"], 5)
        self.assertEqual(inventory["unchangedFunctionRows"], 8275)
        self.assertEqual(inventory["changedFunctionRows"], 5)
        self.assertEqual(
            {key: replicas[key] for key in (
                "positiveReplicas", "savedReadbacks", "adverseControls",
                "restoredPreReadbacks", "containmentRefusals",
            )},
            {
                "positiveReplicas": 2,
                "savedReadbacks": 2,
                "adverseControls": 2,
                "restoredPreReadbacks": 2,
                "containmentRefusals": 2,
            },
        )
        self.assertEqual(backup["readOnlyOpen"], "PASS")
        self.assertEqual(len(tools), 5)

    def test_exact_sealed_receipt_and_live_forbidden_verdict(self) -> None:
        if not SEALED.is_file():
            self.skipTest("ignored sealed authority receipt is absent")
        self.assertEqual(SEALED.stat().st_size, 9348)
        self.assertEqual(
            authority.sha256_file(SEALED),
            "a35f35ac99cd5d7251a86b7cf54c5aac2e2919870efca6566600045138571a04",
        )
        value = json.loads(SEALED.read_text(encoding="utf-8"))
        self.assertEqual(value["status"], "READY")
        self.assertEqual(value["verdict"], "STRICT_GO_FOR_LATER_TRACKED_PREPARATION")
        self.assertEqual(value["policy"], "LIVE_FORBIDDEN")
        self.assertEqual(
            value["repair"],
            {
                "addedBodyBytes": 1258,
                "bridgedPriorRangeComponents": 4,
                "existingFunctionsOnly": 5,
                "extendedSinglePriorComponent": 1,
                "newFunctions": 0,
                "postBodyRanges": 8396,
                "postFunctions": 8280,
                "postInstructions": 551014,
                "postOwnedBytes": 1795470,
                "postReferences": 234478,
            },
        )

    def test_report_binds_receipt_runtime_limits_and_nop_exclusion(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for marker in (
            "a35f35ac99cd5d7251a86b7cf54c5aac2e2919870efca6566600045138571a04",
            "431/825",
            "0/22",
            "14/28",
            "272/272",
            "0/111",
            "9/86",
            "0x00462B64..0x00462B70",
            "LIVE_FORBIDDEN",
        ):
            self.assertIn(marker, report)

    def test_exact_stamp_and_metric_parsers_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact = root / "artifact.bin"
            artifact.write_bytes(b"exact")
            authority.require_stamp(
                root,
                artifact.name,
                size=5,
                sha256=authority.sha256_file(artifact),
            )
            artifact.write_bytes(b"drift")
            with self.assertRaisesRegex(authority.AuthorityError, "hash drift"):
                authority.require_stamp(root, artifact.name, sha256="0" * 64)

            metrics = root / "metrics.tsv"
            metrics.write_text(
                "metric\tvalue\nfunctions\t8280\nfunctions\t8396\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(authority.AuthorityError, "duplicate metric"):
                authority.read_metrics(metrics)

    def test_receipt_normalization_removes_only_timestamp(self) -> None:
        value = {"completedAtUtc": "now", "mode": "apply", "policy": "LIVE_FORBIDDEN"}
        self.assertEqual(
            authority.normalized_receipt(value),
            {"mode": "apply", "policy": "LIVE_FORBIDDEN"},
        )


if __name__ == "__main__":
    unittest.main()
