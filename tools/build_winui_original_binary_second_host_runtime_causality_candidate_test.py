#!/usr/bin/env python3
"""Tests for the second-host runtime-causality candidate materializer."""

from __future__ import annotations

import tempfile
import unittest
import json
import subprocess
import sys
from pathlib import Path

import build_winui_original_binary_second_host_runtime_causality_candidate as builder
import winui_safe_copy_online_second_host_runtime_causality_check as causality
import winui_safe_copy_online_second_host_runtime_executor_check_test as executor_test


class SecondHostRuntimeCausalityCandidateBuilderTests(unittest.TestCase):
    def test_file_backed_self_test_candidate_is_checker_accepted_only_as_fixture(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = Path(raw_tmp) / "second-host-runtime-causality-candidate.json"

            summary = builder.build_file_backed_self_test_candidate(output_path)

            self.assertEqual(summary["artifact"], output_path.relative_to(causality.PRIVATE_PROOF_ROOT).as_posix())
            self.assertTrue(summary["selfTestFixtureCandidate"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
            self.assertFalse(summary["hostJoinControlsMayBeEnabled"])

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(causality.read_json(output_path), candidate_path=output_path)

    def test_current_compatibility_executor_is_rejected_without_writing_candidate(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            executor_path = executor_test.SecondHostRuntimeExecutorTests().build_fixture(root / "executor-source")
            output_path = root / "candidate" / "second-host-runtime-causality-candidate.json"

            with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError) as caught:
                builder.build_candidate_from_runtime_executor(executor_path, output_path, allow_fixture_executor=True)

            self.assertIn("host-authority-derived compatibility executor", str(caught.exception))
            self.assertFalse(output_path.exists())

    def test_truthy_edited_executor_is_rejected_without_writing_candidate(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            executor_path = executor_test.SecondHostRuntimeExecutorTests().build_fixture(root / "executor-source")
            payload = json.loads(executor_path.read_text(encoding="utf-8-sig"))
            payload["secondHostRuntimeExecutor"]["runtimeInputDerivedFromSecondHostCommandSource"] = True
            payload["secondHostRuntimeExecutor"]["runtimeDrivenBySecondHostCommandSource"] = True
            payload["secondHostRuntimeExecutor"]["acceptedLiveSecondHostRuntimeDeliveryProof"] = True
            executor_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            output_path = root / "candidate" / "second-host-runtime-causality-candidate.json"

            with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError) as caught:
                builder.build_candidate_from_runtime_executor(executor_path, output_path, allow_fixture_executor=True)

            self.assertIn("runtime executor proof rejected", str(caught.exception))
            self.assertFalse(output_path.exists())

    def test_raw_material_plan_lists_required_roles_without_enabling_host_join(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = Path(raw_tmp) / "raw-material-plan.json"

            summary = builder.build_raw_material_plan(output_path)

            self.assertEqual(summary["schemaVersion"], builder.RAW_MATERIAL_PLAN_SCHEMA)
            self.assertEqual(summary["requiredRoleCount"], len(causality.CHAIN_HASH_KEYS))
            self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeCausalityProof"])
            self.assertFalse(summary["privateProofRootPublished"])

            payload = json.loads(output_path.read_text(encoding="utf-8-sig"))
            role_hash_keys = {role["hashKey"] for role in payload["requiredRawMaterialRoles"]}
            self.assertEqual(role_hash_keys, set(causality.CHAIN_HASH_KEYS))
            self.assertIn("runtimeInputWindowArtifactSha256", role_hash_keys)
            self.assertIn("exactPidCdbLogSha256", role_hash_keys)
            self.assertNotIn(str(causality.PRIVATE_PROOF_ROOT), output_path.read_text(encoding="utf-8-sig"))

    def test_raw_material_plan_validator_rejects_missing_role_or_host_join_overclaim(self) -> None:
        plan = builder.make_raw_material_plan()
        plan["requiredRawMaterialRoles"] = plan["requiredRawMaterialRoles"][:-1]

        with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
            builder.validate_raw_material_plan(plan)

        plan = builder.make_raw_material_plan()
        plan["nonClaims"]["hostJoinControlsMayBeEnabled"] = True

        with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
            builder.validate_raw_material_plan(plan)

    def test_raw_material_plan_validator_rejects_stale_modes_and_extra_truthy_claims(self) -> None:
        plan = builder.make_raw_material_plan()
        plan["artifactReferenceMode"] = "fixture-path"

        with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
            builder.validate_raw_material_plan(plan)

        plan = builder.make_raw_material_plan()
        plan["requiredRawMaterialRoles"][0]["requiredEvidenceMode"] = "self-test-file-backed-artifact"

        with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
            builder.validate_raw_material_plan(plan)

        plan = builder.make_raw_material_plan()
        plan["acceptedLiveSecondHostRuntimeDeliveryProof"] = True

        with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
            builder.validate_raw_material_plan(plan)

        plan = builder.make_raw_material_plan()
        plan["releaseBoundary"]["acceptedLiveSecondHostRuntimeDeliveryProof"] = True

        with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
            builder.validate_raw_material_plan(plan)

    def test_raw_material_plan_rejects_candidate_named_output(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = Path(raw_tmp) / builder.DEFAULT_OUTPUT.name

            with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
                builder.build_raw_material_plan(output_path)

            output_path = Path(raw_tmp) / builder.DEFAULT_OUTPUT.name.upper()

            with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
                builder.build_raw_material_plan(output_path)

    def test_raw_material_plan_cli_uses_plan_default_and_rejects_executor_combo(self) -> None:
        script = Path(__file__).with_name("build_winui_original_binary_second_host_runtime_causality_candidate.py")
        result = subprocess.run(
            [sys.executable, str(script), "--raw-material-plan"],
            cwd=Path(__file__).resolve().parents[1],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(result.stdout)
        self.assertTrue(summary["artifact"].endswith("/second-host-runtime-causality-raw-material-plan.json"))
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])

        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            executor_path = executor_test.SecondHostRuntimeExecutorTests().build_fixture(root / "executor-source")
            result = subprocess.run(
                [sys.executable, str(script), "--raw-material-plan", "--from-runtime-executor", str(executor_path)],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot be combined", result.stdout)

    def test_raw_material_manifest_summarizes_file_backed_candidate_without_live_claims(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            candidate_path = root / "second-host-runtime-causality-candidate.json"
            manifest_path = root / "second-host-runtime-causality-raw-material-manifest.json"
            builder.build_file_backed_self_test_candidate(candidate_path)

            summary = builder.build_raw_material_manifest_from_candidate(
                candidate_path,
                manifest_path,
                allow_fixture=True,
            )

            self.assertEqual(summary["schemaVersion"], builder.RAW_MATERIAL_MANIFEST_SCHEMA)
            self.assertEqual(summary["requiredRoleCount"], len(causality.CHAIN_HASH_KEYS))
            self.assertTrue(summary["allowFixtureMaterial"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeCausalityProof"])
            self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            role_hash_keys = {role["hashKey"] for role in payload["rawMaterialRoles"]}
            self.assertEqual(role_hash_keys, set(causality.CHAIN_HASH_KEYS))
            self.assertEqual(payload["sourceCandidateRelativePath"], candidate_path.name)
            self.assertNotIn(str(causality.PRIVATE_PROOF_ROOT), json.dumps(payload, sort_keys=True))

    def test_raw_material_manifest_requires_fixture_flag_for_self_test_candidate(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            candidate_path = root / "second-host-runtime-causality-candidate.json"
            manifest_path = root / "second-host-runtime-causality-raw-material-manifest.json"
            builder.build_file_backed_self_test_candidate(candidate_path)

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                builder.build_raw_material_manifest_from_candidate(candidate_path, manifest_path)

            self.assertFalse(manifest_path.exists())

    def test_raw_material_manifest_validator_rejects_hash_drift_and_overclaims(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            candidate_path = root / "second-host-runtime-causality-candidate.json"
            manifest_path = root / "second-host-runtime-causality-raw-material-manifest.json"
            builder.build_file_backed_self_test_candidate(candidate_path)
            builder.build_raw_material_manifest_from_candidate(candidate_path, manifest_path, allow_fixture=True)
            payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            payload["rawMaterialRoles"][0]["artifactSha256"] = "0" * 64

            with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
                builder.validate_raw_material_manifest(payload, manifest_path=manifest_path, allow_fixture=True)

            payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            payload["releaseBoundary"]["acceptedLiveSecondHostRuntimeCausalityProof"] = True

            with self.assertRaises(builder.SecondHostRuntimeCausalityCandidateBuildError):
                builder.validate_raw_material_manifest(payload, manifest_path=manifest_path, allow_fixture=True)

    def test_raw_material_manifest_cli_requires_fixture_flag_for_self_test_material(self) -> None:
        script = Path(__file__).with_name("build_winui_original_binary_second_host_runtime_causality_candidate.py")
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            candidate_path = root / "second-host-runtime-causality-candidate.json"
            manifest_path = root / "second-host-runtime-causality-raw-material-manifest.json"
            builder.build_file_backed_self_test_candidate(candidate_path)
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--raw-material-manifest-from-candidate",
                    str(candidate_path),
                    "--output",
                    str(manifest_path),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("self-test", result.stdout)
            self.assertFalse(manifest_path.exists())

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--raw-material-manifest-from-candidate",
                    str(candidate_path),
                    "--allow-fixture-raw-material",
                    "--output",
                    str(manifest_path),
                ],
                cwd=Path(__file__).resolve().parents[1],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout)
            self.assertTrue(summary["artifact"].endswith("/second-host-runtime-causality-raw-material-manifest.json"))
            self.assertTrue(summary["allowFixtureMaterial"])
            self.assertFalse(summary["hostJoinControlsMayBeEnabled"])


if __name__ == "__main__":
    unittest.main()
