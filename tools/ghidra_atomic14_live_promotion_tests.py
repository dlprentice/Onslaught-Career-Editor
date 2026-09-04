#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-Ghidra counterexamples for the one-shot Atomic14 live owner."""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
OWNER_PATH = TOOLS / "ghidra_atomic14_live_promotion.py"
SPEC = importlib.util.spec_from_file_location("atomic14_live_owner", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class Atomic14LivePromotionTests(unittest.TestCase):
    def test_tracked_cli_refuses_retired_historical_topology(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = owner.main(["verify"])
        self.assertEqual(1, result)
        payload = json.loads(output.getvalue())
        self.assertEqual("REFUSED", payload["status"])
        self.assertIn("completed Windows-era one-shot", payload["error"])
        self.assertIn("never substitute the active mutable", payload["error"])

    def test_direct_preflight_is_also_fail_closed(self) -> None:
        with self.assertRaisesRegex(owner.PromotionError, "package catalog"):
            owner.preflight()

    def test_retired_owner_does_not_load_historical_executable_dependencies(self) -> None:
        source = OWNER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("import ghidra_global_init515_live_promotion", source)
        self.assertNotIn('spec_from_file_location("atomic14_formal"', source)
        self.assertNotIn("copies remain sealed beside", source)
        self.assertIn(owner.FROZEN_GIT_COMMIT, source)

    def test_git_recovery_matches_ready_owner_and_full_tracked_closure(self) -> None:
        result = owner.verify_frozen_git_recovery()
        self.assertEqual("VERIFIED_GIT_SOURCE_RECOVERY", result["status"])
        self.assertEqual(owner.FROZEN_GIT_COMMIT, result["commit"])
        self.assertEqual(len(owner.FROZEN_GIT_BLOBS), result["trackedBlobCount"])
        self.assertEqual(
            owner.FROZEN_GIT_BLOBS[owner.FROZEN_OWNER_RELATIVE][1],
            result["ownerSha256"],
        )
        self.assertEqual(
            owner.FROZEN_GIT_BLOBS[owner.FROZEN_OWNER_RELATIVE][0],
            result["receiptOwnerStamp"]["bytes"],
        )
        self.assertIn("machine-local replay inputs", result["claimBoundary"])

    def test_git_recovery_dependency_closure_rejects_missing_or_extra_pins(self) -> None:
        source = owner.frozen_git_blob(owner.FROZEN_OWNER_RELATIVE).decode("utf-8")
        missing = source.replace(
            owner.FROZEN_GIT_BLOBS["tools/ghidra_function_batch_proof.py"][1],
            "0" * 64,
            1,
        )
        with self.assertRaisesRegex(owner.PromotionError, "hashes differ"):
            owner.verify_frozen_owner_dependency_closure(missing)

        extra = (
            source
            + '\nEXTRA_TOOL = TOOLS / "unexpected_dependency.py"\n'
            + f'EXTRA_TOOL_SHA256 = "{"0" * 64}"\n'
        )
        with self.assertRaisesRegex(owner.PromotionError, "paths differ"):
            owner.verify_frozen_owner_dependency_closure(extra)

    def test_git_recovery_cli_is_read_only_and_reports_claim_boundary(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = owner.main(["verify-git-recovery"])
        self.assertEqual(0, result)
        payload = json.loads(output.getvalue())
        self.assertEqual("VERIFIED_GIT_SOURCE_RECOVERY", payload["status"])
        self.assertIn("Git recovers", payload["claimBoundary"])

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
        self.skipTest("historical executable dependencies are intentionally not loaded")
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
        self.skipTest("historical executable dependencies are intentionally not loaded")
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

    def test_promote_refuses_before_creating_an_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owner"
            with self.assertRaisesRegex(owner.PromotionError, "package catalog"):
                owner.promote(root)
            self.assertFalse(root.exists())

    def test_verify_is_retired_before_reading_owner_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owner"
            with self.assertRaisesRegex(owner.PromotionError, "package catalog"):
                owner.verify_artifacts(root)
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
