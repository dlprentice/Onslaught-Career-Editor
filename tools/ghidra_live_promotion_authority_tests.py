#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the manifest-driven live-promotion authority."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import tools.ghidra_live_promotion_authority as authority
except ModuleNotFoundError:  # direct execution from tools/
    import ghidra_live_promotion_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARED = Path.home() / "source/Onslaught-Career-Editor"
EVIDENCE_REPO = Path(os.environ.get(
    "BEA_NEW34_EVIDENCE_REPO",
    DEFAULT_SHARED if DEFAULT_SHARED.is_dir() else ROOT,
))
MANIFEST = ROOT / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-new-function-vocabulary-live-authority-2026-08-13.json"
)
LIVE_LANE = Path(os.environ.get(
    "BEA_NEW34_LIVE_LANE",
    Path.home() / "source/Onslaught-Career-Editor/local-lab/"
    "ghidra-mission-registry-new34-live-promotion-20260813-v1",
))
PRE_READBACK = Path(os.environ.get(
    "BEA_NEW34_PRE_READBACK",
    Path.home() / "source/Onslaught-Career-Editor/local-lab/"
    "ghidra-cexplosion-live-promotion-20260813-v1/runs/live-readback",
))
SCRATCH_RECEIPT = Path(os.environ.get(
    "BEA_NEW34_SCRATCH_RECEIPT",
    Path.home() / "source/Onslaught-Career-Editor-lane-mission-registry-new34-vocab/"
    "local-lab/ghidra-mission-registry-new34-vocabulary-20260813-v1/"
    "scratch-authority.ready.json",
))
LIVE_PROJECT = Path(os.environ.get(
    "BEA_LIVE_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects"
))
PRE_BACKUP = Path(os.environ.get(
    "BEA_NEW34_PRE_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-13-mission-registry-new34-pre-live",
))
POST_BACKUP = Path(os.environ.get(
    "BEA_NEW34_POST_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-13-mission-registry-new34-post-live",
))
SAVED_RECEIPT = ROOT / (
    "local-lab/ghidra-mission-registry-new34-live-authority-20260813-v1/"
    "authority.ready.json"
)


