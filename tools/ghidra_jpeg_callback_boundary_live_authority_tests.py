#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the inert JPEG24 live-promotion authority."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_jpeg_callback_boundary_live_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRATCH = Path.home() / "source/Onslaught-Career-Editor-lane-jpeg24-scratch-admission"
if not (DEFAULT_SCRATCH / authority.SCRATCH_LANE_REL).is_dir():
    DEFAULT_SCRATCH = ROOT
SCRATCH_REPO = Path(os.environ.get("BEA_JPEG24_SCRATCH_REPO", DEFAULT_SCRATCH))


def config(live_lane: Path, output: Path | None = None) -> authority.Config:
    return authority.Config(
        ROOT.resolve(),
        SCRATCH_REPO.resolve(),
        (ROOT / "fixture-live-project").resolve(strict=False),
        live_lane.resolve(strict=False),
        (ROOT / "fixture-pre-backup").resolve(strict=False),
        (ROOT / "fixture-post-backup").resolve(strict=False),
        output.resolve(strict=False) if output is not None else None,
    )


class PureContractTests(unittest.TestCase):
    def test_exact_pre_post_contract(self) -> None:
        self.assertEqual(authority.POLICY, "PREPARATION_ONLY")
        self.assertEqual(
            authority.BASE_COMMIT,
            "3a2397aec192330a9d26f4615b3e1aee599e7850",
        )
        self.assertEqual((authority.PRE_FUNCTIONS, authority.POST_FUNCTIONS), (8280, 8304))
        self.assertEqual((authority.PRE_RANGES, authority.POST_RANGES), (8400, 8438))
        self.assertEqual((authority.PRE_OWNED, authority.POST_OWNED), (1794212, 1809029))
        self.assertEqual(
            (authority.PRE_INSTRUCTIONS, authority.POST_INSTRUCTIONS),
            (550991, 551032),
        )
        self.assertEqual(
            (authority.PRE_REFERENCES, authority.POST_REFERENCES),
            (234495, 234484),
        )
        self.assertEqual(authority.POST_OWNED - authority.PRE_OWNED, 14817)

    def test_repo_input_stamps_are_current(self) -> None:
        for relative, expected in authority.EXPECTED_REPO_INPUTS.items():
            path = ROOT / relative
            self.assertEqual(
                (path.stat().st_size, authority.sha256_file(path)),
                expected,
                relative,
            )

    def test_target_manifest_is_exact_24_entry_38_range_cohort(self) -> None:
        rows = authority.load_targets(ROOT / authority.MANIFEST_REL)
        self.assertEqual(len(rows), 24)
        self.assertEqual(sum(int(row["body_range_count"]) for row in rows), 38)
        self.assertEqual(sum(int(row["body_bytes"]) for row in rows), 14817)
        self.assertEqual(sum(int(row["instruction_count"]) for row in rows), 4497)
        correction = next(row for row in rows if row["retail_va"] == "0x005B6800")
        self.assertEqual(correction["body_ranges"], "0x005B6800-0x005B6A86")

    def test_post_body_rows_close_exact_accounting(self) -> None:
        self.assertEqual(len(authority.POST_BODY_ROWS), 24)
        self.assertEqual(sum(len(rows) for rows in authority.POST_BODY_ROWS.values()), 38)
        self.assertEqual(
            sum(int(row[3]) for rows in authority.POST_BODY_ROWS.values() for row in rows),
            14817,
        )
        self.assertEqual(authority.TEXT_BYTES - authority.POST_OWNED, 120088)
        for rows in authority.POST_BODY_ROWS.values():
            for start, maximum, end, size, digest in rows:
                self.assertEqual(int(end, 16) - int(start, 16), int(size))
                self.assertEqual(int(maximum, 16) + 1, int(end, 16))
                self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_project_digest_and_rotation_are_fail_closed(self) -> None:
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
            row for row in post["files"] if row["relative_path"] != authority.PRE_OLD_DB_PATH
        ]
        post["files"].append({
            "relative_path": authority.POST_ROLLING_DB_PATH,
            "size": 2,
            "sha256": "b",
        })
        pre["files"].sort(key=lambda row: row["relative_path"])
        post["files"].sort(key=lambda row: row["relative_path"])
        with mock.patch.dict(authority.PRE_PROJECT, {"fileCount": 3}):
            result = authority.validate_post_transition(pre, post, "synthetic")
        self.assertEqual(result["removed"], [authority.PRE_OLD_DB_PATH])
        self.assertEqual(result["added"], [authority.POST_ROLLING_DB_PATH])
        post["files"][0]["sha256"] = "drift"
        with mock.patch.dict(authority.PRE_PROJECT, {"fileCount": 3}):
            with self.assertRaises(authority.AuthorityError):
                authority.validate_post_transition(pre, post, "synthetic")

    def test_all_pre_function_fields_must_remain_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            live = root / "live"
            scratch = root / authority.SCRATCH_LANE_REL
            (live / "runs/live-pre-readback").mkdir(parents=True)
            (live / "runs/live-readback").mkdir(parents=True)
            (scratch / "runs/base-inventory").mkdir(parents=True)
            (scratch / "runs/formal-replica-a-readback").mkdir(parents=True)
            header = b"address\tname\tnameSource\tbodyBytes\tbodyRanges\tinstrCount\n"
            before = header + b"0x00000010\tStable\tUSER_DEFINED\t1\t1\t1\n"
            after = (
                header
                + b"0x00000010\tChanged\tUSER_DEFINED\t1\t1\t1\n"
                + b"0x00000020\tFUN_00000020\tDEFAULT\t2\t1\t1\n"
            )
            for path in (
                live / "runs/live-pre-readback/functions.tsv",
                scratch / "runs/base-inventory/functions.tsv",
            ):
                path.write_bytes(before)
            for path in (
                live / "runs/live-readback/functions.tsv",
                scratch / "runs/formal-replica-a-readback/functions.tsv",
            ):
                path.write_bytes(after)
            cfg = authority.Config(
                root, root, root / "project", live, root / "pre", root / "post", None
            )
            target = {
                "retail_va": "0x00000020", "body_bytes": "2",
                "body_range_count": "1", "instruction_count": "1",
            }
            with (
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 2),
                mock.patch.object(authority, "TARGETS", 1),
                mock.patch.object(authority, "PRE_FUNCTIONS_STAMP",
                                  (len(before), hashlib.sha256(before).hexdigest())),
                mock.patch.object(authority, "POST_FUNCTIONS_STAMP",
                                  (len(after), hashlib.sha256(after).hexdigest())),
                mock.patch.object(authority, "load_targets", return_value=[target]),
            ):
                with self.assertRaisesRegex(authority.AuthorityError, "PRE row changed"):
                    authority.validate_function_delta(cfg)

    def test_portability_and_create_new_receipt_fail_closed(self) -> None:
        authority.ensure_portable({"path": "local-lab/evidence.json"})
        for path in (r"C:\secret\receipt.json", "/tmp/receipt.json"):
            with self.assertRaisesRegex(authority.AuthorityError, "absolute"):
                authority.ensure_portable({"path": path})
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "receipt.json"
            authority.atomic_new_json(target, {"status": "READY"})
            self.assertEqual(json.loads(target.read_text()), {"status": "READY"})
            with self.assertRaisesRegex(authority.AuthorityError, "overwrite"):
                authority.atomic_new_json(target, {"status": "DRIFT"})

    def test_restore_execution_paths_and_command_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cfg = authority.Config(
                root,
                root,
                root / "live-project",
                root / "live-lane",
                root / "pre-backup",
                root / "post-backup",
                None,
            )
            retained = cfg.live_lane / "probe" / "BEA-open-probe-fixture"
            expected_command = authority.project_backup.build_open_command(
                authority.ANALYZE_HEADLESS,
                retained,
                "BEA",
                authority.PROGRAM_NAME,
                cfg.repo / "tools",
                authority.PROGRAM_MD5,
                authority.PROGRAM_SHA256,
            )
            value = {
                "source": {"root": str(cfg.pre_backup)},
                "probeCopy": str(retained),
                "readonlyOpen": {"commandArgv": expected_command},
            }
            authority.validate_restore_execution_paths(
                cfg, value, retained, cfg.pre_backup, "fixture restore"
            )

            wrong = json.loads(json.dumps(value))
            wrong["source"]["root"] = str(root / "other-source")
            with self.assertRaisesRegex(authority.AuthorityError, "source root"):
                authority.validate_restore_execution_paths(
                    cfg, wrong, retained, cfg.pre_backup, "fixture restore"
                )

            wrong = json.loads(json.dumps(value))
            wrong["probeCopy"] = str(root / "other-probe")
            with self.assertRaisesRegex(authority.AuthorityError, "probe-copy path"):
                authority.validate_restore_execution_paths(
                    cfg, wrong, retained, cfg.pre_backup, "fixture restore"
                )

            mutations = {
                "headless": (0, str(root / "other-analyzeHeadless.bat")),
                "project": (1, str(root / "other-project")),
                "program": (4, "Other.exe"),
                "script": (
                    expected_command.index("-scriptPath") + 1,
                    str(root / "other-tools"),
                ),
                "md5": (-2, "0" * 32),
                "sha256": (-1, "0" * 64),
            }
            for label, (index, replacement) in mutations.items():
                with self.subTest(label=label):
                    wrong = json.loads(json.dumps(value))
                    wrong["readonlyOpen"]["commandArgv"][index] = replacement
                    with self.assertRaisesRegex(
                        authority.AuthorityError, "read-only command"
                    ):
                        authority.validate_restore_execution_paths(
                            cfg, wrong, retained, cfg.pre_backup, "fixture restore"
                        )

    def test_backup_manifest_paths_and_no_open_contract_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "destination"
            expected = {
                "projectName": "BEA",
                "fileCount": 0,
                "totalBytes": 0,
                "structurallyComplete": True,
                "files": [],
            }
            comparison = {
                "extra": [],
                "extraCount": 0,
                "hashDiffCount": 0,
                "hashDifferences": [],
                "matches": True,
                "missing": [],
                "missingCount": 0,
                "sizeDiffCount": 0,
                "sizeDifferences": [],
            }
            payload = {
                "schemaVersion": authority.project_backup.SCHEMA_VERSION,
                "createdAtUtc": "2026-08-14T00:00:00Z",
                "sourceStable": True,
                "copyComparison": comparison,
                "source": {**expected, "root": str(source)},
                "destination": {**expected, "root": str(destination)},
                "readonlyOpen": None,
            }
            path = root / "backup_manifest.json"
            path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            authority.validate_backup_manifest(
                path, expected, source, destination, "fixture backup"
            )

            wrong = json.loads(json.dumps(payload))
            wrong["destination"]["root"] = str(root / "other-destination")
            path.write_text(json.dumps(wrong) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "destination root"):
                authority.validate_backup_manifest(
                    path, expected, source, destination, "fixture backup"
                )

            wrong = json.loads(json.dumps(payload))
            wrong["readonlyOpen"] = {"opened": True}
            path.write_text(json.dumps(wrong) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "opened Ghidra"):
                authority.validate_backup_manifest(
                    path, expected, source, destination, "fixture backup"
                )

    def test_live_receipt_rebase_retains_fixed_point_contract(self) -> None:
        if not (SCRATCH_REPO / authority.SCRATCH_RECEIPT_REL).is_file():
            self.skipTest("retained JPEG24 scratch package is unavailable")
        source_root = SCRATCH_REPO / authority.SCRATCH_LANE_REL / "runs"
        source_by_mode = {
            "dry": "formal-replica-a-dry",
            "apply": "formal-replica-a-apply",
            "readback": "formal-replica-a-readback",
        }
        with tempfile.TemporaryDirectory() as temporary:
            lane = Path(temporary) / "lane"
            cfg = config(lane)
            for mode, source_name in source_by_mode.items():
                run_name = "fixture-" + mode
                run = lane / "runs" / run_name
                run.mkdir(parents=True)
                source = source_root / source_name
                shutil.copyfile(source / "boundaries.tsv", run / "boundaries.tsv")
                receipt = json.loads(
                    (source / "boundaries.ready.json").read_text(encoding="utf-8")
                )
                receipt["tool"]["path"] = "tools/GhidraApplyJpegCallbackBoundaries.java"
                receipt["output"]["path"] = (
                    f"{authority.LIVE_LANE_REL}/runs/{run_name}/boundaries.tsv"
                )
                (run / "boundaries.ready.json").write_text(
                    json.dumps(receipt) + "\n", encoding="utf-8"
                )
                authority.validate_low_level_receipt(cfg, run_name, mode)
                receipt["fixedPointInstructionOwner"] = "0x005b6900"
                (run / "boundaries.ready.json").write_text(
                    json.dumps(receipt) + "\n", encoding="utf-8"
                )
                with self.assertRaisesRegex(authority.AuthorityError, "fixed-point"):
                    authority.validate_low_level_receipt(cfg, run_name, mode)


