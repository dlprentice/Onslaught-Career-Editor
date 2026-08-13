#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/ghidra_cexplosion_factory_identity_promotion_authority.py"
SPEC = importlib.util.spec_from_file_location("cexplosion_authority", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    fields = fields or list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class CExplosionManifestTests(unittest.TestCase):
    def test_manifest_is_exactly_one_proof_bound_row(self) -> None:
        row = owner.manifest_row()
        self.assertEqual(row["address"], owner.TARGET)
        self.assertEqual(row["postName"], "CWorldPhysicsManager__CreateExplosion")
        self.assertEqual(
            row["postSignature"],
            "void * __cdecl CWorldPhysicsManager__CreateExplosion(int explosion_definition_index)",
        )
        self.assertEqual(row["callingConvention"], "__cdecl")
        self.assertEqual(row["returnStorage"], "EAX:4")
        self.assertEqual(row["parameterStorage"], "Stack[0x4]:4")
        self.assertEqual(row["preParameterSource"], "USER_DEFINED")
        self.assertEqual(row["postParameterSource"], "USER_DEFINED")
        self.assertNotIn("pickup", row["postTags"].split(","))
        self.assertIn("explosion", row["postTags"].split(","))
        self.assertIn("identity-corrected", row["postTags"].split(","))

    def test_all_current_immutable_stamps_match(self) -> None:
        for path in owner.STAMPS:
            owner.require_stamp(path)

    def test_historical_worktree_claim_normalizes_without_dereferencing(self) -> None:
        expected = owner.REPO / "tools/GhidraProjectOpenProbe.java"
        historical = (
            r"C:\historical-worktree\tools\GhidraProjectOpenProbe.java"
        )
        self.assertEqual(
            owner.require_repo_path_claim(
                historical, expected, "test", allow_absolute_legacy=True
            ),
            "tools/GhidraProjectOpenProbe.java",
        )
        with self.assertRaisesRegex(owner.AuthorityError, "recognized historical"):
            owner.require_repo_path_claim(
                r"C:\historical-worktree\tools\Different.java",
                expected,
                "test",
                allow_absolute_legacy=True,
            )

    def test_saved_authority_verifies_from_current_repository_root(self) -> None:
        saved = owner.verify_saved()
        self.assertEqual(saved["verdict"], "READY")
        probe_copy = Path(saved["baseline"]["restore"]["probeCopy"])
        self.assertFalse(probe_copy.is_absolute())
        self.assertEqual(
            probe_copy.parent.as_posix(),
            "local-lab/ghidra-cexplosion-identity-scratch-20260813-v7/restore-probe",
        )
        self.assertEqual(
            saved["baseline"]["restore"]["commandArgv"][8], "tools"
        )
        self.assertEqual(saved["result"]["preTransactionPathControls"], 2)
        for control in saved["preTransactionControls"]["controls"].values():
            self.assertTrue(control["rejectedBeforePreValidation"])
            self.assertTrue(control["rejectedBeforeTransaction"])
            self.assertEqual(control["publishedArtifacts"], 0)


class CExplosionInventoryGateTests(unittest.TestCase):
    def test_target_readback_requires_exact_parameter_source(self) -> None:
        expected = owner.expected_target("PRE")
        expected["mode"] = "dry"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "target.tsv"
            write_tsv(path, [expected])
            owner.validate_target_tsv(path, "dry", "PRE")
            poisoned = dict(expected, parameterSource="DEFAULT")
            write_tsv(path, [poisoned])
            with self.assertRaisesRegex(owner.AuthorityError, "parameterSource differs"):
                owner.validate_target_tsv(path, "dry", "PRE")

    @staticmethod
    def baseline_target() -> dict[str, str]:
        row = owner.manifest_row()
        name, signature, tags = row["preName"], row["preSignature"], row["preTags"]
        result = {
            "address": owner.TARGET, "name": name, "nameLen": str(len(name)),
            "nameSha256": owner.sha256_text(name), "fqname": name,
            "fqnameLen": str(len(name)), "fqnameSha256": owner.sha256_text(name),
            "signature": signature, "signatureLen": str(len(signature)),
            "signatureSha256": owner.sha256_text(signature),
            "commentLen": row["preCommentBytes"],
            "commentSha256": row["preCommentSha256"],
            "tagCount": str(len(tags.split(","))),
            "tagsSha256": owner.inventory_sorted_digest(tags.split(",")),
            "tags": tags, "bodyBytes": row["bodyBytes"], "callingConv": "__cdecl",
            "returnType": "void *", "returnStorage": "EAX:4",
            "paramCount": "1", "paramSize": "4", "frameSize": "20",
            "localSize": "16", "nameSource": "USER_DEFINED",
            "sigSource": "USER_DEFINED", "bodyDigest": row["bodyRangeSha256"],
            "instrCount": row["instructionCount"], "commentPresent": "true",
            "repeatableCommentPresent": "false", "repeatableCommentLen": "0",
            "repeatableCommentSha256": owner.sha256_text(""), "isThunk": "false",
            "thunkTarget": "", "isExternal": "false", "customStorage": "false",
            "inline": "false", "noReturn": "false", "varArgs": "false",
        }
        return result

    @staticmethod
    def post_target(before: dict[str, str]) -> dict[str, str]:
        row = owner.manifest_row()
        result = dict(before)
        name, signature, tags = row["postName"], row["postSignature"], row["postTags"]
        result.update({
            "name": name, "nameLen": str(len(name)), "nameSha256": owner.sha256_text(name),
            "fqname": name, "fqnameLen": str(len(name)),
            "fqnameSha256": owner.sha256_text(name), "signature": signature,
            "signatureLen": str(len(signature)),
            "signatureSha256": owner.sha256_text(signature),
            "commentLen": row["postCommentBytes"],
            "commentSha256": row["postCommentSha256"],
            "tagCount": str(len(tags.split(","))),
            "tagsSha256": owner.inventory_sorted_digest(tags.split(",")),
            "tags": tags,
        })
        return result

    def run_inventory(self, pre: list[dict[str, str]], post: list[dict[str, str]]) -> dict:
        with tempfile.TemporaryDirectory() as folder:
            pre_path, post_path = Path(folder) / "pre.tsv", Path(folder) / "post.tsv"
            fields = list(pre[0])
            write_tsv(pre_path, pre, fields)
            write_tsv(post_path, post, fields)
            with patch.object(owner, "PRE_FUNCTIONS", pre_path), \
                 patch.object(owner, "FUNCTION_COUNT", len(pre)):
                return owner.compare_inventories(post_path, "test")

    def test_accepts_only_target_metadata_columns(self) -> None:
        target = self.baseline_target()
        other = dict(target, address="0x00401000", name="Other", fqname="Other")
        result = self.run_inventory([other, target], [other, self.post_target(target)])
        self.assertEqual(result["changedAddresses"], [owner.TARGET])
        self.assertEqual(result["nonTargetRowsUnchanged"], 1)

    def test_rejects_non_target_row_change(self) -> None:
        target = self.baseline_target()
        other = dict(target, address="0x00401000", name="Other", fqname="Other")
        changed_other = dict(other, name="Changed")
        with self.assertRaisesRegex(owner.AuthorityError, "changed function rows"):
            self.run_inventory([other, target], [changed_other, self.post_target(target)])

    def test_rejects_target_abi_change(self) -> None:
        target = self.baseline_target()
        post = self.post_target(target)
        post["callingConv"] = "__thiscall"
        with self.assertRaisesRegex(owner.AuthorityError, "changed target columns"):
            self.run_inventory([target], [post])

    def test_rejects_target_body_change(self) -> None:
        target = self.baseline_target()
        post = self.post_target(target)
        post["bodyDigest"] = "changed"
        with self.assertRaisesRegex(owner.AuthorityError, "changed target columns"):
            self.run_inventory([target], [post])


class CExplosionProgramGateTests(unittest.TestCase):
    def run_program(self, pre: list[dict[str, str]], post: list[dict[str, str]]) -> dict:
        with tempfile.TemporaryDirectory() as folder:
            pre_path, post_path = Path(folder) / "pre.tsv", Path(folder) / "post.tsv"
            write_tsv(pre_path, pre)
            write_tsv(post_path, post)
            with patch.object(owner, "PRE_PROGRAM", pre_path):
                return owner.compare_programs(post_path, "test")

    @staticmethod
    def rows() -> list[dict[str, str]]:
        return [
            {"metric": "commentsSha256", "value": "pre"},
            {"metric": "memorySha256", "value": "memory"},
            {"metric": "instructionLayoutSha256", "value": "instructions"},
            {"metric": "definedDataSha256", "value": "data"},
            {"metric": "undefinedData", "value": "4"},
            {"metric": "nonFunctionSymbolsSha256", "value": "symbols"},
            {"metric": "referencesSha256", "value": "refs"},
            {"metric": "comments", "value": "9"},
        ]

    def test_allows_only_exact_comment_digest_delta(self) -> None:
        pre = self.rows()
        post = [dict(row) for row in pre]
        post[0]["value"] = "7bf6458538656da36fea94f5ca62c41ca026d75f489e2b59fc3fd3c502c62c2a"
        result = self.run_program(pre, post)
        self.assertEqual(result["changedMetrics"], ["commentsSha256"])
        self.assertTrue(result["referencesUnchanged"])

    def test_rejects_reference_drift(self) -> None:
        pre = self.rows()
        post = [dict(row) for row in pre]
        post[0]["value"] = "7bf6458538656da36fea94f5ca62c41ca026d75f489e2b59fc3fd3c502c62c2a"
        post[6]["value"] = "changed"
        with self.assertRaisesRegex(owner.AuthorityError, "program changes"):
            self.run_program(pre, post)

    def test_rejects_data_drift(self) -> None:
        pre = self.rows()
        post = [dict(row) for row in pre]
        post[0]["value"] = "7bf6458538656da36fea94f5ca62c41ca026d75f489e2b59fc3fd3c502c62c2a"
        post[3]["value"] = "changed"
        with self.assertRaisesRegex(owner.AuthorityError, "program changes"):
            self.run_program(pre, post)


if __name__ == "__main__":
    unittest.main()
