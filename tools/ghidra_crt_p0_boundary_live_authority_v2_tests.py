#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the completed CRT23 P0 live authority."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_crt_p0_boundary_live_authority_v2 as authority


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_REPO = Path(os.environ.get("BEA_CRT23_LIVE_EVIDENCE_REPO", ROOT))
LIVE_PROJECT = Path(os.environ.get(
    "BEA_LIVE_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects"
))
PRE_BACKUP = Path(os.environ.get(
    "BEA_CRT23_PRE_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-pre-live-v2",
))
POST_BACKUP = Path(os.environ.get(
    "BEA_CRT23_POST_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-post-live-v2",
))


def config() -> authority.Config:
    return authority.Config(
        repo=EVIDENCE_REPO.resolve(),
        live_project=LIVE_PROJECT.resolve(strict=False),
        pre_backup=PRE_BACKUP.resolve(strict=False),
        post_backup=POST_BACKUP.resolve(strict=False),
        output=(EVIDENCE_REPO / authority.LIVE_LANE_REL / authority.RECEIPT_NAME).resolve(strict=False),
    )


class PureContractTests(unittest.TestCase):
    def test_authority_tool_identity_is_frozen(self) -> None:
        tool = ROOT / "tools/ghidra_crt_p0_boundary_live_authority_v2.py"
        self.assertEqual(tool.stat().st_size, 57301)
        self.assertEqual(
            authority.sha256_file(tool),
            "1fe983fb208fb1634cad360ae7a4b13a59ee95f11177c960ad1f6a22a7629eb8",
        )

    def test_exact_transition_contract(self) -> None:
        self.assertEqual(authority.POLICY, "LIVE_PROMOTION_VERIFIED")
        self.assertEqual((authority.PRE_FUNCTIONS, authority.POST_FUNCTIONS), (8304, 8327))
        self.assertEqual((authority.PRE_RANGES, authority.POST_RANGES), (8434, 8458))
        self.assertEqual((authority.PRE_OWNED, authority.POST_OWNED), (1810287, 1811418))
        self.assertEqual((authority.PRE_INSTRUCTIONS, authority.POST_INSTRUCTIONS), (551055, 551133))
        self.assertEqual((authority.PRE_REFERENCES, authority.POST_REFERENCES), (234467, 234478))
        self.assertEqual(authority.POST_FUNCTIONS - authority.PRE_FUNCTIONS, authority.TARGETS)
        self.assertEqual(authority.POST_OWNED - authority.PRE_OWNED, authority.BODY_BYTES)
        self.assertEqual(authority.POST_RANGES - authority.PRE_RANGES, authority.BODY_RANGES)

    def test_repo_input_stamps_are_current(self) -> None:
        for relative, expected in authority.EXPECTED_REPO_INPUTS.items():
            path = ROOT / relative
            self.assertEqual((path.stat().st_size, authority.sha256_file(path)), expected, relative)

    def test_manifest_is_exact_23_entry_cohort(self) -> None:
        rows = authority.load_targets(ROOT / authority.MANIFEST_REL)
        self.assertEqual(len(rows), 23)
        self.assertEqual(sum(int(row["expectedBodyBytes"]) for row in rows), 1131)
        self.assertEqual(sum(int(row["expectedInstructionCount"]) for row in rows), 312)
        self.assertEqual(sum(len(row["expectedRanges"].split(";")) for row in rows), 24)
        self.assertEqual(sum(row["expectedIsThunk"] == "true" for row in rows), 1)
        self.assertEqual(rows[0]["entry"], "0x004010e0")
        self.assertEqual(rows[-1]["entry"], "0x005d0c12")

    def test_project_digest_requires_order(self) -> None:
        value = {"files": [
            {"relative_path": "a", "size": 1, "sha256": "1" * 64},
            {"relative_path": "b", "size": 2, "sha256": "2" * 64},
        ]}
        raw = (("1" * 64) + "\t1\ta\n" + ("2" * 64) + "\t2\tb\n").encode()
        self.assertEqual(authority.project_digest(value), hashlib.sha256(raw).hexdigest())
        value["files"].reverse()
        with self.assertRaisesRegex(authority.AuthorityError, "ordered"):
            authority.project_digest(value)

    def test_rotation_rejects_common_file_drift(self) -> None:
        empty = hashlib.sha256(b"").hexdigest()
        pre = {
            "projectName": "BEA", "fileCount": 3, "totalBytes": 3,
            "structurallyComplete": True,
            "files": sorted([
                {"relative_path": "BEA.gpr", "size": 0, "sha256": empty},
                {"relative_path": authority.PRE_OLD_DB_PATH, "size": authority.DB_18614[0], "sha256": authority.DB_18614[1]},
                {"relative_path": authority.STABLE_DB_PATH, "size": authority.DB_18615[0], "sha256": authority.DB_18615[1]},
            ], key=lambda row: row["relative_path"]),
        }
        post = json.loads(json.dumps(pre))
        post["files"] = [row for row in post["files"] if row["relative_path"] != authority.PRE_OLD_DB_PATH]
        post["files"].append({"relative_path": authority.POST_ROLLING_DB_PATH, "size": authority.DB_18616[0], "sha256": authority.DB_18616[1]})
        post["files"].sort(key=lambda row: row["relative_path"])
        post["totalBytes"] = 4
        pre_summary = authority.project_summary(pre)
        post_summary = authority.project_summary(post)
        with mock.patch.dict(authority.PRE_PROJECT, pre_summary, clear=True), mock.patch.dict(authority.POST_PROJECT, post_summary, clear=True):
            result = authority.validate_transition(pre, post)
            self.assertEqual(result["removed"], [authority.PRE_OLD_DB_PATH])
            post["files"][0]["sha256"] = "drift"
            with self.assertRaises(authority.AuthorityError):
                authority.validate_transition(pre, post)

    def test_portability_and_create_new_are_fail_closed(self) -> None:
        authority.ensure_portable({"path": "local-lab/evidence.json"})
        with self.assertRaisesRegex(authority.AuthorityError, "absolute path"):
            authority.ensure_portable({"path": r"C:\secret\receipt.json"})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "receipt.json"
            authority.atomic_new_json(target, {"status": "READY"})
            with self.assertRaisesRegex(authority.AuthorityError, "already exists"):
                authority.atomic_new_json(target, {"status": "DRIFT"})

    def test_exact_directory_census_rejects_extra_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a").mkdir()
            authority.exact_directory_entries(
                root, expected_files=(), expected_directories={"a"}, label="synthetic"
            )
            (root / "unexpected").mkdir()
            with self.assertRaisesRegex(authority.AuthorityError, "directory set"):
                authority.exact_directory_entries(
                    root, expected_files=(), expected_directories={"a"}, label="synthetic"
                )

    def test_exact_comparison_rejects_hidden_difference(self) -> None:
        clean = {
            "matches": True, "extraCount": 0, "hashDiffCount": 0,
            "missingCount": 0, "sizeDiffCount": 0, "extra": [],
            "hashDifferences": [], "missing": [], "sizeDifferences": [],
        }
        authority.require_exact_comparison(clean, "synthetic")
        changed = dict(clean)
        changed["matches"] = False
        with self.assertRaisesRegex(authority.AuthorityError, "comparison"):
            authority.require_exact_comparison(changed, "synthetic")


class RetainedEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        current = config()
        if not current.output or not current.output.is_file():
            self.skipTest("retained CRT23 live authority is absent")
        if not current.live_project.is_dir() or not current.pre_backup.is_dir() or not current.post_backup.is_dir():
            self.skipTest("live or backup project evidence is absent")

    def test_saved_authority_replays_without_project_mutation(self) -> None:
        current = config()
        live_before = authority.project_summary(authority.project_value(current.live_project))
        tracked_before = authority.project_summary(authority.project_value(current.tracked_project))
        receipt_before = authority.stamp(current.output, "saved receipt")
        authority.verify(current)
        self.assertEqual(live_before, authority.project_summary(authority.project_value(current.live_project)))
        self.assertEqual(tracked_before, authority.project_summary(authority.project_value(current.tracked_project)))
        self.assertEqual(receipt_before, authority.stamp(current.output, "saved receipt"))

    def test_saved_authority_is_portable_and_exact(self) -> None:
        current = config()
        saved = authority.load_json(current.output, "saved authority")
        authority.ensure_portable(saved)
        self.assertEqual(saved["schemaVersion"], authority.SCHEMA)
        self.assertEqual(saved["ceremony"]["saveCount"], 1)
        self.assertEqual(saved["ceremony"]["functionDelta"]["unchangedRowsExact"], 8304)
        self.assertEqual(saved["accounting"]["ownedBytes"], 1811418)
        self.assertEqual(saved["projects"]["post"]["canonicalInventorySha256"], authority.POST_PROJECT["canonicalInventorySha256"])


if __name__ == "__main__":
    unittest.main()