RETAINED_AVAILABLE = (
    (SCRATCH_REPO / authority.SCRATCH_RECEIPT_REL).is_file()
    and (SCRATCH_REPO / authority.PRE_ACCOUNTING_REL).is_file()
)


@unittest.skipUnless(RETAINED_AVAILABLE, "retained JPEG24 scratch package is unavailable")
class RetainedEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = config(ROOT / authority.LIVE_LANE_REL)

    def test_scratch_receipt_and_whole_tree_reproduce(self) -> None:
        result = authority.validate_scratch(self.config)
        self.assertEqual(result["receipt"]["sha256"], authority.SCRATCH_RECEIPT_STAMP[1])
        self.assertEqual(result["fullTree"], authority.SCRATCH_TREE)

    def test_prospective_projection_is_exact_without_materializing(self) -> None:
        result = authority.prospective_projection(self.config)
        self.assertEqual(
            (result["bytes"], result["sha256"]), authority.POST_PROJECTION_STAMP
        )
        self.assertIs(result["materialized"], False)

    def test_prospective_body_accounting_is_exact_without_materializing(self) -> None:
        result = authority.prospective_body_accounting(self.config)
        self.assertEqual(
            (result["bytes"], result["sha256"]), authority.POST_BODY_RANGES_STAMP
        )
        self.assertEqual((result["functions"], result["ranges"]), (8304, 8438))
        self.assertEqual(result["ownedBytes"], 1809029)
        self.assertIs(result["materialized"], False)

    def test_scratch_listing_proves_005b6900_final_byte_ownership(self) -> None:
        base = SCRATCH_REPO / authority.SCRATCH_LANE_REL / "runs"
        authority.scratch.verify_listing(
            base / "base-diagnostic/listing-state.tsv", False
        )
        authority.scratch.verify_listing(
            base / "formal-replica-a-readback/listing-state.tsv", True
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
