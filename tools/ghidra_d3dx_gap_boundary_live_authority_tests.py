#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the db.18617 D3DX two-boundary live authority."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_d3dx_gap_boundary_live_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = Path.home() / "source/Onslaught-Career-Editor"
EVIDENCE = Path(
    os.environ.get(
        "BEA_D3DX_GAP_TWO_EVIDENCE_REPO",
        DEFAULT_EVIDENCE if DEFAULT_EVIDENCE.is_dir() else ROOT,
    )
)
LIVE_PROJECT = Path(
    os.environ.get("BEA_LIVE_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects")
)
LIVE_LANE = EVIDENCE / authority.LIVE_LANE_REL
PRE_BACKUP = Path(
    os.environ.get(
        "BEA_D3DX_GAP_TWO_PRE_BACKUP",
        r"D:\BEA-Ghidra-Backups\2026-08-14-d3dx-gap-two-pre-live",
    )
)
POST_BACKUP = Path(
    os.environ.get(
        "BEA_D3DX_GAP_TWO_POST_BACKUP",
        r"D:\BEA-Ghidra-Backups\2026-08-14-d3dx-gap-two-post-live",
    )
)


def config(output: Path | None = None, *, repo: Path = ROOT) -> authority.Config:
    return authority.Config(
        repo.resolve(),
        EVIDENCE.resolve(),
        LIVE_PROJECT.resolve(),
        LIVE_LANE.resolve(strict=False),
        PRE_BACKUP.resolve(strict=False),
        POST_BACKUP.resolve(strict=False),
        output.resolve(strict=False) if output is not None else None,
    )


