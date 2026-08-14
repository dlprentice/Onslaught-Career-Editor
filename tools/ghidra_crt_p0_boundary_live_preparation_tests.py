#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the read-only CRT23/db.18614 preparation authority."""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_crt_p0_boundary_live_preparation as authority


ROOT = Path(__file__).resolve().parents[1]


def find_scratch_repo() -> Path:
    configured = os.environ.get("BEA_CRT23_SCRATCH_REPO")
    candidates = (
        Path(configured) if configured else None,
        ROOT,
        Path.home() / "source/Onslaught-Career-Editor",
    )
    for candidate in candidates:
        if candidate is not None and (candidate / authority.SCRATCH_READY_REL).is_file():
            return candidate.resolve()
    return ROOT.resolve()


SCRATCH_REPO = find_scratch_repo()
LIVE_PROJECT = Path(
    os.environ.get("BEA_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects")
).resolve(strict=False)


def current_config() -> authority.Config:
    return authority.Config(
        repo=ROOT.resolve(),
        scratch_repo=SCRATCH_REPO,
        live_project=LIVE_PROJECT,
        live_lane=(ROOT / authority.LIVE_LANE_REL).resolve(strict=False),
        pre_backup=Path(
            r"D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18614-pre-live-v1"
        ).resolve(strict=False),
        post_backup=Path(
            r"D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18614-post-live-v1"
        ).resolve(strict=False),
    )


