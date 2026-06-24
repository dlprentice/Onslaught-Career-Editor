#!/usr/bin/env python3
"""Tests for the second-host runtime-causality proof gate."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_second_host_runtime_executor_bundle as executor_builder
import winui_safe_copy_online_second_host_runtime_causality_check as causality
import winui_safe_copy_online_second_host_runtime_promotion_guard as promotion_guard


class SecondHostRuntimeCausalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        causality.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)

    def test_self_test_fixture_requires_explicit_allow_fixture_and_is_not_live(self) -> None:
        payload = causality.make_future_raw_artifact_fixture()

        with self.assertRaises(causality.SecondHostRuntimeCausalityError):
            causality.validate_causality_candidate(payload)

        summary = causality.validate_causality_candidate(payload, allow_fixture=True)

        self.assertTrue(summary["selfTestFixtureCandidate"])
        self.assertFalse(summary["runtimeDrivenBySecondHostCommandSource"])
        self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
        self.assertFalse(summary["rawArtifactReceiptsRecomputed"])
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])

    def test_file_backed_self_test_candidate_requires_allow_fixture_and_is_not_live(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(causality.read_json(candidate_path), candidate_path=candidate_path)

            summary = causality.validate_causality_candidate(
                causality.read_json(candidate_path),
                candidate_path=candidate_path,
                allow_fixture=True,
            )

        self.assertTrue(summary["selfTestFixtureCandidate"])
        self.assertFalse(summary["runtimeDrivenBySecondHostCommandSource"])
        self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
        self.assertFalse(summary["rawArtifactReceiptsRecomputed"])

    def test_rejects_json_only_file_backed_live_candidate_without_raw_bodies(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            old_run_id = payload["runId"]
            live_run_id = "second-host-runtime-causality-live-forged-0001"
            payload = causality.replace_scalar_values(payload, {old_run_id: live_run_id})
            for hash_key, receipt in payload["rawArtifactChain"]["artifactReceipts"].items():
                artifact_path = candidate_path.parent / receipt["relativePath"]
                artifact = causality.read_json(artifact_path)
                artifact = causality.replace_scalar_values(artifact, {old_run_id: live_run_id})
                artifact["secondHostRuntimeCausalityArtifact"]["selfTestOnly"] = False
                evidence = artifact["roleSpecificRawEvidence"]
                evidence["evidenceMode"] = "live-runtime-artifact"
                evidence["selfTestOnly"] = False
                evidence.pop("rawEvidenceBody", None)
                causality.write_json(artifact_path, artifact)
                new_hash = causality.sha256_file(artifact_path)
                old_hash = receipt["sha256"]
                payload = causality.replace_scalar_values(payload, {old_hash: new_hash})
                payload["rawArtifactChain"]["artifactReceipts"][hash_key]["sha256"] = new_hash
            causality.write_json(candidate_path, payload)

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(causality.read_json(candidate_path), candidate_path=candidate_path)

    def test_rejects_file_backed_candidate_outside_private_proof_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(causality.read_json(candidate_path), candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_file_backed_artifact_without_semantic_receipt(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            receipt = payload["rawArtifactChain"]["artifactReceipts"]["schedulerProofSha256"]
            artifact_path = candidate_path.parent / receipt["relativePath"]
            artifact_path.write_text('{"artifactRole":"schedulerProofSha256","selfTestOnly":true}\n', encoding="utf-8")
            new_hash = causality.sha256_file(artifact_path)
            receipt["sha256"] = new_hash
            payload["rawArtifactChain"]["schedulerProofSha256"] = new_hash
            payload["sourceBoundRuntimeCausalityReceipt"]["schedulerReceipt"]["artifactSha256"] = new_hash
            causality.write_json(candidate_path, payload)

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(causality.read_json(candidate_path), candidate_path=candidate_path)

    def test_rejects_file_backed_artifact_with_envelope_only_receipt(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            receipt = payload["rawArtifactChain"]["artifactReceipts"]["schedulerProofSha256"]
            artifact_path = candidate_path.parent / receipt["relativePath"]
            artifact = causality.read_json(artifact_path)
            artifact.pop("roleSpecificRawEvidence", None)
            causality.write_json(artifact_path, artifact)
            new_hash = causality.sha256_file(artifact_path)
            receipt["sha256"] = new_hash
            payload["rawArtifactChain"]["schedulerProofSha256"] = new_hash
            payload["sourceBoundRuntimeCausalityReceipt"]["schedulerReceipt"]["artifactSha256"] = new_hash
            causality.write_json(candidate_path, payload)

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(causality.read_json(candidate_path), candidate_path=candidate_path)

    def mutate_raw_artifact_body(
        self,
        candidate_path: Path,
        payload: dict[str, object],
        hash_key: str,
        updates: dict[str, object],
    ) -> dict[str, object]:
        receipt = payload["rawArtifactChain"]["artifactReceipts"][hash_key]  # type: ignore[index]
        artifact_path = candidate_path.parent / receipt["relativePath"]  # type: ignore[index]
        artifact = causality.read_json(artifact_path)
        artifact["roleSpecificRawEvidence"]["rawEvidenceBody"].update(updates)
        causality.write_json(artifact_path, artifact)
        old_hash = receipt["sha256"]  # type: ignore[index]
        new_hash = causality.sha256_file(artifact_path)
        payload = causality.replace_scalar_values(payload, {old_hash: new_hash})
        payload["rawArtifactChain"]["artifactReceipts"][hash_key]["sha256"] = new_hash  # type: ignore[index]
        payload["rawArtifactChain"][hash_key] = new_hash  # type: ignore[index]
        return payload

    def test_rejects_runtime_input_window_raw_body_direct_client_input_bypass(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {
                    "hostHelperInputBoundToSecondHostCommandSource": True,
                    "gameInputSentBySecondHostClient": True,
                },
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_exact_pid_cdb_raw_body_without_host_helper_binding(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "exactPidCdbLogSha256",
                {
                    "hostHelperInputBoundToSecondHostCommandSource": False,
                    "gameInputSentBySecondHostClient": False,
                },
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_runtime_input_window_raw_body_wrong_host_helper_mapped_p2_sequence(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {"hostHelperMappedInputSequence": "down:Q,wait:500,up:Q"},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_exact_pid_cdb_raw_body_wrong_host_helper_route(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "exactPidCdbLogSha256",
                {"hostHelperRuntimeRoute": "P1/inputDevice0/top-split-half"},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_raw_body_missing_material_descriptor(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {"rawEvidenceMaterialKind": None},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_raw_body_material_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "exactPidCdbLogSha256",
                {"rawEvidenceMaterialUnitCount": 1},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_raw_body_without_recomputed_raw_evidence_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {"rawEvidenceRelativePath": None},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_raw_body_raw_evidence_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "exactPidCdbLogSha256",
                {"rawEvidenceSha256": "9" * 64},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_hidden_raw_body_host_join_overclaim(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {"hostJoinControlsMayBeEnabled": True},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_hidden_raw_body_host_join_string_overclaim(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {"hostJoinControlsMayBeEnabled": "true"},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_sensitive_raw_body_key(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            sensitive_key = "C:" + "\\Users" + "\\david" + "\\secret-path"
            payload = self.mutate_raw_artifact_body(
                candidate_path,
                payload,
                "runtimeInputWindowArtifactSha256",
                {sensitive_key: "redacted"},
            )

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_top_level_host_join_overclaim(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["hostJoinControlsMayBeEnabled"] = True

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_outside_private_root_error_does_not_disclose_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))

            with self.assertRaises(causality.SecondHostRuntimeCausalityError) as caught:
                causality.validate_causality_candidate(causality.read_json(candidate_path), candidate_path=candidate_path, allow_fixture=True)

        message = str(caught.exception).lower()
        self.assertNotIn(str(causality.PRIVATE_PROOF_ROOT).lower(), message)
        self.assertNotIn("c:\\", message)
        self.assertNotIn("users\\", message)

    def test_rejects_current_compatibility_executor_fixture(self) -> None:
        with tempfile.TemporaryDirectory(dir=executor_builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            payload = promotion_guard.make_current_compatibility_executor_fixture(Path(raw_tmp))

        with self.assertRaises(causality.SecondHostRuntimeCausalityError):
            causality.validate_causality_candidate(payload)

    def test_rejects_shape_only_promotion_fixture(self) -> None:
        payload = promotion_guard.make_future_candidate_fixture()

        with self.assertRaises(causality.SecondHostRuntimeCausalityError):
            causality.validate_causality_candidate(payload)

    def test_rejects_swapped_bridge_artifact_hash(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["rawArtifactChain"]["bridgeProofSha256"] = "1" * 64

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_mismatched_pid_between_runtime_and_cdb_receipts(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["rawArtifactChain"]["exactPidCdb"]["observedProcessIdentitySha256"] = "2" * 64

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path)

    def test_rejects_stale_run_id_in_runtime_input_window(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["sourceBoundRuntimeCausalityReceipt"]["runtimeInputWindowReceipt"]["runId"] = "different-run"

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path)

    def test_rejects_mapped_p2_sequence_receipt_wrong_artifact_hash(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["sourceBoundRuntimeCausalityReceipt"]["mappedP2SequenceReceipt"]["artifactSha256"] = payload[
                "rawArtifactChain"
            ]["bridgeProofSha256"]

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_host_helper_delivery_receipt_stale_run_id(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["sourceBoundRuntimeCausalityReceipt"]["hostHelperDeliveryReceipt"]["runId"] = "different-run"

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)

    def test_rejects_fixture_or_operator_source_safety(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["sourceSafety"]["evidenceMode"] = "self-test-fixture"

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path)

    def test_rejects_unknown_source_hash_mode(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["sourceSafety"]["host"]["copiedProfileHashMode"] = "nonsense"

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path)

    def test_rejects_host_join_overclaim(self) -> None:
        with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = causality.write_file_backed_self_test_candidate(Path(tmp))
            payload = causality.read_json(candidate_path)
            payload["nonClaims"]["hostJoinControlsMayBeEnabled"] = True

            with self.assertRaises(causality.SecondHostRuntimeCausalityError):
                causality.validate_causality_candidate(payload, candidate_path=candidate_path)

    def test_rejects_missing_contract_requirement_and_nonclaim_keys(self) -> None:
        for section, key in (
            ("livePromotionRequirements", "requiresExactPidCdbRuntimeInputEvidence"),
            ("livePromotionRequirements", "requiresRoleSpecificRawEvidenceMaterialDescriptors"),
            ("currentEvidence", "runtimeDrivenBySecondHostCommandSource"),
            ("nonClaims", "nativeBeaNetcodeProof"),
        ):
            payload = causality.make_contract_fixture()
            del payload[section][key]

            with self.assertRaises(causality.SecondHostRuntimeCausalityError, msg=f"{section}.{key}"):
                causality.validate_contract(payload)

    def test_fixture_is_fresh_copy(self) -> None:
        first = causality.make_future_raw_artifact_fixture()
        second = causality.make_future_raw_artifact_fixture()
        first["rawArtifactChain"]["runId"] = "mutated"

        self.assertNotEqual(first["rawArtifactChain"]["runId"], second["rawArtifactChain"]["runId"])
        self.assertEqual(second, copy.deepcopy(second))


if __name__ == "__main__":
    unittest.main()
