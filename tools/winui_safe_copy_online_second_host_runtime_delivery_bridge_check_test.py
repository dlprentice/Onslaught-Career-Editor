#!/usr/bin/env python3
"""Regression tests for the second-host runtime-delivery bridge checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_second_host_command_source_bundle as command_builder
import build_winui_original_binary_second_host_runtime_delivery_bridge_bundle as builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_second_host_runtime_delivery_bridge_check as bridge_check


class SecondHostRuntimeDeliveryBridgeTests(unittest.TestCase):
    def build_matching_second_host_fixture(self, root: Path, executor_path: Path) -> Path:
        executor_payload = executor_check.read_json(executor_path)
        host_path = executor_check.resolve_path(executor_path, str(executor_payload["hostAuthorityTwoClientProofBundle"]))
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
        executor_path = executor_check.make_executor_fixture(root / "executor-source")
        second_path = self.build_matching_second_host_fixture(root, executor_path)
        output_path = root / "bridge" / "second-host-runtime-delivery-bridge-proof.json"
        builder.build_bundle(second_path, executor_path, output_path, allow_fixture_executor=True)
        return output_path

    def test_fixture_bridge_validates(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            summary = bridge_check.validate_bundle(output_path, allow_fixture=True)
            self.assertTrue(summary["secondHostRuntimeDeliveryBridgeProven"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
            self.assertFalse(summary["runtimeDrivenBySecondHostCommandSource"])

    def test_runtime_driven_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = bridge_check.read_json(output_path)
            payload["runtimeEvidence"]["runtimeDrivenBySecondHostCommandSource"] = True
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaises(bridge_check.SecondHostRuntimeDeliveryBridgeError):
                bridge_check.validate_bundle(output_path, allow_fixture=True)

    def test_accepted_live_runtime_delivery_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = bridge_check.read_json(output_path)
            payload["runtimeEvidence"]["acceptedLiveSecondHostRuntimeDeliveryProof"] = True
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(bridge_check.SecondHostRuntimeDeliveryBridgeError):
                bridge_check.validate_bundle(output_path, allow_fixture=True)

    def test_upstream_private_lan_hash_binding_is_recomputed(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = bridge_check.read_json(output_path)
            payload["secondHostRuntimeDeliveryBridge"]["hostAuthorityPrivateRemoteClientUpstreamPrivateLanProofSha256"] = "0" * 64
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(bridge_check.SecondHostRuntimeDeliveryBridgeError):
                bridge_check.validate_bundle(output_path, allow_fixture=True)

    def test_base_online_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = bridge_check.read_json(output_path)
            payload["nonClaims"]["baseOnlineMultiplayerReady"] = True
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaises(bridge_check.SecondHostRuntimeDeliveryBridgeError):
                bridge_check.validate_bundle(output_path, allow_fixture=True)

    def test_absolute_artifact_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = bridge_check.read_json(output_path)
            payload["sourceArtifacts"]["secondHostCommandSourceProof"] = str(output_path.resolve())
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaises(bridge_check.SecondHostRuntimeDeliveryBridgeError):
                bridge_check.validate_bundle(output_path, allow_fixture=True)

    def test_sensitive_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            output_path = self.build_fixture(Path(raw_tmp))
            payload = bridge_check.read_json(output_path)
            payload["releaseBoundary"]["credentialHex"] = "00"
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaises(bridge_check.SecondHostRuntimeDeliveryBridgeError):
                bridge_check.validate_bundle(output_path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()