class PureContractTests(unittest.TestCase):
    def test_exact_pre_post_contract(self) -> None:
        self.assertEqual(authority.POLICY, "PREPARATION_ONLY")
        self.assertEqual(
            authority.BASE_COMMIT,
            "4d7ba6f938ea54ed1312e0f61ba208b0d285b84e",
        )
        self.assertEqual((authority.PRE_FUNCTIONS, authority.POST_FUNCTIONS), (8280, 8303))
        self.assertEqual((authority.PRE_RANGES, authority.POST_RANGES), (8396, 8420))
        self.assertEqual((authority.PRE_OWNED, authority.POST_OWNED), (1795470, 1796601))
        self.assertEqual(
            (authority.PRE_INSTRUCTIONS, authority.POST_INSTRUCTIONS),
            (551014, 551092),
        )
        self.assertEqual(
            (authority.PRE_REFERENCES, authority.POST_REFERENCES),
            (234478, 234489),
        )
        self.assertEqual(authority.POST_OWNED - authority.PRE_OWNED, 1131)
        self.assertEqual(authority.TEXT_BYTES - authority.POST_OWNED, 132516)

    def test_v3_mutator_is_only_the_current_pre_counter_rebase(self) -> None:
        v2 = (ROOT / "tools/GhidraApplyCrtP0BoundariesV2.java").read_text(
            encoding="utf-8"
        )
        actual = (ROOT / authority.MUTATOR_REL).read_text(encoding="utf-8")
        replacements = (
            ("8,280-function/db.18613", "8,280-function/db.18614"),
            ("GhidraApplyCrtP0BoundariesV2", "GhidraApplyCrtP0BoundariesV3"),
            ("bea.ghidra.crt-p0-boundaries.v2", "bea.ghidra.crt-p0-boundaries.v3"),
            ("PRE_INSTRUCTIONS = 550991", "PRE_INSTRUCTIONS = 551014"),
            ("POST_INSTRUCTIONS = 551069", "POST_INSTRUCTIONS = 551092"),
            ("PRE_REFERENCES = 234495", "PRE_REFERENCES = 234478"),
            ("POST_REFERENCES = 234506", "POST_REFERENCES = 234489"),
            ("PRE_RANGES = 8400", "PRE_RANGES = 8396"),
            ("POST_RANGES = 8424", "POST_RANGES = 8420"),
        )
        expected = v2
        for old, new in replacements:
            self.assertIn(old, expected)
            expected = expected.replace(old, new)
        self.assertEqual(actual, expected)

    def test_repo_inputs_and_manifest_are_exact(self) -> None:
        for relative, expected in authority.EXPECTED_REPO_INPUTS.items():
            path = ROOT / relative
            self.assertEqual((path.stat().st_size, authority.sha256_file(path)), expected)
        rows = authority.read_tsv(ROOT / authority.MANIFEST_REL)
        self.assertEqual(len(rows), 23)
        self.assertEqual(
            sum(len(row["expectedRanges"].split(";")) for row in rows), 24
        )
        self.assertEqual(sum(int(row["expectedBodyBytes"]) for row in rows), 1131)
        self.assertEqual(sum(int(row["expectedInstructionCount"]) for row in rows), 312)
        entries = {row["entry"].lower() for row in rows}
        self.assertTrue(set(authority.FORBIDDEN).isdisjoint(entries))
        self.assertNotIn(authority.EXCLUDED_CANARY, entries)
        thunk = next(row for row in rows if row["entry"].lower() == authority.THUNK_ENTRY)
        self.assertEqual(thunk["expectedIsThunk"], "true")
        self.assertEqual(thunk["expectedThunkTarget"].lower(), authority.THUNK_TARGET)

    def test_project_inventory_and_rotation_are_fail_closed(self) -> None:
        empty_sha = hashlib.sha256(b"").hexdigest()
        pre = {
            "projectName": "BEA",
            "fileCount": 3,
            "totalBytes": authority.DB_18614[0] + 1,
            "structurallyComplete": True,
            "files": [
                {"relative_path": authority.PRE_OLD_DB_PATH,
                 "size": 1, "sha256": "a" * 64},
                {"relative_path": authority.PRE_STABLE_DB_PATH,
                 "size": authority.DB_18614[0], "sha256": authority.DB_18614[1]},
                {"relative_path": "BEA.gpr", "size": 0, "sha256": empty_sha},
            ],
        }
        pre["files"].sort(key=lambda row: row["relative_path"])
        post = {
            **pre,
            "totalBytes": authority.DB_18614[0] + 2,
            "files": [
                row for row in pre["files"]
                if row["relative_path"] != authority.PRE_OLD_DB_PATH
            ] + [{
                "relative_path": authority.POST_ROLLING_DB_PATH,
                "size": 2,
                "sha256": "b" * 64,
            }],
        }
        post["files"].sort(key=lambda row: row["relative_path"])
        with mock.patch.dict(authority.PRE_PROJECT, {"fileCount": 3}):
            result = authority.validate_post_transition(pre, post, "synthetic")
            self.assertEqual(result["removed"], [authority.PRE_OLD_DB_PATH])
            self.assertEqual(result["added"], [authority.POST_ROLLING_DB_PATH])

            drift = {**post, "files": [dict(row) for row in post["files"]]}
            stable = next(
                row for row in drift["files"]
                if row["relative_path"] == authority.PRE_STABLE_DB_PATH
            )
            stable["sha256"] = "c" * 64
            with self.assertRaises(authority.PreparationError):
                authority.validate_post_transition(pre, drift, "synthetic")

            wrong_total = {**post, "totalBytes": post["totalBytes"] + 1}
            with self.assertRaisesRegex(authority.PreparationError, "byte total"):
                authority.validate_post_transition(pre, wrong_total, "synthetic")

        duplicate = {**pre, "files": pre["files"] + [dict(pre["files"][0])]}
        with self.assertRaisesRegex(authority.PreparationError, "duplicate"):
            authority.project_file_map(duplicate)

    def test_tree_identity_rejects_reparse_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "evidence.bin").write_bytes(b"evidence")
            with mock.patch.object(authority.project_backup, "is_reparse", return_value=True):
                with self.assertRaisesRegex(authority.PreparationError, "reparse"):
                    authority.tree_identity(root)

    def test_all_pre_function_fields_must_remain_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.tsv"
            after = root / "after.tsv"
            manifest = root / "manifest.tsv"
            before.write_text("address\tname\n0x00000010\tStable\n", encoding="utf-8")
            after.write_text(
                "address\tname\n0x00000010\tChanged\n0x00000020\tFUN_00000020\n",
                encoding="utf-8",
            )
            manifest.write_text("entry\n0x00000020\n", encoding="utf-8")
            with (
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 2),
            ):
                with self.assertRaisesRegex(authority.PreparationError, "PRE function row"):
                    authority.validate_function_delta(before, after, manifest)

    def test_future_ceremony_path_forces_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            live_lane = root / "future-live-lane"
            live_lane.mkdir()
            config = authority.Config(
                repo=root,
                scratch_repo=root,
                live_project=root / "live",
                live_lane=live_lane,
                pre_backup=root / "pre",
                post_backup=root / "post",
            )
            project = {"projectName": "BEA", "files": []}
            with (
                mock.patch.object(authority, "validate_repo_inputs", return_value={}),
                mock.patch.object(authority, "validate_scratch", return_value={}),
                mock.patch.object(authority, "validate_preparation", return_value={}),
                mock.patch.object(authority, "project_value", return_value=project),
                mock.patch.object(authority, "require_pre_project"),
            ):
                with self.assertRaisesRegex(authority.PreparationError, "already exists"):
                    authority.preflight(config)


RETAINED_AVAILABLE = (
    (ROOT / authority.PREP_LANE_REL).is_dir()
    and (SCRATCH_REPO / authority.SCRATCH_READY_REL).is_file()
    and LIVE_PROJECT.is_dir()
)


@unittest.skipUnless(RETAINED_AVAILABLE, "retained CRT23 current-state evidence unavailable")
class RetainedEvidenceTests(unittest.TestCase):
    def test_full_read_only_preflight_reproduces(self) -> None:
        result = authority.preflight(current_config())
        self.assertEqual(result["policy"], "PREPARATION_ONLY")
        self.assertIs(result["liveEqualsTracked"], True)
        self.assertIs(result["mutationAuthorized"], False)
        self.assertEqual(result["blocker"], "future_ceremony_artifacts_absent")
        self.assertEqual(result["scratch"]["receipt"]["sha256"], authority.SCRATCH_READY_STAMP[1])
        self.assertEqual(result["preparation"]["tree"], authority.PREP_TREE)
        self.assertEqual(
            (result["prospectivePost"]["functions"],
             result["prospectivePost"]["ranges"],
             result["prospectivePost"]["ownedBytes"]),
            (8303, 8420, 1796601),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
