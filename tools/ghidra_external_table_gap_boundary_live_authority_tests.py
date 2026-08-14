#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the prospective 79-function live authority."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import tools.ghidra_external_table_gap_boundary_live_authority as authority
except ModuleNotFoundError:  # direct execution from tools/
    import ghidra_external_table_gap_boundary_live_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARED = Path.home() / "source/Onslaught-Career-Editor"
EVIDENCE_REPO = Path(os.environ.get(
    "BEA_EXTERNAL_TABLE_GAP_EVIDENCE_REPO",
    DEFAULT_SHARED if DEFAULT_SHARED.is_dir() else ROOT,
))
LIVE_PROJECT = Path(os.environ.get(
    "BEA_LIVE_GHIDRA_PROJECT",
    Path.home() / "Ghidra/Projects",
))
LIVE_LANE = EVIDENCE_REPO / authority.LIVE_LANE_REL
PRE_BACKUP = Path(os.environ.get(
    "BEA_EXTERNAL_TABLE_GAP_PRE_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-external-table-gap-boundaries-pre-live",
))
POST_BACKUP = Path(os.environ.get(
    "BEA_EXTERNAL_TABLE_GAP_POST_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-external-table-gap-boundaries-post-live",
))


def retained_config(output: Path | None = None) -> authority.Config:
    return authority.Config(
        EVIDENCE_REPO,
        EVIDENCE_REPO,
        LIVE_PROJECT,
        LIVE_LANE,
        PRE_BACKUP,
        POST_BACKUP,
        output,
    )