class PureContractTests(unittest.TestCase):
    def test_authority_tool_identity_is_frozen(self) -> None:
        tool = ROOT / "tools/ghidra_d3dx_gap_boundary_live_authority.py"
        self.assertEqual(tool.stat().st_size, 50_209)
        self.assertEqual(
            authority.sha256_file(tool),
            "41f214dfe779787baf7a032b3524ada0318217e185bac515fcc709d25aa59d8e",
        )

    def test_exact_pre_post_contract(self) -> None:
        self.assertEqual(authority.POLICY, "PREPARATION_ONLY")
        self.assertEqual(
            authority.BASE_COMMIT, "028edae969f9ffb92e2f73ae394cbcf282b9fed8"
        )
        self.assertEqual(
            (authority.prep.PRE_FUNCTIONS, authority.prep.POST_FUNCTIONS),
            (8327, 8329),
        )
        self.assertEqual(
            (authority.prep.PRE_RANGES, authority.prep.POST_RANGES),
            (8457, 8459),
        )
        self.assertEqual(
            (authority.prep.PRE_OWNED, authority.prep.POST_OWNED),
            (1811443, 1811691),
        )
        self.assertEqual(authority.prep.POST_OWNED - authority.prep.PRE_OWNED, 248)
        self.assertEqual(
            (authority.prep.PRE_INSTRUCTIONS, authority.prep.POST_INSTRUCTIONS),
            (551143, 551143),
        )
        self.assertEqual(
            (authority.prep.PRE_REFERENCES, authority.prep.POST_REFERENCES),
            (234478, 234478),
        )
        self.assertEqual(
            (authority.AGGREGATE_PRE_FUNCTIONS, authority.AGGREGATE_POST_FUNCTIONS),
            (8551, 8553),
        )

    def test_exact_two_default_targets(self) -> None:
        self.assertEqual(
            sorted(authority.prep.TARGETS), ["0x00595fc9", "0x00596028"]
        )
        self.assertEqual(
            sum(int(row["bytes"]) for row in authority.prep.TARGETS.values()), 248
        )
        self.assertEqual(
            sum(int(row["instructions"]) for row in authority.prep.TARGETS.values()),
            92,
        )
        self.assertEqual(
            {row["name"] for row in authority.prep.TARGETS.values()},
            {"FUN_00595fc9", "FUN_00596028"},
        )
        self.assertEqual(
            authority.BOUNDARY_STATUS,
            {"dry": "ready_absent", "apply": "created", "readback": "verified"},
        )

    def test_repo_input_stamps_are_current(self) -> None:
        for relative, expected in authority.EXPECTED_REPO_INPUTS.items():
            path = ROOT / relative
            self.assertEqual(
                (path.stat().st_size, authority.sha256_file(path)), expected, relative
            )

    def test_project_digest_canonicalization(self) -> None:
        value = {
            "files": [
                {"relative_path": "a", "size": 1, "sha256": "1" * 64},
                {"relative_path": "b", "size": 2, "sha256": "2" * 64},
            ]
        }
        raw = (("1" * 64) + "\t1\ta\n" + ("2" * 64) + "\t2\tb\n").encode()
        self.assertEqual(
            authority.prep.project_digest(value), hashlib.sha256(raw).hexdigest()
        )
        value["files"].reverse()
        with self.assertRaisesRegex(authority.prep.AuthorityError, "ordered"):
            authority.prep.project_digest(value)

    def test_post_transition_allows_only_expected_database_rotation(self) -> None:
        files = [
            {
                "relative_path": authority.PRE_OLD_DB_PATH,
                "size": authority.PRE_DB_STAMP[0],
                "sha256": "a" * 64,
            },
            {
                "relative_path": authority.PRE_STABLE_DB_PATH,
                "size": authority.PRE_DB_STAMP[0],
                "sha256": authority.PRE_DB_STAMP[1],
            },
            {
                "relative_path": "BEA.gpr",
                "size": 50_301_829,
                "sha256": "d" * 64,
            },
        ]
        files.extend(
            {
                "relative_path": f"BEA.rep/synthetic-{index:02d}",
                "size": 0,
                "sha256": hashlib.sha256(b"").hexdigest(),
            }
            for index in range(16)
        )
        files.sort(key=lambda row: row["relative_path"])
        before = {
            "projectName": "BEA",
            "fileCount": 19,
            "totalBytes": 187_009_925,
            "structurallyComplete": True,
            "files": files,
        }
        pre_digest = authority.prep.project_digest(before)
        after = json.loads(json.dumps(before))
        after["files"] = [
            row
            for row in after["files"]
            if row["relative_path"] != authority.PRE_OLD_DB_PATH
        ]
        after["files"].append(
            {
                "relative_path": authority.POST_ROLLING_DB_PATH,
                "size": authority.PRE_DB_STAMP[0],
                "sha256": "b" * 64,
            }
        )
        after["files"].sort(key=lambda row: row["relative_path"])
        digest = authority.prep.project_digest(after)
        with (
            mock.patch.object(authority.prep, "PRE_PROJECT_SHA256", pre_digest),
            mock.patch.object(authority, "POST_PROJECT_SHA256", digest),
            mock.patch.object(authority, "POST_DB_SHA256", "b" * 64),
        ):
            result = authority.validate_post_transition(before, after, "synthetic")
        self.assertEqual(result["removed"], [authority.PRE_OLD_DB_PATH])
        self.assertEqual(result["added"], [authority.POST_ROLLING_DB_PATH])
        self.assertEqual(result["changed"], [])

        stable = next(
            row
            for row in after["files"]
            if row["relative_path"] == authority.PRE_STABLE_DB_PATH
        )
        stable["sha256"] = "c" * 64
        drift_digest = authority.prep.project_digest(after)
        with (
            mock.patch.object(authority.prep, "PRE_PROJECT_SHA256", pre_digest),
            mock.patch.object(authority, "POST_PROJECT_SHA256", drift_digest),
            mock.patch.object(authority, "POST_DB_SHA256", "b" * 64),
        ):
            with self.assertRaises(authority.AuthorityError):
                authority.validate_post_transition(before, after, "synthetic")

    def test_final_physical_identities_fail_closed_until_measured(self) -> None:
        if authority.POST_PROJECT_SHA256 == "0" * 64:
            with self.assertRaisesRegex(authority.AuthorityError, "not frozen"):
                authority.require_final_constants()
        else:
            self.assertRegex(authority.POST_PROJECT_SHA256, r"^[0-9a-f]{64}$")
            self.assertRegex(authority.POST_DB_SHA256, r"^[0-9a-f]{64}$")
            authority.require_final_constants()

    def test_portability_and_create_new_receipt_are_fail_closed(self) -> None:
        authority.ensure_portable({"path": "local-lab/evidence.json"})
        with self.assertRaisesRegex(authority.AuthorityError, "absolute path"):
            authority.ensure_portable({"path": r"C:\secret\receipt.json"})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "receipt.json"
            authority.atomic_new_json(target, {"status": "READY"})
            self.assertEqual(json.loads(target.read_text()), {"status": "READY"})
            with self.assertRaisesRegex(authority.AuthorityError, "overwrite"):
                authority.atomic_new_json(target, {"status": "DRIFT"})

    def test_exact_directory_census_rejects_nested_or_extra_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "expected.txt").write_text("ok", encoding="utf-8")
            authority.exact_directory_entries(
                root,
                expected_files=("expected.txt",),
                expected_directories=(),
                label="synthetic",
            )
            (root / "unexpected").mkdir()
            with self.assertRaisesRegex(authority.AuthorityError, "directory set"):
                authority.exact_directory_entries(
                    root,
                    expected_files=("expected.txt",),
                    expected_directories=(),
                    label="synthetic",
                )

    def test_inventory_diff_accepts_only_two_creations(self) -> None:
        value = {
            "counts": {"before": 8327, "after": 8329, "created": 2, "destroyed": 0},
            "created": [
                {"address": "0x00595fc9"},
                {"address": "0x00596028"},
            ],
            "destroyed": [],
            "dangerous": {
                "gradedBoundsMoved": [],
                "gradedBoundsMovedCount": 0,
                "gradedDemotedCount": 0,
                "gradedDestroyedCount": 0,
                "gradedFunctionsDestroyed": [],
                "gradedFunctionsRenamed": [],
                "gradedNameSourceDemoted": [],
                "gradedRenamedCount": 0,
            },
            "changesByField": {"name": [], "bodyBytes": [], "bodyDigest": []},
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "inventory-diff.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            result = authority.validate_inventory_diff(path)
            self.assertEqual(result["created"], sorted(authority.prep.TARGETS))
            value["created"][1]["address"] = "0x00596029"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(authority.AuthorityError):
                authority.validate_inventory_diff(path)

    def test_chronology_requires_strict_partial_order(self) -> None:
        start = datetime(2026, 8, 14, tzinfo=timezone.utc)
        offsets = {
            "live.pre.inspect": 0,
            "tracked.pre.inspect": 0,
            "pre.backup.created": 1,
            "pre.restore.verified": 2,
            "live.beforeApply.inspect": 4,
            "live.post.inspect": 7,
            "post.backup.created": 8,
            "post.restore.verified": 9,
            "tracked.stillPre.inspect": 10,
        }
        projects = {
            key: start + timedelta(seconds=offset) for key, offset in offsets.items()
        }
        runs = {
            "live.dry.complete": start + timedelta(seconds=3),
            "live.apply.complete": start + timedelta(seconds=5),
            "live.readback.complete": start + timedelta(seconds=6),
        }
        authority.validate_chronology(projects, runs)
        runs["live.apply.complete"] = runs["live.dry.complete"]
        with self.assertRaisesRegex(authority.AuthorityError, "chronology"):
            authority.validate_chronology(projects, runs)


class RetainedEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        if os.environ.get("BEA_RUN_D3DX_GAP_TWO_LIVE_EVIDENCE") != "1":
            self.skipTest("set BEA_RUN_D3DX_GAP_TWO_LIVE_EVIDENCE=1")
        if not (EVIDENCE / authority.PREPARATION_RECEIPT_REL).is_file():
            self.skipTest("retained D3DX preparation evidence is absent")

    def test_prepared_exports_satisfy_future_delta_validators(self) -> None:
        package = EVIDENCE / authority.PREPARATION_REL
        functions = authority.validate_function_delta(
            package / "inputs/pre/functions.tsv",
            package / "runs/replica-a-readback/functions.tsv",
        )
        program = authority.validate_program_delta(
            package / "inputs/pre/program.tsv",
            package / "runs/replica-a-readback/program.tsv",
        )
        self.assertEqual(functions["unchangedPreRowsExact"], 8327)
        self.assertEqual(functions["created"], sorted(authority.prep.TARGETS))
        self.assertEqual(program["changedMetrics"], ["functions"])

    def test_prospective_projection_and_accounting_are_exact(self) -> None:
        current = config()
        projection = authority.prospective_projection(current)
        accounting = authority.prospective_accounting(current)
        self.assertEqual(
            (projection["bytes"], projection["sha256"]),
            authority.prep.PROJECTION_STAMP,
        )
        self.assertEqual(
            (accounting["post"]["bytes"], accounting["post"]["sha256"]),
            authority.prep.BODY_RANGES_STAMP,
        )
        self.assertEqual(
            accounting["directCalls"]["sha256"],
            authority.prep.DIRECT_CALLS_STAMP[1],
        )

    def test_current_phase_is_read_only_and_reproducible(self) -> None:
        current = config(repo=EVIDENCE)
        output = EVIDENCE / authority.AUTHORITY_RECEIPT_REL
        if output.is_file():
            authority.verify(config(output, repo=EVIDENCE))
            return
        if current.live_lane.exists():
            live_pre, _ = authority.inspect_receipt(
                current.live_lane / "live-pre-inspect.json",
                current.live_project,
                authority.prep.PRE_PROJECT_SHA256,
                "live PRE inspect",
            )
            tracked_pre, _ = authority.inspect_receipt(
                current.live_lane / "tracked-pre-inspect.json",
                current.tracked_project,
                authority.prep.PRE_PROJECT_SHA256,
                "tracked PRE inspect",
            )
            authority.require_same_project(live_pre, tracked_pre, "live/tracked PRE")
            backup, _ = authority.validate_backup_manifest(
                current.pre_backup / "backup_manifest.json",
                current.live_project,
                current.pre_backup,
                live_pre,
                authority.prep.PRE_PROJECT_SHA256,
                "PRE backup",
            )
            authority.validate_restore(
                current.live_lane / "pre-backup-restore.ready.json",
                current.pre_backup,
                current.live_lane / "pre-backup-restore-probe",
                current.repo / "tools",
                backup,
                authority.prep.PRE_PROJECT_SHA256,
                authority.AGGREGATE_PRE_FUNCTIONS,
                "PRE restore",
            )
            if (
                authority.POST_PROJECT_SHA256 != "0" * 64
                and (current.live_lane / "live-post-inspect.json").is_file()
                and not (current.live_lane / "tracked-post-inspect.json").exists()
            ):
                authority.build_live_phase(current)
            return
        live_before = authority.project_value(current.live_project)
        tracked_before = authority.project_value(current.tracked_project)
        result = authority.preflight(current)
        live_after = authority.project_value(current.live_project)
        tracked_after = authority.project_value(current.tracked_project)
        self.assertEqual(
            authority.project_map(live_before), authority.project_map(live_after)
        )
        self.assertEqual(
            authority.project_map(tracked_before), authority.project_map(tracked_after)
        )
        self.assertEqual(result["verdict"], "PREPARATION_READY_MUTATION_NOT_AUTHORIZED")
        self.assertFalse(result["futureMutationAuthorized"])


if __name__ == "__main__":
    unittest.main()
