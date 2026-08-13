#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the Mission-registry vocabulary live authority."""

from __future__ import annotations

import csv
import inspect
import shutil
import tempfile
import unittest
from pathlib import Path

import tools.ghidra_mission_registry_vocabulary_live_authority as AUTH


class MissionRegistryVocabularyLiveAuthorityTests(unittest.TestCase):
    def test_historical_base_and_final_hashes_are_exact(self):
        self.assertEqual(
            AUTH.BASE_COMMIT, "0132d3cdd55a335e1f0d3e64de0f13de24477356")
        self.assertEqual(
            AUTH.SCRATCH_SEAL_SHA256,
            "1ee8f6b1a9cca61857f528f173b40828172ed0bee82dc751ec65e26276d3b4e0")
        self.assertEqual(
            AUTH.POST_PROJECT_SHA256,
            "b0635c394c57ddbc7ccbe8f239c2fec811e445bffca7d813e1d562c0d350c6ef")
        self.assertEqual(
            AUTH.PROJECTION_SHA256,
            "f7f987b55730fb074d8b1fe31998553a9b94432dea31b1134f6a207defdfa51e")

    def test_live_artifact_ledger_covers_all_three_phases_and_recovery(self):
        expected = {
            "runs/live-dry/ghidra.log", "runs/live-dry/vocabulary.ready.json",
            "runs/live-dry/vocabulary.tsv", "runs/live-apply/ghidra.log",
            "runs/live-apply/vocabulary.ready.json", "runs/live-apply/vocabulary.tsv",
            "runs/live-readback/ghidra.log",
            "runs/live-readback/vocabulary.ready.json",
            "runs/live-readback/vocabulary.tsv", "runs/live-readback/functions.tsv",
            "runs/live-readback/program.tsv", "pre-backup-restore.ready.json",
            "post-backup-restore.ready.json", "tracked-snapshot-restore.ready.json",
        }
        self.assertTrue(expected <= set(AUTH.LIVE_ARTIFACT_STAMPS))
        self.assertEqual(len(AUTH.LIVE_ARTIFACT_STAMPS), 22)

    def test_project_digest_sorts_rendered_lines_and_has_trailing_lf(self):
        project = {"files": [
            {"relative_path": "z", "size": 2, "sha256": "0" * 64},
            {"relative_path": "a", "size": 1, "sha256": "f" * 64},
        ]}
        payload = (
            f"{'0' * 64}\t2\tz\n"
            f"{'f' * 64}\t1\ta\n"
        ).encode()
        self.assertEqual(AUTH.canonical_project_digest(project), AUTH.sha256_bytes(payload))

    def test_committed_tool_ledger_includes_mutator_exporter_probe_and_backup(self):
        self.assertTrue({
            "tools/GhidraApplyMissionRegistryVocabulary.java",
            "tools/ExportFullFunctionInventory.java",
            "tools/GhidraProjectOpenProbe.java",
            "tools/ghidra_project_backup.py",
            "tools/ghidra_mission_registry_vocabulary_authority.py",
        } <= set(AUTH.COMMITTED_FILES))
        self.assertEqual(len(AUTH.COMMITTED_FILES), 10)

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

    def _write_logs(self, root: Path, second_apply: bool = False) -> None:
        for phase in ("dry", "apply", "readback"):
            path = root / f"live-{phase}/ghidra.log"
            path.parent.mkdir(parents=True)
            markers = ""
            if phase == "apply" or (phase == "dry" and second_apply):
                markers = (
                    "MISSION_REGISTRY_VOCABULARY_APPLY_COMPLETE\n"
                    "REPORT: Processing project file: /BEA.exe\n"
                    "Save succeeded for processed file: /BEA.exe\n"
                )
            path.write_text(markers, encoding="utf-8")

    def test_exactly_one_mutation_log_is_accepted(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._write_logs(root)
            result = AUTH.validate_one_mutation_log(root)
            self.assertEqual(result["logs"], 3)
            self.assertEqual(result["mutationLogs"], 1)

    def test_second_mutation_log_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._write_logs(root, second_apply=True)
            with self.assertRaisesRegex(AUTH.AuthorityError, "exactly one"):
                AUTH.validate_one_mutation_log(root)

    @staticmethod
    def _target_rows() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        before = {key: "same" for key in AUTH.ALLOWED_TARGET_FIELDS}
        before.update({"name": "FUN_1", "fqname": "FUN_1", "nameSource": "DEFAULT",
                       "signature": "void FUN_1(void)", "stable": "unchanged"})
        after = dict(before)
        for key in AUTH.ALLOWED_TARGET_FIELDS:
            after[key] = "changed-" + key
        after.update({"name": "IScript__Thing", "fqname": "IScript__Thing",
                      "nameSource": "USER_DEFINED",
                      "signature": "void IScript__Thing(void)"})
        target = {"expectedPreName": "FUN_1", "proposedName": "IScript__Thing"}
        return before, after, target

    def test_target_only_inventory_delta_is_accepted(self):
        before, after, target = self._target_rows()
        stable = {"name": "other", "stable": "same"}
        result = AUTH.compare_inventory_records(
            {"0x1": before, "0x2": stable},
            {"0x1": after, "0x2": dict(stable)},
            {"0x1": target},
        )
        self.assertEqual(result["nonTargetsByteIdentical"], 1)
        self.assertEqual(result["changedTargetFields"], AUTH.EXPECTED_CHANGED_TARGET_FIELDS)

    def test_non_target_inventory_delta_is_rejected(self):
        before, after, target = self._target_rows()
        with self.assertRaisesRegex(AUTH.AuthorityError, "non-target"):
            AUTH.compare_inventory_records(
                {"0x1": before, "0x2": {"name": "before"}},
                {"0x1": after, "0x2": {"name": "after"}},
                {"0x1": target},
            )

    def test_program_comparator_accepts_only_expected_global_deltas(self):
        base = {
            "programName": "BEA.exe", "executableSHA256": AUTH.PROGRAM_SHA256,
            "functions": str(AUTH.FUNCTION_COUNT),
            "instructions": str(AUTH.INSTRUCTION_COUNT),
            "symbolsUserDefined": "6016", "symbolsDefaultOther": "61682",
            "comments": "9111", "commentsSha256": "pre",
        }
        post = dict(base)
        post.update({"symbolsUserDefined": "6070", "symbolsDefaultOther": "61628",
                     "comments": "9165", "commentsSha256": "post"})
        with tempfile.TemporaryDirectory() as raw:
            paths = [Path(raw) / name for name in ("pre.tsv", "post.tsv")]
            for path, values in zip(paths, (base, post)):
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
                    writer.writerow(("metric", "value"))
                    writer.writerows(values.items())
            result = AUTH.compare_programs(*paths)
        self.assertEqual(result["changedMetrics"], AUTH.EXPECTED_PROGRAM_CHANGES)
        self.assertEqual(result["newUserSymbols"], 54)

    def test_old_scratch_authority_is_explicitly_historical(self):
        source = Path(AUTH.__file__).read_text(encoding="utf-8")
        self.assertIn('"historicalScratchVerifierIsOneShot": True', source)
        self.assertNotIn(
            "ghidra_mission_registry_vocabulary_authority_tests",
            inspect.getsource(AUTH.build),
        )


if __name__ == "__main__":
    unittest.main()
