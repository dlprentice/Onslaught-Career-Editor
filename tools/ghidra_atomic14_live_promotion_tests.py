#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-Ghidra counterexamples for the one-shot Atomic14 live owner."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parent
OWNER_PATH = TOOLS / "ghidra_atomic14_live_promotion.py"
SPEC = importlib.util.spec_from_file_location("atomic14_live_owner", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class Atomic14LivePromotionTests(unittest.TestCase):
    def test_formal_author_is_hashed_before_its_module_is_executed(self) -> None:
        source = OWNER_PATH.read_text(encoding="utf-8")
        check = source.index('exact_file(FORMAL_AUTHOR, FORMAL_AUTHOR_SHA256, "formal verifier")')
        execute = source.index('importlib.util.spec_from_file_location("atomic14_formal"')
        self.assertLess(check, execute)

    def test_full_result_gate_precedes_ready_publication(self) -> None:
        source = OWNER_PATH.read_text(encoding="utf-8")
        in_memory_gate = source.index("validate_promotion_payload(result, owner_root)")
        result_freeze = source.index("write_json_new(result_path, result)")
        frozen_gate = source.index("validate_promotion_payload(frozen_result, owner_root)")
        ready_publish = source.index("write_json_new(ready_path, ready_payload)")
        self.assertLess(in_memory_gate, result_freeze)
        self.assertLess(result_freeze, frozen_gate)
        self.assertLess(frozen_gate, ready_publish)

    def test_inventory_classifier_accepts_only_exact_pre_or_post_pairs(self) -> None:
        receipt = owner.formal_receipt()
        post = receipt["replicas"][0]["post"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pre_functions = root / "pre-functions.tsv"
            pre_program = root / "pre-program.tsv"
            post_functions = root / "post-functions.tsv"
            post_program = root / "post-program.tsv"
            shutil.copy2(owner.formal.BASE_FUNCTIONS, pre_functions)
            shutil.copy2(owner.formal.BASE_PROGRAM, pre_program)
            shutil.copy2(owner.REPO / post["functions"]["path"], post_functions)
            shutil.copy2(owner.REPO / post["program"]["path"], post_program)

            pre = {
                "functions": owner.relative_stamp(pre_functions, root),
                "program": owner.relative_stamp(pre_program, root),
            }
            exact_post = {
                "functions": owner.relative_stamp(post_functions, root),
                "program": owner.relative_stamp(post_program, root),
            }
            mixed = {
                "functions": pre["functions"],
                "program": exact_post["program"],
            }
            self.assertEqual(owner.classify_inventory(pre, root, "pre"), owner.ProjectState.PRE)
            self.assertEqual(
                owner.classify_inventory(exact_post, root, "post"), owner.ProjectState.POST
            )
            self.assertEqual(
                owner.classify_inventory(mixed, root, "mixed"), owner.ProjectState.UNKNOWN
            )

    def _write_run(self, root: Path, relative: str, command: str) -> None:
        path = root / relative / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"argv": [command]}), encoding="utf-8")

    def test_mutation_census_requires_exactly_one_promotion_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_run(
                root,
                "promotion/runs/live-apply",
                "analyzeHeadless.bat BEA -postScript RepairAndCreateConsoleCallbacks.java apply",
            )
            owner.validate_mutation_census(root)

    def test_mutation_census_does_not_mistake_readonly_path_text_for_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_run(
                root,
                "promotion/runs/live-apply",
                "analyzeHeadless.bat C:/artifact-readOnly-name BEA "
                "-postScript RepairAndCreateConsoleCallbacks.java apply",
            )
            owner.validate_mutation_census(root)

    def test_mutation_census_rejects_prepare_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_run(
                root,
                "runs/prepare-apply",
                "analyzeHeadless.bat BEA -postScript RepairAndCreateConsoleCallbacks.java apply",
            )
            self._write_run(
                root,
                "promotion/runs/live-apply",
                "analyzeHeadless.bat BEA -postScript RepairAndCreateConsoleCallbacks.java apply",
            )
            with self.assertRaisesRegex(owner.PromotionError, "preparation contains"):
                owner.validate_mutation_census(root)

    def test_mutation_census_rejects_second_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index in range(2):
                self._write_run(
                    root,
                    f"promotion/runs/live-apply-{index}",
                    "analyzeHeadless.bat BEA -postScript RepairAndCreateConsoleCallbacks.java apply",
                )
            with self.assertRaisesRegex(owner.PromotionError, "differs from one"):
                owner.validate_mutation_census(root)

    def test_mutation_census_rejects_unexpected_mutator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_run(
                root,
                "promotion/runs/live-apply",
                "analyzeHeadless.bat BEA -postScript OtherMutator.java apply",
            )
            with self.assertRaisesRegex(owner.PromotionError, "unexpected mutating"):
                owner.validate_mutation_census(root)

    def test_mutation_census_ignores_read_only_ghidra(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_run(
                root,
                "runs/pre-observation",
                "analyzeHeadless.bat BEA -readOnly -postScript ExportFullFunctionInventory.java",
            )
            with self.assertRaisesRegex(owner.PromotionError, "differs from one"):
                owner.validate_mutation_census(root)

    def test_apply_validator_accepts_formal_artifacts_and_rejects_tamper(self) -> None:
        replica = owner.formal_receipt()["replicas"][0]
        source_output = owner.REPO / replica["apply"]["output"]["path"]
        source_ready = owner.REPO / replica["apply"]["ready"]["path"]
        source_log = owner.REPO / replica["apply"]["log"]["path"]
        process = {"status": "COMPLETED", "exitCode": 0, "readerError": ""}
        text = source_log.read_text(encoding="utf-8")
        execution, reasons = owner.validate_apply(
            process, text, source_output, source_ready, source_log
        )
        self.assertEqual(reasons, [])
        self.assertTrue(execution["semanticSuccessMarkerPresent"])

        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "atomic14.tsv"
            shutil.copy2(source_output, tampered)
            tampered.write_bytes(tampered.read_bytes() + b"tamper")
            _, reasons = owner.validate_apply(
                process, text, tampered, source_ready, source_log
            )
            self.assertTrue(reasons)

    def test_promote_publishes_intent_before_spawn_and_then_forbids_retry(self) -> None:
        snapshot = {
            "root": "fixture",
            "fileCount": 1,
            "totalBytes": 1,
            "fileSetSha256": "a" * 64,
            "files": [{"path": "BEA.gpr", "bytes": 1, "sha256": "b" * 64}],
        }

        @contextmanager
        def lease():
            yield SimpleNamespace(name=owner.MUTEX_NAME, abandoned=False)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owner"
            root.mkdir()
            (root / "prepared.ready.json").write_text("{}", encoding="utf-8")
            prepared = {
                "livePreimage": snapshot,
                "preBackup": {"backupRoot": "backup", "restoreRoot": "restore"},
            }
            pre_observation = {"rawAfter": snapshot}

            def fail_after_intent(*args, **kwargs):
                self.assertTrue((root / "promotion/attempt.started.json").is_file())
                raise owner.PromotionError("injected spawn failure")

            with (
                patch.object(owner.guard, "acquire_mutex", side_effect=lambda: lease()),
                patch.object(owner.guard, "assert_quiescent", return_value={}),
                patch.object(owner.guard, "project_snapshot", return_value=snapshot),
                patch.object(owner, "load_prepared", return_value=prepared),
                patch.object(owner, "environment_for", return_value=({}, root)),
                patch.object(owner, "run_formal_verifier", return_value={}),
                patch.object(owner, "observe_pre", return_value=pre_observation),
                patch.object(owner, "atomic_argv", return_value=["fixed-mutator"]),
                patch.object(owner, "run_process", side_effect=fail_after_intent),
            ):
                with self.assertRaisesRegex(owner.PromotionError, "injected spawn failure"):
                    owner.promote(root)

            self.assertTrue((root / "promotion/attempt.started.json").is_file())
            self.assertFalse((root / "promotion/promotion.ready.json").exists())
            with self.assertRaisesRegex(owner.PromotionError, "attempt already exists"):
                owner.promote(root)

    def test_verify_refuses_attempted_state_without_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owner"
            attempt = root / "promotion/attempt.started.json"
            attempt.parent.mkdir(parents=True)
            attempt.write_text("{}", encoding="utf-8")
            with patch.object(
                owner, "load_prepared", return_value={"preparedAtUtc": "fixture"}
            ):
                with self.assertRaisesRegex(owner.PromotionError, "use recover-status"):
                    owner.verify_artifacts(root)


if __name__ == "__main__":
    unittest.main()
