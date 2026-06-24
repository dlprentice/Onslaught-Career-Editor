#!/usr/bin/env python3
"""Regression tests for second-host runtime executor proof validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_second_host_command_source_bundle as command_builder
import build_winui_original_binary_second_host_runtime_executor_bundle as builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_second_host_command_source_check as second_check
import winui_safe_copy_online_second_host_runtime_executor_check as checker


class SecondHostRuntimeExecutorTests(unittest.TestCase):
    def build_matching_second_host_fixture(self, root: Path, host_path: Path) -> Path:
        host_payload = executor_check.delivery.host.read_json(host_path)
        remote_path = executor_check.delivery.host.resolve_artifact_path(host_path, str(host_payload["privateRemoteClientProofBundle"]))
        remote_payload = executor_check.delivery.host.read_json(remote_path)
        private_lan_path = executor_check.delivery.resolve_path(remote_path, str(remote_payload["privateLanTransportProofBundle"]))
        output_path = root / "second-host-command-source-proof.json"
        credential = bytes.fromhex("12" * 32)
        auth = command_builder.make_authorization(credential, command_builder.lan.sha256_file(private_lan_path), "c" * 64)
        source_safety = command_builder.make_source_safety(
            host_copied_profile_sha256="3" * 64,
            host_installed_game_sha256="4" * 64,
            client_copied_profile_sha256="5" * 64,
            client_installed_game_sha256="6" * 64,
        )
        command_builder.make_bundle_from_observation(
            private_lan_proof_path=private_lan_path,
            output_path=output_path,
            command_source_kind="distinct-vm-private-lan-labeled-vm-only",
            host_bind_address=command_builder.checker.FIXTURE_HOST_ADDRESS,
            host_assigned_addresses=[command_builder.checker.FIXTURE_HOST_ADDRESS],
            host_machine_fingerprint="1" * 64,
            client_source_address=command_builder.checker.FIXTURE_CLIENT_ADDRESS,
            client_assigned_address=command_builder.checker.FIXTURE_CLIENT_ADDRESS,
            client_machine_fingerprint="2" * 64,
            client_identity_fingerprint="c" * 64,
            authorization=auth,
            source_safety=source_safety,
            transcript_events=[
                command_builder.make_event(kind, {"kind": kind})
                for kind in command_builder.checker.EXPECTED_TRANSCRIPT_EVENTS
            ],
        )
        return output_path

    def build_fixture(self, root: Path) -> Path:
        host_path = executor_check.delivery.host.make_bundle_fixture(root / "host-authority")
        second_path = self.build_matching_second_host_fixture(root, host_path)
        output_path = root / "executor" / "second-host-runtime-executor-proof.json"
        builder.build_bundle(
            second_path,
            host_path,
            output_path,
            artifact_root=root / "runtime",
            allow_fixture_executor=True,
        )
        return output_path

    def make_live_hardening_payload(self) -> dict:
        hardening = {
            "evidenceMode": "live-server-client-transcript",
            "liveNegativeCaseTranscript": True,
            "requiredBeforeAcceptedLiveRuntimeDelivery": True,
        }
        for flag in second_check.REQUIRED_SESSION_SECURITY_HARDENING_FLAGS:
            hardening[flag] = True
        return {"sessionSecurityHardening": hardening}

    def make_computed_source_safety(self, root: Path) -> dict:
        roots: dict[str, Path] = {}
        for name in ("host-copied", "host-installed", "client-copied", "client-installed"):
            roots[name] = root / name
            roots[name].mkdir(parents=True, exist_ok=True)
            (roots[name] / "sentinel.bin").write_text(name, encoding="utf-8")
        host_evidence = command_builder.make_source_safety_side_evidence(
            role="host",
            copied_profile_root=roots["host-copied"],
            installed_game_root=roots["host-installed"],
        )
        client_evidence = command_builder.make_source_safety_side_evidence(
            role="client",
            copied_profile_root=roots["client-copied"],
            installed_game_root=roots["client-installed"],
        )
        return command_builder.make_source_safety(
            host_copied_profile_sha256="0" * 64,
            host_installed_game_sha256="1" * 64,
            client_copied_profile_sha256="2" * 64,
            client_installed_game_sha256="3" * 64,
            host_evidence=host_evidence,
            client_evidence=client_evidence,
        )

    def test_runtime_hardening_flags_follow_command_source_contract(self) -> None:
        self.assertEqual(
            builder.REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS,
            second_check.REQUIRED_SESSION_SECURITY_HARDENING_FLAGS,
        )
        self.assertEqual(
            checker.REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS,
            second_check.REQUIRED_SESSION_SECURITY_HARDENING_FLAGS,
        )

        for flag in ("preSessionCommandLiveRejected", "directInputBypassLiveRejected"):
            with self.subTest(flag=flag, guard="builder"):
                payload = self.make_live_hardening_payload()
                del payload["sessionSecurityHardening"][flag]
                with self.assertRaises(builder.SecondHostRuntimeExecutorBuildError):
                    builder.require_second_host_security_hardening(payload)
            with self.subTest(flag=flag, guard="checker"):
                payload = self.make_live_hardening_payload()
                del payload["sessionSecurityHardening"][flag]
                with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                    checker.require_second_host_security_hardening(payload)

    def test_live_runtime_requires_computed_source_safety_preflight(self) -> None:
        payload = self.make_live_hardening_payload()
        payload["sourceSafety"] = command_builder.make_source_safety(
            host_copied_profile_sha256="3" * 64,
            host_installed_game_sha256="4" * 64,
            client_copied_profile_sha256="5" * 64,
            client_installed_game_sha256="6" * 64,
        )
        with self.assertRaises(builder.SecondHostRuntimeExecutorBuildError):
            builder.require_live_source_safety_preflight(payload)
        with self.assertRaises(checker.SecondHostRuntimeExecutorError):
            checker.require_live_source_safety_preflight(payload)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            payload = self.make_live_hardening_payload()
            payload["sourceSafety"] = self.make_computed_source_safety(Path(raw_tmp))
            self.assertEqual(payload["sourceSafety"]["evidenceMode"], "local-preflight-computed")
            builder.require_live_source_safety_preflight(payload)
            checker.require_live_source_safety_preflight(payload)

            payload["sourceSafety"]["client"]["copiedProfileFileCount"] = 0
            with self.assertRaises(builder.SecondHostRuntimeExecutorBuildError):
                builder.require_live_source_safety_preflight(payload)
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.require_live_source_safety_preflight(payload)

    def test_fixture_executor_validates_only_with_fixture_flag(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            summary = checker.validate_bundle(output_path, allow_fixture=True)
            self.assertTrue(summary["secondHostRuntimeExecutorProofBuilt"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
            self.assertFalse(summary["runtimeDrivenBySecondHostCommandSource"])
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path)

    def test_base_online_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["nonClaims"]["baseOnlineMultiplayerReady"] = True
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_host_join_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["nonClaims"]["hostJoinControlsMayBeEnabled"] = True
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_source_binding_is_recomputed_by_checker(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["acceptedSecondHostCommandPayloadSha256"] = "0" * 64
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["sessionCompatibilityKeyMatch"] = not payload["sourceBinding"]["sessionCompatibilityKeyMatch"]
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["acceptedSecondHostCommandRequestPayloadSha256"] = "0" * 64
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["hostAuthorityPrivateRemoteClientUpstreamPrivateLanProofSha256"] = "0" * 64
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["secondHostInvitationLifecycleSha256"] = "0" * 64
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["secondHostInvitationLifecyclePostDeleteAbsent"] = False
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["sourceBinding"]["hostAuthorityAcceptedP2MappedInputSequence"] = "down:Q,wait:500,up:Q"
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["secondHostRuntimeExecutor"]["runtimeDrivenBySecondHostCommandSource"] = True
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["secondHostRuntimeExecutor"]["acceptedLiveSecondHostRuntimeDeliveryProof"] = True
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_runtime_evidence_requires_host_helper_receipt_bound_to_mapped_p2_sequence(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["runtimeEvidence"]["hostHelperInputBoundToSecondHostCommandSource"] = False
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["runtimeEvidence"]["hostHelperMappedInputSequence"] = "down:Q,wait:500,up:Q"
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["runtimeEvidence"]["hostHelperRuntimeRoute"] = "P1/inputDevice0/top-split-half"
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_bridge_proof_must_belong_to_same_executor_bundle(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            root = Path(raw_tmp)
            output_path = self.build_fixture(root / "first")
            other_output_path = self.build_fixture(root / "second")
            payload = checker.read_json(output_path)
            other_payload = checker.read_json(other_output_path)
            payload["sourceArtifacts"]["bridgeProof"] = other_payload["sourceArtifacts"]["bridgeProof"]
            payload["sourceArtifacts"]["bridgeProofSha256"] = other_payload["sourceArtifacts"]["bridgeProofSha256"]
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_sensitive_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = checker.read_json(output_path)
            payload["releaseBoundary"]["credentialHex"] = "00"
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(checker.SecondHostRuntimeExecutorError):
                checker.validate_bundle(output_path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()
