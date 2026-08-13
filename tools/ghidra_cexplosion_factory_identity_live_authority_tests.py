#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the one-row CExplosion identity live authority."""

from __future__ import annotations

import csv
import inspect
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tools.ghidra_cexplosion_factory_identity_live_authority as AUTH


class CExplosionFactoryIdentityLiveAuthorityTests(unittest.TestCase):
    CHRONOLOGY_KEYS = (
        "livePreInspect", "trackedPreInspect", "preBackupCreated",
        "preRestoreVerified", "dryCompleted", "afterDryInspect",
        "applyCompleted", "readbackCompleted", "livePostInspect",
        "postBackupCreated", "postRestoreVerified", "trackedPostInspect",
        "trackedRestoreVerified",
    )

    @classmethod
    def _chronology(cls) -> dict[str, datetime]:
        start = datetime(2026, 8, 13, tzinfo=timezone.utc)
        result = {
            name: start + timedelta(seconds=index)
            for index, name in enumerate(cls.CHRONOLOGY_KEYS)
        }
        # The two independent PRE inspections need only precede the backup.
        result["livePreInspect"] = start
        result["trackedPreInspect"] = start
        return result

    def test_base_scratch_post_and_projection_hashes_are_exact(self):
        self.assertEqual(
            AUTH.BASE_COMMIT, "daf7b3c7512fdfb078dabe9d6cde6b2648c19e58")
        self.assertEqual(
            AUTH.SCRATCH_SEAL_SHA256,
            "a7cc0d76b1429d4a18aaa68b9bc506d378f1663041438cf50593bf416218ab6e",
        )
        self.assertEqual(
            AUTH.POST_PROJECT_SHA256,
            "8eb664062a8ba67005e9f8ad8f61aa2222585622c41022a69080c5e408cd3cf6",
        )
        self.assertEqual(
            AUTH.POST_DB_SHA256,
            "210a0461a6b1746f7bbc53e883b616c4a02694a055f1bd23ccadaf44472c1356",
        )
        self.assertEqual(
            AUTH.PROJECTION_SHA256,
            "515170759dda2686db408d25296362275f8913f7be42b6f0536b986c591786ee",
        )

    def test_live_ledger_covers_three_phases_inspections_and_recovery(self):
        expected = {
            "runs/live-dry/ghidra.log",
            "runs/live-dry/cexplosion.ready.json",
            "runs/live-dry/cexplosion.tsv",
            "runs/live-apply/ghidra.log",
            "runs/live-apply/cexplosion.ready.json",
            "runs/live-apply/cexplosion.tsv",
            "runs/live-readback/ghidra.log",
            "runs/live-readback/cexplosion.ready.json",
            "runs/live-readback/cexplosion.tsv",
            "runs/live-readback/functions.tsv",
            "runs/live-readback/program.tsv",
            "live-pre-inspect.json",
            "live-after-dry-inspect.json",
            "live-post-inspect.json",
            "tracked-pre-inspect.json",
            "tracked-post-inspect.json",
            "pre-backup-restore.ready.json",
            "post-backup-restore.ready.json",
            "tracked-snapshot-restore.ready.json",
        }
        self.assertTrue(expected <= set(AUTH.LIVE_ARTIFACT_STAMPS))
        self.assertIn("tracked-pre-db.18608.gbf", AUTH.LIVE_ARTIFACT_STAMPS)
        self.assertEqual(len(AUTH.LIVE_ARTIFACT_STAMPS), 24)

    def test_committed_ledger_binds_v7_and_common_ceremony_tools(self):
        self.assertTrue({
            "tools/GhidraApplyCExplosionFactoryIdentity.java",
            "tools/GhidraInspectCExplosionFactoryIdentity.java",
            "tools/ghidra_cexplosion_factory_identity_promotion_authority.py",
            "tools/re_cexplosion_factory_identity_reproof.py",
            "tools/ExportFullFunctionInventory.java",
            "tools/GhidraProjectOpenProbe.java",
            "tools/ghidra_project_backup.py",
            "tools/re_ghidra_name_projection.py",
            "reverse-engineering/binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.md",
            "reverse-engineering/binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.tsv",
        } <= set(AUTH.COMMITTED_FILES))
        self.assertEqual(len(AUTH.COMMITTED_FILES), 13)

    def test_project_digest_sorts_rendered_lines_and_appends_lf(self):
        project = {"files": [
            {"relative_path": "z", "size": 2, "sha256": "0" * 64},
            {"relative_path": "a", "size": 1, "sha256": "f" * 64},
        ]}
        payload = (f"{'0' * 64}\t2\tz\n{'f' * 64}\t1\ta\n").encode()
        self.assertEqual(AUTH.canonical_project_digest(project), AUTH.sha256_bytes(payload))

    def test_authority_tool_stamp_is_repository_relative_and_self_binds(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            shared = root / AUTH.AUTHORITY_TOOL_RELATIVE
            shared.parent.mkdir(parents=True)
            shutil.copyfile(AUTH.SCRIPT, shared)
            config = AUTH.Config(root, root, root, root, root, root, root)
            result = AUTH.authority_tool_stamp(config)
            self.assertEqual(result["path"], AUTH.AUTHORITY_TOOL_RELATIVE.as_posix())
            self.assertEqual(result["sha256"], AUTH.sha256_file(AUTH.SCRIPT))
            shared.write_bytes(shared.read_bytes() + b"\n")
            with self.assertRaisesRegex(AUTH.AuthorityError, "shared repository copy"):
                AUTH.authority_tool_stamp(config)

    @staticmethod
    def _write_logs(root: Path, *, second_apply: bool = False) -> None:
        for phase in ("dry", "apply", "readback"):
            path = root / f"live-{phase}/ghidra.log"
            path.parent.mkdir(parents=True)
            mutating = phase == "apply" or (phase == "dry" and second_apply)
            text = ""
            if mutating:
                text = (
                    "CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE\n"
                    "REPORT: Processing project file: /BEA.exe\n"
                    "Save succeeded for processed file: /BEA.exe\n"
                )
            path.write_text(text, encoding="utf-8")

    def test_exactly_one_mutation_log_is_accepted(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._write_logs(root)
            result = AUTH.validate_one_mutation_log(root)
            self.assertEqual((result["logs"], result["mutationLogs"]), (3, 1))

    def test_second_mutation_log_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._write_logs(root, second_apply=True)
            with self.assertRaisesRegex(AUTH.AuthorityError, "exactly one"):
                AUTH.validate_one_mutation_log(root)

    @staticmethod
    def _manifest() -> dict[str, str]:
        result = {
            "preName": "CWorldPhysicsManager__CreatePickup",
            "postName": "CWorldPhysicsManager__CreateExplosion",
            "preSignature": "void * __cdecl CWorldPhysicsManager__CreatePickup(int pickup_type)",
            "postSignature": "void * __cdecl CWorldPhysicsManager__CreateExplosion(int explosion_definition_index)",
            "preParameterName": "pickup_type",
            "postParameterName": "explosion_definition_index",
            "preParameterSource": "USER_DEFINED",
            "postParameterSource": "USER_DEFINED",
            "parameterType": "int",
            "parameterStorage": "Stack[0x4]:4",
            "callingConvention": "__cdecl",
            "returnType": "void *",
            "returnStorage": "EAX:4",
            "bodyRanges": "0x0050ff10-0x0050ffa7",
            "bodyBytes": "152",
            "bodyRangeSha256": "range",
            "bodyBytesSha256": "bytes",
            "instructionCount": "39",
            "preCommentBytes": "512",
            "preCommentSha256": "pre-comment",
            "postCommentBytes": "915",
            "postCommentSha256": "post-comment",
            "preTags": "factory,pickup",
            "postTags": "explosion,factory,identity-corrected",
        }
        return result

    @classmethod
    def _target_output(cls, state: str) -> dict[str, str]:
        manifest = cls._manifest()
        prefix = "pre" if state == "PRE" else "post"
        result = {
            "address": AUTH.TARGET,
            "mode": "dry" if state == "PRE" else "readback",
            "state": state,
            "name": manifest[prefix + "Name"],
            "nameSource": "USER_DEFINED",
            "signatureSource": "USER_DEFINED",
            "signature": manifest[prefix + "Signature"],
            "parameterName": manifest[prefix + "ParameterName"],
            "parameterType": manifest["parameterType"],
            "parameterStorage": manifest["parameterStorage"],
            "parameterSource": manifest[prefix + "ParameterSource"],
            "callingConvention": manifest["callingConvention"],
            "returnType": manifest["returnType"],
            "returnStorage": manifest["returnStorage"],
            "bodyRanges": manifest["bodyRanges"],
            "bodyBytes": manifest["bodyBytes"],
            "bodyRangeSha256": manifest["bodyRangeSha256"],
            "bodyBytesSha256": manifest["bodyBytesSha256"],
            "instructionCount": manifest["instructionCount"],
            "commentBytes": manifest[prefix + "CommentBytes"],
            "commentSha256": manifest[prefix + "CommentSha256"],
            "tags": manifest[prefix + "Tags"],
        }
        result["tagsSha256"] = AUTH.sha256_bytes(result["tags"].encode("utf-8"))
        return result

    def test_target_row_binds_parameter_source_and_all_abi_storage(self):
        AUTH.validate_target_row(self._target_output("PRE"), self._manifest(), "PRE")
        AUTH.validate_target_row(self._target_output("POST"), self._manifest(), "POST")

    def test_target_row_rejects_parameter_source_or_storage_drift(self):
        for field in ("parameterSource", "parameterStorage", "returnStorage"):
            with self.subTest(field=field):
                row = self._target_output("POST")
                row[field] = "wrong"
                with self.assertRaisesRegex(AUTH.AuthorityError, field):
                    AUTH.validate_target_row(row, self._manifest(), "POST")

    @classmethod
    def _inventory_triplet(cls) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        manifest = cls._manifest()
        before = {key: "pre-" + key for key in AUTH.EXPECTED_CHANGED_TARGET_FIELDS}
        after = {key: "post-" + key for key in AUTH.EXPECTED_CHANGED_TARGET_FIELDS}
        before.update({
            "name": manifest["preName"], "fqname": manifest["preName"],
            "nameSource": "USER_DEFINED", "sigSource": "USER_DEFINED",
            "signature": manifest["preSignature"], "commentLen": "512",
            "commentSha256": manifest["preCommentSha256"],
            "tags": manifest["preTags"], "stableAbi": "same",
        })
        after.update({
            "name": manifest["postName"], "fqname": manifest["postName"],
            "nameSource": "USER_DEFINED", "sigSource": "USER_DEFINED",
            "signature": manifest["postSignature"], "commentLen": "915",
            "commentSha256": manifest["postCommentSha256"],
            "tags": manifest["postTags"], "stableAbi": "same",
        })
        return before, after, manifest

    def test_one_target_only_inventory_delta_is_accepted(self):
        before, after, manifest = self._inventory_triplet()
        stable = {"name": "other", "stableAbi": "same"}
        result = AUTH.compare_inventory_records(
            {AUTH.TARGET: before, "0x1": stable},
            {AUTH.TARGET: after, "0x1": dict(stable)},
            {AUTH.TARGET: manifest},
        )
        self.assertEqual(result["nonTargetsByteIdentical"], 1)
        self.assertEqual(result["changedTargetFields"], AUTH.EXPECTED_CHANGED_TARGET_FIELDS)

    def test_non_target_or_target_abi_delta_is_rejected(self):
        before, after, manifest = self._inventory_triplet()
        with self.assertRaisesRegex(AUTH.AuthorityError, "non-target"):
            AUTH.compare_inventory_records(
                {AUTH.TARGET: before, "0x1": {"name": "before"}},
                {AUTH.TARGET: after, "0x1": {"name": "after"}},
                {AUTH.TARGET: manifest},
            )
        after = dict(after)
        after["stableAbi"] = "changed"
        with self.assertRaisesRegex(AUTH.AuthorityError, "target delta"):
            AUTH.compare_inventory_records(
                {AUTH.TARGET: before}, {AUTH.TARGET: after}, {AUTH.TARGET: manifest}
            )
        after = dict(self._inventory_triplet()[1])
        after["unexpectedColumn"] = "unexpected"
        with self.assertRaisesRegex(AUTH.AuthorityError, "columns changed"):
            AUTH.compare_inventory_records(
                {AUTH.TARGET: before}, {AUTH.TARGET: after}, {AUTH.TARGET: manifest}
            )

    def test_program_comparator_accepts_only_comment_digest_delta(self):
        base = {
            "programName": "BEA.exe", "executableSHA256": AUTH.PROGRAM_SHA256,
            "functions": str(AUTH.FUNCTION_COUNT),
            "instructions": str(AUTH.INSTRUCTION_COUNT),
            "symbolsUserDefined": "6070", "symbolsDefaultOther": "61628",
            "comments": "9165", "commentsSha256": "pre",
        }
        post = dict(base)
        post["commentsSha256"] = "post"
        with tempfile.TemporaryDirectory() as raw:
            paths = [Path(raw) / name for name in ("pre.tsv", "post.tsv")]
            for path, values in zip(paths, (base, post)):
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
                    writer.writerow(("metric", "value"))
                    writer.writerows(values.items())
            result = AUTH.compare_programs(*paths)
            self.assertEqual(result["changedMetrics"], ["commentsSha256"])
            post["comments"] = "9166"
            with paths[1].open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
                writer.writerow(("metric", "value"))
                writer.writerows(post.items())
            with self.assertRaisesRegex(AUTH.AuthorityError, "program collateral"):
                AUTH.compare_programs(*paths)

    def test_complete_restore_chronology_is_accepted(self):
        result = AUTH.validate_ceremony_chronology(self._chronology())
        self.assertEqual(len(result["relations"]), 12)
        self.assertTrue(result["freshPreBackupRestoredBeforeDry"])
        self.assertTrue(result["postBackupRestoredAfterReadback"])
        self.assertTrue(result["trackedRefreshRestoredAfterInspection"])

    def test_pre_restore_after_dry_is_rejected(self):
        times = self._chronology()
        times["preRestoreVerified"] = times["dryCompleted"]
        with self.assertRaisesRegex(
            AUTH.AuthorityError, "preRestoreVerified !< dryCompleted"
        ):
            AUTH.validate_ceremony_chronology(times)

    def test_post_restore_before_post_backup_is_rejected(self):
        times = self._chronology()
        times["postRestoreVerified"] = times["postBackupCreated"]
        with self.assertRaisesRegex(
            AUTH.AuthorityError, "postBackupCreated !< postRestoreVerified"
        ):
            AUTH.validate_ceremony_chronology(times)

    def test_tracked_restore_before_tracked_inspection_is_rejected(self):
        times = self._chronology()
        times["trackedRestoreVerified"] = times["trackedPostInspect"]
        with self.assertRaisesRegex(
            AUTH.AuthorityError, "trackedPostInspect !< trackedRestoreVerified"
        ):
            AUTH.validate_ceremony_chronology(times)

    def test_semantic_doc_contract_does_not_pin_mutable_file_hash(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "owner.md"
            path.write_text("required fact\nadditional synthesis\n", encoding="utf-8")
            AUTH.require_text_contract(path, ["required fact"], ["stale fact"])
            path.write_text("required fact\nstale fact\n", encoding="utf-8")
            with self.assertRaisesRegex(AUTH.AuthorityError, "stale documentation"):
                AUTH.require_text_contract(path, ["required fact"], ["stale fact"])

    def test_build_includes_current_documentation_validation(self):
        source = inspect.getsource(AUTH.build)
        self.assertIn("validate_documentation(config)", source)
        self.assertIn('"currentDocumentation": documentation', source)

    def test_build_does_not_reinvoke_historical_scratch_suite_or_ghidra(self):
        source = inspect.getsource(AUTH.build)
        self.assertNotIn("promotion_authority_tests", source)
        self.assertNotIn("analyzeHeadless", source)
        self.assertIn('"historicalScratchVerifierIsOneShot": True', Path(AUTH.__file__).read_text())


if __name__ == "__main__":
    unittest.main()