def file_stamp(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class ManifestContractTests(unittest.TestCase):
    def test_manifest_encodes_exact_new34_scope(self) -> None:
        value = json.loads(MANIFEST.read_text(encoding="utf-8"))
        delta = value["functionDelta"]
        self.assertEqual(value["schema"], authority.MANIFEST_SCHEMA)
        self.assertEqual((delta["targets"], delta["nonTargets"]), (34, 8136))
        self.assertEqual(len(delta["expectedChangedTargetFields"]), 16)
        self.assertEqual(set(value["runs"]), {"dry", "apply", "readback"})
        ceremony = {
            "ghidra-function-name-table-2026-08-13.tsv", "inventory-diff.json",
            "live-pre-inspect.json", "live-safe-stop-inspect.json",
            "live-after-dry-inspect.json", "live-post-inspect.json",
            "tracked-pre-inspect.json", "tracked-post-inspect.json",
            "refresh_tracked_snapshot.ps1",
        }
        recovery = {
            "pre-backup-restore.ready.json",
            "pre-backup-restore.ready.open-probe.log",
            "post-backup-restore.ready.json",
            "post-backup-restore.ready.open-probe.log",
            "tracked-snapshot-restore.ready.json",
            "tracked-snapshot-restore.ready.open-probe.log",
        }
        runs = {
            f"runs/live-{phase}/{name}"
            for phase, names in {
                "dry": ("ghidra.log", "vocabulary.ready.json", "vocabulary.tsv"),
                "apply": ("ghidra.log", "vocabulary.ready.json", "vocabulary.tsv"),
                "readback": (
                    "ghidra.log", "vocabulary.ready.json", "vocabulary.tsv",
                    "functions.tsv", "program.tsv",
                ),
            }.items()
            for name in names
        }
        self.assertEqual(set(value["artifacts"]), ceremony | recovery | runs)
        self.assertEqual(value["inventoryDiff"]["counts"]["namesChanged"], 34)
        self.assertEqual(value["inventoryDiff"]["changesByField"]["bodyDigest"], 0)
        self.assertIn(["preRestoreVerified", "safeStopInspect"], value["chronology"])
        self.assertIn(["safeStopInspect", "dryCompleted"], value["chronology"])
        self.assertIn("listing-comment record", value["programDelta"]["commentMetricSemantics"])
        self.assertIn("34 new target function comments", value["programDelta"]["observedCommentDelta"])
        self.assertEqual(
            value["projects"]["delta"]["changed"], [],
            "all common PRE/POST project files must remain byte-identical",
        )

    def test_program_metric_keys_remain_case_sensitive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "program.tsv"
            write_tsv(
                path,
                [{"metric": "symbolsUserDefined", "value": "6104"}],
                ["metric", "value"],
            )
            rows, order = authority.load_program(path)
        self.assertEqual(order, ("symbolsUserDefined",))
        self.assertEqual(rows, {"symbolsUserDefined": "6104"})


class InventoryDeltaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fields = [
            "address", "name", "nameLen", "nameSha256", "fqname", "fqnameLen",
            "fqnameSha256", "nameSource", "signature", "signatureLen",
            "signatureSha256", "commentPresent", "commentLen", "commentSha256",
            "repeatableCommentPresent", "repeatableCommentSha256", "tagCount",
            "tagsSha256", "tags", "bodyDigest",
        ]
        self.spec = {
            "functionCount": 2,
            "targets": 1,
            "nonTargets": 1,
            "expectedChangedTargetFields": [
                "commentLen", "commentPresent", "commentSha256", "fqname",
                "fqnameLen", "fqnameSha256", "name", "nameLen", "nameSha256",
                "nameSource", "signature", "signatureLen", "signatureSha256",
                "tagCount", "tags", "tagsSha256",
            ],
            "expectedPreNameField": "expectedPreName",
            "proposedNameField": "proposedName",
            "expectedPreSourceField": "expectedNameSource",
            "postNameSource": "USER_DEFINED",
            "postTags": ["script-command-registry", "tier2-script-facing-name"],
        }

    def rows(self) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        target = {
            "address": "0x00000001", "name": "FUN_1", "nameLen": "5",
            "nameSha256": "pre-name", "fqname": "FUN_1", "fqnameLen": "5",
            "fqnameSha256": "pre-fqname", "nameSource": "DEFAULT",
            "signature": "void FUN_1(void)", "signatureLen": "16",
            "signatureSha256": "pre-signature", "commentPresent": "false",
            "commentLen": "0", "commentSha256": "empty",
            "repeatableCommentPresent": "false", "repeatableCommentSha256": "empty",
            "tagCount": "0", "tagsSha256": "empty", "tags": "",
            "bodyDigest": "stable-body",
        }
        post = dict(target)
        post.update({
            "name": "IScript__Thing", "nameLen": "14", "nameSha256": "post-name",
            "fqname": "IScript__Thing", "fqnameLen": "14",
            "fqnameSha256": "post-fqname", "nameSource": "USER_DEFINED",
            "signature": "void IScript__Thing(void)", "signatureLen": "25",
            "signatureSha256": "post-signature", "commentPresent": "true",
            "commentLen": "12", "commentSha256": "post-comment", "tagCount": "2",
            "tagsSha256": "post-tags",
            "tags": "script-command-registry,tier2-script-facing-name",
        })
        other = dict(target, address="0x00000002", name="Stable", fqname="Stable")
        return [target, other], [post, dict(other)]

    def compare(self, poison_non_target: bool = False) -> dict[str, object]:
        before, after = self.rows()
        if poison_non_target:
            after[1]["bodyDigest"] = "changed"
        targets = {"0x00000001": {
            "expectedPreName": "FUN_1", "proposedName": "IScript__Thing",
            "expectedNameSource": "DEFAULT",
        }}
        with tempfile.TemporaryDirectory() as raw:
            pre, post = Path(raw) / "pre.tsv", Path(raw) / "post.tsv"
            write_tsv(pre, before, self.fields)
            write_tsv(post, after, self.fields)
            return authority.compare_function_inventories(pre, post, targets, self.spec)

    def test_accepts_exact_target_only_delta(self) -> None:
        result = self.compare()
        self.assertEqual(result["nonTargetsByteIdentical"], 1)
        self.assertEqual(len(result["changedTargetFields"]), 16)

    def test_rejects_one_non_target_byte_delta(self) -> None:
        with self.assertRaisesRegex(authority.AuthorityError, "non-target"):
            self.compare(poison_non_target=True)


class SavedReceiptPortabilityTests(unittest.TestCase):
    @staticmethod
    def make_inputs(root: Path) -> authority.Config:
        repo = root / "repo"
        lane = root / "lane"
        pre = root / "pre"
        scratch = root / "scratch/ready.json"
        pre_backup = root / "pre-backup"
        post_backup = root / "post-backup"
        for path, content in (
            (repo / "tracked.txt", "tracked\n"),
            (lane / "artifact.txt", "artifact\n"),
            (pre / "functions.tsv", "functions\n"),
            (pre / "program.tsv", "program\n"),
            (scratch, "{}\n"),
            (pre_backup / "backup_manifest.json", "{}\n"),
            (post_backup / "backup_manifest.json", "{}\n"),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        manifest = {
            "trackedFiles": {"tracked.txt": file_stamp(repo / "tracked.txt")},
            "artifacts": {"artifact.txt": file_stamp(lane / "artifact.txt")},
            "retainedProjectRoots": [],
            "externalStamps": {
                "preFunctions": file_stamp(pre / "functions.tsv"),
                "preProgram": file_stamp(pre / "program.tsv"),
                "scratchReceipt": file_stamp(scratch),
                "preBackupManifest": file_stamp(pre_backup / "backup_manifest.json"),
                "postBackupManifest": file_stamp(post_backup / "backup_manifest.json"),
            },
        }
        manifest_path = repo / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        return authority.Config(
            repo, manifest_path, lane, pre, scratch, root / "live-project",
            pre_backup, post_backup, repo / "local-lab/authority.ready.json",
        )

    def test_saved_verify_survives_checkout_root_change(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            first = self.make_inputs(Path(raw) / "checkout-a")
            second = self.make_inputs(Path(raw) / "checkout-b")

            def evidence(config: authority.Config) -> dict[str, object]:
                manifest = json.loads(config.manifest_path.read_text(encoding="utf-8"))
                return authority.validate_stamps(config, manifest)

            with patch.object(authority, "validate_output_path"), \
                 patch.object(authority, "build", side_effect=evidence):
                authority.seal(first)
                second.output.parent.mkdir(parents=True)
                shutil.copyfile(first.output, second.output)
                authority.verify(second)

            saved = second.output.read_text(encoding="utf-8")
            self.assertNotIn(str(first.repo), saved)
            self.assertNotIn(str(second.repo), saved)
            value = json.loads(saved)
            self.assertEqual(
                value["evidence"]["tracked"]["tracked.txt"]["role"], "tracked.txt"
            )


RETAINED_AVAILABLE = all(path.exists() for path in (
    MANIFEST, LIVE_LANE, PRE_READBACK / "functions.tsv", SCRATCH_RECEIPT,
    LIVE_PROJECT / "BEA.gpr", PRE_BACKUP / "backup_manifest.json",
    POST_BACKUP / "backup_manifest.json", SAVED_RECEIPT,
))


@unittest.skipUnless(RETAINED_AVAILABLE, "retained new34 authority evidence is unavailable")
class RetainedEvidenceTests(unittest.TestCase):
    def test_saved_retained_receipt_reproduces_without_opening_ghidra(self) -> None:
        config = authority.Config(
            EVIDENCE_REPO, MANIFEST, LIVE_LANE, PRE_READBACK, SCRATCH_RECEIPT, LIVE_PROJECT,
            PRE_BACKUP, POST_BACKUP, SAVED_RECEIPT,
        )
        authority.verify(config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