class PureContractTests(unittest.TestCase):
    def test_project_digest_is_relative_path_ordered(self) -> None:
        value = {
            "files": [
                {"relative_path": "a", "size": 1, "sha256": "1" * 64},
                {"relative_path": "b", "size": 2, "sha256": "2" * 64},
            ]
        }
        raw = (
            f"{'1' * 64}\t1\ta\n"
            f"{'2' * 64}\t2\tb\n"
        ).encode("utf-8")
        self.assertEqual(authority.project_digest(value), hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(authority.AuthorityError, "relative-path ordered"):
            authority.project_digest({"files": list(reversed(value["files"]))})

    def test_post_transition_allows_only_rolling_database_rotation(self) -> None:
        pre = {
            "projectName": "BEA",
            "fileCount": 19,
            "totalBytes": 30,
            "structurallyComplete": True,
            "files": [
                {
                    "relative_path": authority.PRE_OLD_DB_PATH,
                    "size": authority.DB_18611[0],
                    "sha256": authority.DB_18611[1],
                },
                {
                    "relative_path": authority.PRE_STABLE_DB_PATH,
                    "size": authority.DB_18612[0],
                    "sha256": authority.DB_18612[1],
                },
            ],
        }
        post = {
            **pre,
            "totalBytes": 40,
            "files": [
                pre["files"][1],
                {
                    "relative_path": authority.POST_ROLLING_DB_PATH,
                    "size": 100,
                    "sha256": "3" * 64,
                },
            ],
        }
        result = authority.validate_post_transition(pre, post, "fixture")
        self.assertEqual([authority.PRE_OLD_DB_PATH], result["removed"])
        self.assertEqual([authority.POST_ROLLING_DB_PATH], result["added"])
        post["files"][0] = {**post["files"][0], "sha256": "4" * 64}
        with self.assertRaisesRegex(authority.AuthorityError, "changed common files"):
            authority.validate_post_transition(pre, post, "fixture")

    def test_raw_function_comparison_checks_every_pre_field(self) -> None:
        fields = "address\tname\tnameSource\n"
        stable = "0x00000010\tStable\tUSER_DEFINED\n"
        changed = "0x00000010\tChanged\tUSER_DEFINED\n"
        added = "0x00000020\tFUN_00000020\tDEFAULT\n"
        target = {"retail_va": "0x00000020"}
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pre = root / "pre.tsv"
            post = root / "post.tsv"
            scratch_pre = root / "scratch-pre.tsv"
            scratch_post = root / "scratch-post.tsv"
            pre.write_bytes((fields + stable).encode("utf-8"))
            post.write_bytes((fields + changed + added).encode("utf-8"))
            scratch_pre.write_bytes(pre.read_bytes())
            scratch_post.write_bytes(post.read_bytes())
            with (
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 2),
                mock.patch.object(
                    authority,
                    "PRE_FUNCTIONS_STAMP",
                    (pre.stat().st_size, authority.sha256_file(pre)),
                ),
                mock.patch.object(
                    authority,
                    "POST_FUNCTIONS_STAMP",
                    (post.stat().st_size, authority.sha256_file(post)),
                ),
            ):
                with self.assertRaisesRegex(authority.AuthorityError, "PRE row changed"):
                    authority.validate_function_delta(
                        pre, post, scratch_pre, scratch_post, [target]
                    )

    def test_live_log_gate_requires_exactly_one_save(self) -> None:
        prefix = (
            "EXTERNAL_TABLE_GAP_BOUNDARIES_OK mode=apply\n"
            "Processing project file: /BEA.exe\n"
        )
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "ghidra.log"
            path.write_text(
                prefix + "Save succeeded for processed file: /BEA.exe\n",
                encoding="utf-8",
            )
            self.assertEqual(
                authority.validate_run_log(path, "apply")["successfulSaves"], 1
            )
            path.write_text(
                prefix + "Save succeeded for processed file: /BEA.exe\n" * 2,
                encoding="utf-8",
            )
            with self.assertRaisesRegex(authority.AuthorityError, "apply shape"):
                authority.validate_run_log(path, "apply")

    def test_read_only_log_rejects_a_save(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "ghidra.log"
            path.write_text(
                "EXTERNAL_TABLE_GAP_BOUNDARIES_OK mode=readback\n"
                "Processing read-only project file: /BEA.exe\n"
                "Save succeeded for processed file: /BEA.exe\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(authority.AuthorityError, "read-only shape"):
                authority.validate_run_log(path, "readback")

    def test_aggregate_payload_rejects_machine_paths(self) -> None:
        authority.ensure_portable({"path": "local-lab/evidence/receipt.json"})
        for value in (
            r"C:\Users\david\evidence.json",
            r"local-lab\evidence.json",
            "/tmp/evidence.json",
        ):
            with self.assertRaises(authority.AuthorityError):
                authority.ensure_portable({"path": value})

    def test_receipt_write_is_create_new(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "ready.json"
            authority.atomic_new_json(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"ok": True})
            with self.assertRaisesRegex(authority.AuthorityError, "refusing to overwrite"):
                authority.atomic_new_json(path, {"ok": False})

    def test_run_topology_rejects_extra_run_and_nested_entry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            lane = Path(raw) / "lane"
            runs = lane / "runs"
            runs.mkdir(parents=True)
            for name in authority.EXPECTED_RUN_NAMES:
                (runs / name).mkdir()
                (runs / name / "ghidra.log").write_bytes(b"fixture\n")
            authority.validate_run_directory_set(lane)
            extra = runs / "live-apply-2"
            extra.mkdir()
            (extra / "ghidra.log").write_bytes(b"extra\n")
            with self.assertRaisesRegex(authority.AuthorityError, "live runs root"):
                authority.validate_run_directory_set(lane)
            (extra / "ghidra.log").unlink()
            extra.rmdir()

            hidden = lane / "projects" / "replica-a"
            hidden.mkdir(parents=True)
            (hidden / "ghidra.log").write_bytes(b"unregistered\n")
            with self.assertRaisesRegex(authority.AuthorityError, "ghidra.log set differs"):
                authority.validate_run_directory_set(lane)
            (hidden / "ghidra.log").unlink()

            run = runs / "replica-a-apply"
            for name in ("boundaries.ready.json", "boundaries.tsv", "ghidra.log"):
                (run / name).write_bytes(b"fixture\n")
            authority.validate_run_file_set(run, "apply", live=False)
            (run / "nested").mkdir()
            with self.assertRaisesRegex(authority.AuthorityError, "run replica-a-apply"):
                authority.validate_run_file_set(run, "apply", live=False)

    def test_live_lane_topology_requires_tracked_still_pre_inspect(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            lane = root / "lane"
            files, directories = authority.expected_live_lane_topology(False)
            lane.mkdir()
            for name in files:
                (lane / name).write_bytes(b"fixture\n")
            for name in directories:
                (lane / name).mkdir()
            for name in ("replica-a", "replica-b"):
                (lane / "projects" / name).mkdir()
            for name in authority.EXPECTED_RUN_NAMES:
                (lane / "runs" / name).mkdir()
                (lane / "runs" / name / "ghidra.log").write_bytes(b"fixture\n")
            config = authority.Config(
                root,
                root,
                root / "live-project",
                lane,
                root / "pre-backup",
                root / "post-backup",
            )
            authority.validate_live_lane_topology(config, final=False)
            (lane / "tracked-still-pre-inspect.json").unlink()
            with self.assertRaisesRegex(authority.AuthorityError, "live evidence root"):
                authority.validate_live_lane_topology(config, final=False)

    def test_inspection_root_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            expected_root = root / "expected-project"
            expected = {
                "projectName": "BEA",
                "fileCount": 0,
                "totalBytes": 0,
                "structurallyComplete": True,
                "files": [],
            }
            path = root / "inspect.json"
            payload = {
                "schemaVersion": authority.project_backup.SCHEMA_VERSION,
                "createdAtUtc": "2026-08-14T00:00:00Z",
                "manifest": {**expected, "root": str(expected_root)},
            }
            path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            authority.validate_inspect(path, expected_root, expected, "fixture inspect")
            payload["manifest"]["root"] = str(root / "other-project")
            path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "root path differs"):
                authority.validate_inspect(path, expected_root, expected, "fixture inspect")

    def test_restore_execution_paths_and_command_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            config = authority.Config(
                root,
                root,
                root / "live-project",
                root / authority.LIVE_LANE_REL,
                root / "pre-backup",
                root / "post-backup",
            )
            retained = config.live_lane / "probe" / "BEA-open-probe-fixture"
            expected_argv = authority.project_backup.build_open_command(
                authority.ANALYZE_HEADLESS,
                retained,
                "BEA",
                authority.PROGRAM_NAME,
                config.repo / "tools",
                authority.PROGRAM_MD5,
                authority.PROGRAM_SHA256,
            )
            value = {
                "source": {"root": str(config.pre_backup)},
                "probeCopy": str(retained),
                "readonlyOpen": {"commandArgv": expected_argv},
            }
            authority.validate_restore_execution_paths(
                config, value, retained, config.pre_backup, "fixture restore"
            )

            wrong = json.loads(json.dumps(value))
            wrong["source"]["root"] = str(root / "other-source")
            with self.assertRaisesRegex(authority.AuthorityError, "source root path differs"):
                authority.validate_restore_execution_paths(
                    config, wrong, retained, config.pre_backup, "fixture restore"
                )

            wrong = json.loads(json.dumps(value))
            wrong["probeCopy"] = str(root / "other-parent" / retained.name)
            with self.assertRaisesRegex(authority.AuthorityError, "probe copy path differs"):
                authority.validate_restore_execution_paths(
                    config, wrong, retained, config.pre_backup, "fixture restore"
                )

            mutations = {
                "headless": (0, str(root / "other-analyzeHeadless.bat")),
                "project": (1, str(root / "other-project")),
                "program": (4, "Other.exe"),
                "script": (expected_argv.index("-scriptPath") + 1, str(root / "other-tools")),
                "md5": (-2, "0" * 32),
                "sha256": (-1, "0" * 64),
            }
            for label, (index, replacement) in mutations.items():
                with self.subTest(label=label):
                    wrong = json.loads(json.dumps(value))
                    wrong["readonlyOpen"]["commandArgv"][index] = replacement
                    with self.assertRaisesRegex(authority.AuthorityError, "open command differs"):
                        authority.validate_restore_execution_paths(
                            config, wrong, retained, config.pre_backup, "fixture restore"
                        )

    def test_aggregate_output_has_one_canonical_path(self) -> None:
        canonical = ROOT / authority.AUTHORITY_RECEIPT_REL
        config = authority.Config(
            ROOT,
            ROOT,
            ROOT / "fixture-live-project",
            ROOT / authority.LIVE_LANE_REL,
            ROOT / "fixture-pre-backup",
            ROOT / "fixture-post-backup",
            canonical,
        )
        authority.validate_output(config, sealing=True)
        with self.assertRaisesRegex(authority.AuthorityError, "canonical authority path"):
            authority.validate_output(
                authority.Config(
                    config.repo,
                    config.scratch_repo,
                    config.live_project,
                    config.live_lane,
                    config.pre_backup,
                    config.post_backup,
                    canonical.with_name("alternate.json"),
                ),
                sealing=True,
            )

    def test_parallel_replica_chronology_still_requires_phase_barriers(self) -> None:
        start = datetime(2026, 8, 14, tzinfo=timezone.utc)
        names = [
            "live.pre.inspect", "tracked.pre.inspect", "pre.backup.created",
            "pre.restore.verified", "replica-a.copy.created", "replica-b.copy.created",
            "replica-a.dry.receipt", "replica-b.dry.receipt",
            "replica-a.apply.receipt", "replica-b.apply.receipt",
            "replica-a.readback.receipt", "replica-b.readback.receipt",
            "replica-a.readback.complete", "replica-b.readback.complete",
            "live.dry.receipt", "live.dry.complete", "live.beforeApply.inspect",
            "live.apply.receipt", "live.readback.receipt", "live.readback.complete",
            "live.inventoryDiff.complete", "live.post.inspect", "post.backup.created",
            "post.restore.verified", "tracked.stillPre.inspect",
        ]
        events = {name: start + timedelta(seconds=index) for index, name in enumerate(names)}
        project_names = {
            "live.pre.inspect", "tracked.pre.inspect", "pre.backup.created",
            "pre.restore.verified", "replica-a.copy.created", "replica-b.copy.created",
            "live.beforeApply.inspect", "live.post.inspect", "post.backup.created",
            "post.restore.verified", "tracked.stillPre.inspect",
        }
        project = {name: value for name, value in events.items() if name in project_names}
        runs = {name: value for name, value in events.items() if name not in project_names}
        authority.validate_chronology(project, runs)
        still_pre = project["tracked.stillPre.inspect"]
        project["tracked.stillPre.inspect"] = project["post.restore.verified"]
        with self.assertRaisesRegex(authority.AuthorityError, "chronology"):
            authority.validate_chronology(project, runs)
        project["tracked.stillPre.inspect"] = still_pre
        runs["live.dry.receipt"] = runs["replica-a.readback.complete"]
        with self.assertRaisesRegex(authority.AuthorityError, "chronology"):
            authority.validate_chronology(project, runs)

    def test_pinned_post_projection_is_exact(self) -> None:
        self.assertEqual(
            authority.POST_PROJECTION_STAMP,
            (
                508242,
                "6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68",
            ),
        )


RETAINED_PREFLIGHT_AVAILABLE = all(path.exists() for path in (
    EVIDENCE_REPO / authority.MANIFEST_REL,
    EVIDENCE_REPO / authority.SCRATCH_RECEIPT_REL,
    LIVE_PROJECT / "BEA.gpr",
    EVIDENCE_REPO / "reverse-engineering/ghidra/BEA.gpr",
)) and not any(path.exists() for path in (LIVE_LANE, PRE_BACKUP, POST_BACKUP))


@unittest.skipUnless(
    RETAINED_PREFLIGHT_AVAILABLE,
    "current PRE state or retained scratch authority is unavailable",
)
class RetainedPreflightTests(unittest.TestCase):
    def test_preflight_reproduces_without_writing(self) -> None:
        before = [path.exists() for path in (LIVE_LANE, PRE_BACKUP, POST_BACKUP)]
        result = authority.preflight(retained_config())
        after = [path.exists() for path in (LIVE_LANE, PRE_BACKUP, POST_BACKUP)]
        self.assertEqual([False, False, False], before)
        self.assertEqual(before, after)
        self.assertEqual("PREFLIGHT_READY_MUTATION_NOT_AUTHORIZED", result["verdict"])
        self.assertIs(result["futureMutationAuthorized"], False)

    def test_scratch_pre_post_are_exact_semantic_fixtures(self) -> None:
        config = retained_config()
        targets = authority.load_targets(config.manifest)
        pre_functions = config.scratch_lane / "runs/base-inventory/functions.tsv"
        post_functions = config.scratch_lane / "runs/replica-a-readback/functions.tsv"
        pre_program = config.scratch_lane / "runs/base-inventory/program.tsv"
        post_program = config.scratch_lane / "runs/replica-a-readback/program.tsv"
        functions = authority.validate_function_delta(
            pre_functions,
            post_functions,
            pre_functions,
            post_functions,
            targets,
        )
        program = authority.validate_program_delta(
            pre_program,
            post_program,
            pre_program,
            post_program,
        )
        self.assertEqual(authority.PRE_FUNCTIONS, functions["preRowsByteIdentical"])
        self.assertTrue(functions["fullPostByteIdenticalToScratch"])
        self.assertTrue(program["memoryUnchanged"])

    def test_projection_preimage_reproduces_expected_future_bytes(self) -> None:
        inventory = (
            EVIDENCE_REPO / authority.SCRATCH_LANE_REL
            / "runs/replica-a-readback/functions.tsv"
        )
        raw = authority.name_projection.projection_bytes(
            inventory,
            expected_inventory_sha256=authority.POST_FUNCTIONS_STAMP[1],
            source_label=authority.PROJECTION_SOURCE,
            projection_date="2026-08-14",
            specimen_sha256=authority.PROGRAM_SHA256,
        )
        self.assertEqual(
            authority.POST_PROJECTION_STAMP,
            (len(raw), hashlib.sha256(raw).hexdigest()),
        )

    def test_live_receipt_contract_accepts_only_rebased_exact_scratch_outputs(self) -> None:
        targets = authority.load_targets(EVIDENCE_REPO / authority.MANIFEST_REL)
        with tempfile.TemporaryDirectory() as raw:
            lane = Path(raw) / "lane"
            config = authority.Config(
                EVIDENCE_REPO,
                EVIDENCE_REPO,
                LIVE_PROJECT,
                lane,
                PRE_BACKUP,
                POST_BACKUP,
            )
            for mode in ("dry", "apply", "readback"):
                run_name = f"fixture-{mode}"
                run = lane / "runs" / run_name
                run.mkdir(parents=True)
                source = (
                    EVIDENCE_REPO / authority.SCRATCH_LANE_REL
                    / f"runs/replica-a-{mode}"
                )
                boundaries = run / "boundaries.tsv"
                boundaries.write_bytes((source / "boundaries.tsv").read_bytes())
                receipt = json.loads(
                    (source / "boundaries.ready.json").read_text(encoding="utf-8")
                )
                receipt["tool"]["path"] = (
                    "tools/GhidraApplyExternalTableGapBoundaries.java"
                )
                receipt["output"]["path"] = (
                    f"{authority.LIVE_LANE_REL}/runs/{run_name}/boundaries.tsv"
                )
                (run / "boundaries.ready.json").write_text(
                    json.dumps(receipt) + "\n", encoding="utf-8"
                )
                authority.validate_run_receipt(config, run_name, mode, targets)
                receipt["namesAuthorized"] = True
                (run / "boundaries.ready.json").write_text(
                    json.dumps(receipt) + "\n", encoding="utf-8"
                )
                with self.assertRaisesRegex(authority.AuthorityError, "claim boundary"):
                    authority.validate_run_receipt(config, run_name, mode, targets)


if __name__ == "__main__":
    unittest.main(verbosity=2)
