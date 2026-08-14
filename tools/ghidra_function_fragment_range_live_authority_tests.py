#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the five-range live-promotion preparation authority."""

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

import ghidra_function_fragment_range_live_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = Path.home() / "source/Onslaught-Career-Editor"
EVIDENCE = Path(os.environ.get(
    "BEA_FUNCTION_FRAGMENT_EVIDENCE_REPO",
    DEFAULT_EVIDENCE if DEFAULT_EVIDENCE.is_dir() else ROOT,
))
LIVE_PROJECT = Path(os.environ.get(
    "BEA_LIVE_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects"
))
LIVE_LANE = EVIDENCE / authority.LIVE_LANE_REL
PRE_BACKUP = Path(os.environ.get(
    "BEA_FUNCTION_FRAGMENT_PRE_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-function-fragment5-ranges-pre-live",
))
POST_BACKUP = Path(os.environ.get(
    "BEA_FUNCTION_FRAGMENT_POST_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-function-fragment5-ranges-post-live",
))


def config(output: Path | None = None) -> authority.Config:
    return authority.Config(
        ROOT.resolve(),
        EVIDENCE.resolve(),
        LIVE_PROJECT.resolve(),
        LIVE_LANE.resolve(strict=False),
        PRE_BACKUP.resolve(strict=False),
        POST_BACKUP.resolve(strict=False),
        output.resolve(strict=False) if output is not None else None,
    )


class PureContractTests(unittest.TestCase):
    def test_authority_tool_identity_is_frozen(self) -> None:
        tool = ROOT / "tools/ghidra_function_fragment_range_live_authority.py"
        self.assertEqual(tool.stat().st_size, 68331)
        self.assertEqual(
            authority.sha256_file(tool),
            "bc6c7fdc9ee9a19ccff0c437166dbde2b08b98a7bcd78b4d3ca7a46de0cab30c",
        )

    def test_exact_pre_post_contract(self) -> None:
        self.assertEqual(authority.POLICY, "PREPARATION_ONLY")
        self.assertEqual(authority.BASE_COMMIT, "add5571c0779287f2e575c371e477cd33872662c")
        self.assertEqual(
            (authority.PRE_FUNCTIONS, authority.POST_FUNCTIONS), (8280, 8280)
        )
        self.assertEqual((authority.PRE_RANGES, authority.POST_RANGES), (8400, 8396))
        self.assertEqual((authority.PRE_OWNED, authority.POST_OWNED), (1794212, 1795470))
        self.assertEqual(
            (authority.PRE_INSTRUCTIONS, authority.POST_INSTRUCTIONS),
            (550991, 551014),
        )
        self.assertEqual(
            (authority.PRE_REFERENCES, authority.POST_REFERENCES),
            (234495, 234478),
        )
        self.assertEqual(authority.POST_OWNED - authority.PRE_OWNED, 1258)
        self.assertEqual(set(authority.POST_BODY_ROWS), set(authority.scratch.TARGETS))

    def test_repo_input_stamps_are_current(self) -> None:
        for relative, expected in authority.EXPECTED_REPO_INPUTS.items():
            path = ROOT / relative
            self.assertEqual(
                (path.stat().st_size, authority.sha256_file(path)),
                expected,
                relative,
            )

    def test_target_manifest_is_exact_five(self) -> None:
        rows = authority.load_targets(ROOT / authority.MANIFEST_REL)
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum(int(row["repair_bytes"]) for row in rows), 1258)
        self.assertEqual(
            sum(int(row["repair_instruction_count"]) for row in rows), 325
        )
        self.assertEqual(
            rows[0]["repair_ranges"], "0x0046282b-0x00462b64"
        )

    def test_post_body_rows_close_exact_accounting(self) -> None:
        target_bytes = sum(
            int(row[3])
            for rows in authority.POST_BODY_ROWS.values()
            for row in rows
        )
        self.assertEqual(target_bytes, 8946)
        self.assertEqual(authority.TEXT_BYTES - authority.POST_OWNED, 133647)
        self.assertEqual(authority.POST_BODY_RANGES_STAMP[0], 1197803)
        for rows in authority.POST_BODY_ROWS.values():
            for start, maximum, end, size, digest in rows:
                self.assertEqual(int(end, 16) - int(start, 16), int(size))
                self.assertEqual(int(maximum, 16) + 1, int(end, 16))
                self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_project_digest_canonicalization(self) -> None:
        value = {
            "files": [
                {"relative_path": "a", "size": 1, "sha256": "1" * 64},
                {"relative_path": "b", "size": 2, "sha256": "2" * 64},
            ]
        }
        raw = (("1" * 64) + "\t1\ta\n" + ("2" * 64) + "\t2\tb\n").encode()
        self.assertEqual(authority.project_digest(value), hashlib.sha256(raw).hexdigest())
        value["files"].reverse()
        with self.assertRaisesRegex(authority.AuthorityError, "ordered"):
            authority.project_digest(value)

    def test_post_transition_allows_only_expected_rotation(self) -> None:
        pre = {
            "projectName": "BEA",
            "fileCount": 3,
            "totalBytes": 12,
            "structurallyComplete": True,
            "files": [
                {"relative_path": authority.PRE_OLD_DB_PATH, "size": 1, "sha256": "a"},
                {"relative_path": authority.PRE_STABLE_DB_PATH,
                 "size": authority.DB_18613[0], "sha256": authority.DB_18613[1]},
                {"relative_path": "BEA.gpr", "size": 0,
                 "sha256": hashlib.sha256(b"").hexdigest()},
            ],
        }
        post = json.loads(json.dumps(pre))
        post["files"] = [
            row for row in post["files"]
            if row["relative_path"] != authority.PRE_OLD_DB_PATH
        ]
        post["files"].append({
            "relative_path": authority.POST_ROLLING_DB_PATH,
            "size": 2,
            "sha256": "b",
        })
        post["files"].sort(key=lambda row: row["relative_path"])
        pre["files"].sort(key=lambda row: row["relative_path"])
        with mock.patch.dict(authority.PRE_PROJECT, {"fileCount": 3}):
            result = authority.validate_post_transition(pre, post, "synthetic")
        self.assertEqual(result["removed"], [authority.PRE_OLD_DB_PATH])
        self.assertEqual(result["added"], [authority.POST_ROLLING_DB_PATH])
        post["files"][0]["sha256"] = "drift"
        with mock.patch.dict(authority.PRE_PROJECT, {"fileCount": 3}):
            with self.assertRaises(authority.AuthorityError):
                authority.validate_post_transition(pre, post, "synthetic")

    def test_backup_manifest_accepts_copy_receipt_shape(self) -> None:
        project = {
            "projectName": "BEA",
            "fileCount": 1,
            "totalBytes": 0,
            "structurallyComplete": True,
            "files": [{
                "relative_path": "BEA.gpr",
                "size": 0,
                "sha256": hashlib.sha256(b"").hexdigest(),
            }],
        }
        receipt = {
            "schemaVersion": authority.project_backup.SCHEMA_VERSION,
            "createdAtUtc": "2026-08-14T00:00:00Z",
            "sourceStable": True,
            "copyComparison": {"matches": True},
            "source": project,
            "destination": project,
            "readonlyOpen": None,
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "backup_manifest.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            authority.validate_backup_manifest(path, project, "synthetic backup")
            receipt["copyComparison"]["matches"] = False
            path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "copy comparison"):
                authority.validate_backup_manifest(path, project, "synthetic backup")

    def test_portability_and_create_new_receipt_fail_closed(self) -> None:
        authority.ensure_portable({"path": "local-lab/evidence.json"})
        with self.assertRaisesRegex(authority.AuthorityError, "absolute path"):
            authority.ensure_portable({"path": r"C:\secret\receipt.json"})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "receipt.json"
            authority.atomic_new_json(target, {"status": "READY"})
            self.assertEqual(json.loads(target.read_text()), {"status": "READY"})
            with self.assertRaisesRegex(authority.AuthorityError, "overwrite"):
                authority.atomic_new_json(target, {"status": "DRIFT"})

    def test_tree_identity_detects_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a").write_bytes(b"one")
            first = authority.tree_identity(root)
            (root / "a").write_bytes(b"two")
            second = authority.tree_identity(root)
            self.assertEqual(first["fileCount"], second["fileCount"])
            self.assertEqual(first["totalBytes"], second["totalBytes"])
            self.assertNotEqual(first["treeSha256"], second["treeSha256"])


class RetainedEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        if os.environ.get("BEA_RUN_FUNCTION_FRAGMENT_LIVE_PREP_EVIDENCE") != "1":
            self.skipTest("set BEA_RUN_FUNCTION_FRAGMENT_LIVE_PREP_EVIDENCE=1")
        if not (EVIDENCE / authority.SCRATCH_RECEIPT_REL).is_file():
            self.skipTest("retained scratch evidence is absent")

    def test_preflight_proves_current_pre_without_writes(self) -> None:
        current = config()
        self.assertFalse(current.live_lane.exists())
        self.assertFalse(current.pre_backup.exists())
        self.assertFalse(current.post_backup.exists())
        live_before = authority.project_value(current.live_project)
        tracked_before = authority.project_value(current.tracked_project)
        result = authority.preflight(current)
        live_after = authority.project_value(current.live_project)
        tracked_after = authority.project_value(current.tracked_project)
        self.assertEqual(
            authority.project_without_root(live_before),
            authority.project_without_root(live_after),
        )
        self.assertEqual(
            authority.project_without_root(tracked_before),
            authority.project_without_root(tracked_after),
        )
        self.assertEqual(result["policy"], "PREPARATION_ONLY")
        self.assertEqual(result["verdict"], "PREPARATION_READY_MUTATION_NOT_AUTHORIZED")
        self.assertEqual(result["blocker"], "FUTURE_CEREMONY_ARTIFACTS_DO_NOT_EXIST")
        self.assertFalse(result["futureMutationAuthorized"])
        self.assertEqual(result["scratchAuthority"]["fullTree"], authority.SCRATCH_TREE)

    def test_future_phase_refuses_absent_ceremony(self) -> None:
        with self.assertRaises((authority.AuthorityError, OSError)):
            authority.build_live_phase(config())

    def test_post_projection_is_predetermined_by_scratch_post(self) -> None:
        inventory = (
            EVIDENCE / authority.SCRATCH_PORTABLE_REL
            / "inventories/final-replica-a/functions.tsv"
        )
        raw = authority.name_projection.projection_bytes(
            inventory,
            expected_inventory_sha256=authority.POST_FUNCTIONS_STAMP[1],
            source_label=authority.PROJECTION_SOURCE,
            projection_date="2026-08-14",
            specimen_sha256=authority.PROGRAM_SHA256,
        )
        self.assertEqual(
            (len(raw), hashlib.sha256(raw).hexdigest()),
            authority.POST_PROJECTION_STAMP,
        )


if __name__ == "__main__":
    unittest.main()
