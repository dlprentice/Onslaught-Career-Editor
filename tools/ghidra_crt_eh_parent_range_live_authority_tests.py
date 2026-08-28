#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the CRT EH parent-range live-promotion authority."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_crt_eh_parent_range_live_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = Path.home() / "source/Onslaught-Career-Editor"
EVIDENCE = Path(os.environ.get(
    "BEA_CRT_EH_PARENT_RANGE_EVIDENCE_REPO",
    DEFAULT_EVIDENCE if DEFAULT_EVIDENCE.is_dir() else ROOT,
))
LIVE_PROJECT = Path(os.environ.get(
    "BEA_LIVE_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects"
))
LIVE_LANE = EVIDENCE / authority.LIVE_LANE_REL
PRE_BACKUP = Path(os.environ.get(
    "BEA_CRT_EH_PARENT_RANGE_PRE_BACKUP",
    r"H:\BEA-Ghidra-Backups\2026-08-14-crt-eh-parent-range-pre-live",
))
POST_BACKUP = Path(os.environ.get(
    "BEA_CRT_EH_PARENT_RANGE_POST_BACKUP",
    r"H:\BEA-Ghidra-Backups\2026-08-14-crt-eh-parent-range-post-live",
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
        tool = ROOT / "tools/ghidra_crt_eh_parent_range_live_authority.py"
        self.assertEqual(tool.stat().st_size, 71504)
        self.assertEqual(
            authority.sha256_file(tool),
            "8a1a4bd536992aae598d252d8059209a1d8c3c19678b64484280086c5116ddfd",
        )

    def test_exact_pre_post_contract(self) -> None:
        self.assertEqual(authority.POLICY, "PREPARATION_ONLY")
        self.assertEqual(authority.BASE_COMMIT, "1ae3b33dbaf1b8a96f32f871ddd6bc42cec9b0be")
        self.assertEqual(
            (authority.PRE_FUNCTIONS, authority.POST_FUNCTIONS), (8327, 8327)
        )
        self.assertEqual((authority.PRE_RANGES, authority.POST_RANGES), (8458, 8457))
        self.assertEqual((authority.PRE_OWNED, authority.POST_OWNED), (1811418, 1811443))
        self.assertEqual(
            (authority.PRE_INSTRUCTIONS, authority.POST_INSTRUCTIONS),
            (551133, 551143),
        )
        self.assertEqual(
            (authority.PRE_REFERENCES, authority.POST_REFERENCES),
            (234478, 234478),
        )
        self.assertEqual(authority.POST_OWNED - authority.PRE_OWNED, 25)
        self.assertEqual(set(authority.POST_BODY_ROWS), {"0x005d0a9f"})

    def test_repo_input_stamps_are_current(self) -> None:
        for relative, expected in authority.EXPECTED_REPO_INPUTS.items():
            path = ROOT / relative
            self.assertEqual(
                (path.stat().st_size, authority.sha256_file(path)),
                expected,
                relative,
            )

    def test_target_manifest_is_exact_one(self) -> None:
        rows = authority.load_targets(ROOT / authority.MANIFEST_REL)
        self.assertEqual(len(rows), 1)
        self.assertEqual(sum(int(row["repair_bytes"]) for row in rows), 25)
        self.assertEqual(
            sum(int(row["repair_instruction_count"]) for row in rows), 10
        )
        self.assertEqual(
            rows[0]["repair_ranges"], "0x005d0ad6-0x005d0aef"
        )

    def test_post_body_rows_close_exact_accounting(self) -> None:
        target_bytes = sum(
            int(row[3])
            for rows in authority.POST_BODY_ROWS.values()
            for row in rows
        )
        self.assertEqual(target_bytes, 101)
        self.assertEqual(authority.TEXT_BYTES - authority.POST_OWNED, 117674)
        self.assertEqual(authority.POST_BODY_RANGES_STAMP[0], 1205601)
        self.assertEqual(authority.DIRECT_CALLS_STAMP[0], 1397680)
        self.assertEqual(
            (authority.DIRECT_EDGES, authority.DIRECT_CALL_SITES), (14598, 27244)
        )
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
                 "size": authority.DB_18616[0], "sha256": authority.DB_18616[1]},
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
        if os.environ.get("BEA_RUN_CRT_EH_PARENT_RANGE_LIVE_PREP_EVIDENCE") != "1":
            self.skipTest("set BEA_RUN_CRT_EH_PARENT_RANGE_LIVE_PREP_EVIDENCE=1")
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
        inventory = EVIDENCE / authority.SCRATCH_LANE_REL / (
            "runs/inventory-post-a/functions.tsv"
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

    def test_post_body_accounting_is_predetermined_by_exact_range_merge(self) -> None:
        raw = (EVIDENCE / authority.PRE_ACCOUNTING_REL).read_bytes()
        old = (
            b"0x005d0a9f\tCRT__LongJmpProbe_NoOp\t1\t0x005d0a9f\t0x005d0ad5\t"
            b"0x005d0ad6\t55\t0653a5a9376b7b01ff503a55f62ac23a41ab6a0e49c8de0711903a1aee7de2b2\n"
            b"0x005d0a9f\tCRT__LongJmpProbe_NoOp\t2\t0x005d0aef\t0x005d0b03\t"
            b"0x005d0b04\t21\t06b57f0df63299384b9e42f6c5b8e92521b7bc53e5fadd9ac31d3ec1206ba868\n"
        )
        new = (
            b"0x005d0a9f\tCRT__LongJmpProbe_NoOp\t1\t0x005d0a9f\t0x005d0b03\t"
            b"0x005d0b04\t101\t50016632446f1259b35479440c4a14ca82c8ac59a6c4f78a34f146bd119b61c3\n"
        )
        self.assertEqual(raw.count(old), 1)
        post = raw.replace(old, new)
        self.assertEqual(
            (len(post), hashlib.sha256(post).hexdigest()),
            authority.POST_BODY_RANGES_STAMP,
        )

    def test_scratch_exports_satisfy_future_delta_validators(self) -> None:
        scratch_runs = EVIDENCE / authority.SCRATCH_LANE_REL / "runs"
        with tempfile.TemporaryDirectory() as temporary:
            lane = Path(temporary) / "live-lane"
            pre = lane / "runs/live-pre-readback"
            post = lane / "runs/live-readback"
            pre.mkdir(parents=True)
            post.mkdir(parents=True)
            for name in ("functions.tsv", "program.tsv"):
                shutil.copyfile(scratch_runs / "inventory-pre" / name, pre / name)
                shutil.copyfile(scratch_runs / "inventory-post-a" / name, post / name)
            shutil.copyfile(
                scratch_runs / "inventory-post-a/inventory-diff.json",
                post / "inventory-diff.json",
            )
            run_sources = {
                "live-pre-readback": "replica-a-dry",
                "live-apply": "replica-a-apply",
                "live-readback": "replica-a-readback",
            }
            for destination, source in run_sources.items():
                target = lane / "runs" / destination
                target.mkdir(parents=True, exist_ok=True)
                for name in ("result.tsv", "result.ready.json"):
                    shutil.copyfile(scratch_runs / source / name, target / name)
            synthetic = authority.Config(
                ROOT.resolve(), EVIDENCE.resolve(), LIVE_PROJECT.resolve(),
                lane.resolve(), PRE_BACKUP.resolve(strict=False),
                POST_BACKUP.resolve(strict=False), None,
            )
            functions = authority.validate_function_delta(synthetic)
            program = authority.validate_program_delta(synthetic)
            diff = authority.validate_inventory_diff(synthetic)
            self.assertEqual(functions["unchangedRowsExact"], 8326)
            self.assertEqual(functions["changedAddresses"], ["0x005d0a9f"])
            self.assertEqual(program["changedMetrics"], [
                "instructionLayoutSha256", "instructions", "undefinedData",
            ])
            self.assertEqual(diff["sha256"], authority.sha256_file(
                post / "inventory-diff.json"
            ))
            for mode, run_name in authority.RUN_LAYOUT.items():
                completed = authority.validate_low_level_receipt(
                    synthetic, run_name, mode
                )
                self.assertIsNotNone(completed.tzinfo)

    def test_synthetic_future_accounting_accepts_only_exact_merge(self) -> None:
        pre_body = (EVIDENCE / authority.PRE_ACCOUNTING_REL).read_bytes()
        old = (
            b"0x005d0a9f\tCRT__LongJmpProbe_NoOp\t1\t0x005d0a9f\t0x005d0ad5\t"
            b"0x005d0ad6\t55\t0653a5a9376b7b01ff503a55f62ac23a41ab6a0e49c8de0711903a1aee7de2b2\n"
            b"0x005d0a9f\tCRT__LongJmpProbe_NoOp\t2\t0x005d0aef\t0x005d0b03\t"
            b"0x005d0b04\t21\t06b57f0df63299384b9e42f6c5b8e92521b7bc53e5fadd9ac31d3ec1206ba868\n"
        )
        new = (
            b"0x005d0a9f\tCRT__LongJmpProbe_NoOp\t1\t0x005d0a9f\t0x005d0b03\t"
            b"0x005d0b04\t101\t50016632446f1259b35479440c4a14ca82c8ac59a6c4f78a34f146bd119b61c3\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            lane = Path(temporary) / "live-lane"
            root = lane / "tracked-post-accounting"
            root.mkdir(parents=True)
            body = pre_body.replace(old, new)
            (root / "body-ranges.tsv").write_bytes(body)
            shutil.copyfile(
                EVIDENCE / authority.PRE_DIRECT_CALLS_REL,
                root / "direct-calls.tsv",
            )
            receipt = {
                "schemaVersion": "bea-ghidra-parity-graph-receipt.v2",
                "program": {
                    "executableMd5": authority.PROGRAM_MD5,
                    "imageBase": "0x00400000",
                    "language": "x86:LE:32:default",
                    "compilerSpec": "windows",
                },
                "bodyRanges": {
                    "file": "body-ranges.tsv", "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "functionCount": authority.POST_FUNCTIONS,
                    "rangeCount": authority.POST_RANGES,
                },
                "directCalls": {
                    "file": "direct-calls.tsv",
                    "bytes": authority.DIRECT_CALLS_STAMP[0],
                    "sha256": authority.DIRECT_CALLS_STAMP[1],
                    "directEdgeCount": authority.DIRECT_EDGES,
                    "directCallSiteCount": authority.DIRECT_CALL_SITES,
                },
            }
            (root / "parity-graph.ready.json").write_text(
                json.dumps(receipt), encoding="utf-8"
            )
            (root / "ghidra.log").write_text(
                "Processing read-only project file: /BEA.exe\n"
                f"PARITY_GRAPH_OK functions={authority.POST_FUNCTIONS} "
                f"ranges={authority.POST_RANGES} directEdges={authority.DIRECT_EDGES} "
                f"directCallSites={authority.DIRECT_CALL_SITES}\n",
                encoding="utf-8",
            )
            synthetic = authority.Config(
                ROOT.resolve(), EVIDENCE.resolve(), LIVE_PROJECT.resolve(),
                lane.resolve(), PRE_BACKUP.resolve(strict=False),
                POST_BACKUP.resolve(strict=False), None,
            )
            result, _ = authority.validate_body_accounting(synthetic)
            self.assertEqual(result["ownedBytes"], authority.POST_OWNED)
            self.assertEqual(result["ranges"], authority.POST_RANGES)
            (root / "direct-calls.tsv").write_bytes(b"drift")
            with self.assertRaises(authority.AuthorityError):
                authority.validate_body_accounting(synthetic)


if __name__ == "__main__":
    unittest.main()
