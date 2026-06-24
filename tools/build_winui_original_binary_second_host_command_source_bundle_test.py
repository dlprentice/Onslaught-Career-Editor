#!/usr/bin/env python3
"""Tests for the second-host command-source proof builder."""

from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

import build_winui_original_binary_second_host_command_source_bundle as builder
import winui_safe_copy_online_private_lan_transport_smoke_check as lan
import winui_safe_copy_online_second_host_command_source_check as checker


class SecondHostCommandSourceBuilderTests(unittest.TestCase):
    def make_valid_bundle(self, root: Path) -> Path:
        private_lan = lan.make_bundle_fixture(root)
        auth = builder.make_authorization(bytes.fromhex("21" * 32), lan.sha256_file(private_lan), "c" * 64)
        safety = builder.make_source_safety(
            host_copied_profile_sha256="3" * 64,
            host_installed_game_sha256="4" * 64,
            client_copied_profile_sha256="5" * 64,
            client_installed_game_sha256="6" * 64,
        )
        output = root / "second-host-command-source-proof.json"
        builder.make_bundle_from_observation(
            private_lan_proof_path=private_lan,
            output_path=output,
            command_source_kind="distinct-vm-private-lan-labeled-vm-only",
            host_bind_address=checker.FIXTURE_HOST_ADDRESS,
            host_assigned_addresses=[checker.FIXTURE_HOST_ADDRESS],
            host_machine_fingerprint="1" * 64,
            client_source_address=checker.FIXTURE_CLIENT_ADDRESS,
            client_assigned_address=checker.FIXTURE_CLIENT_ADDRESS,
            client_machine_fingerprint="2" * 64,
            client_identity_fingerprint="c" * 64,
            authorization=auth,
            source_safety=safety,
            transcript_events=[
                builder.make_event(kind, {"kind": kind})
                for kind in checker.EXPECTED_TRANSCRIPT_EVENTS
            ],
        )
        return output

    def test_builder_output_validates_against_gate_checker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.make_valid_bundle(Path(tmp))
            summary = checker.validate_bundle(bundle)

            self.assertEqual(summary["schemaVersion"], checker.EXPECTED_SCHEMA)
            self.assertEqual(summary["acceptedCommandId"], checker.EXPECTED_COMMAND_ID)
            self.assertTrue(checker.read_json(bundle)["transport"]["samePhysicalMachineOnly"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["multiHostLanPlayProof"])
            self.assertFalse(summary["nativeBeaNetcodeProof"])
            self.assertEqual(summary["nPlayerOriginalBinaryRuntimeProof"], 0)

    def test_live_session_hardening_is_derived_from_transcript_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_lan = lan.make_bundle_fixture(root)
            auth = builder.make_authorization(bytes.fromhex("24" * 32), lan.sha256_file(private_lan), "c" * 64)
            safety = builder.make_source_safety(
                host_copied_profile_sha256="3" * 64,
                host_installed_game_sha256="4" * 64,
                client_copied_profile_sha256="5" * 64,
                client_installed_game_sha256="6" * 64,
            )
            transcript_events = [
                builder.make_event(kind, {"kind": kind})
                for kind in checker.EXPECTED_TRANSCRIPT_EVENTS
            ]
            hardening = builder.make_live_session_security_hardening(transcript_events)
            output = root / "second-host-command-source-proof.json"
            builder.make_bundle_from_observation(
                private_lan_proof_path=private_lan,
                output_path=output,
                command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                host_bind_address=checker.FIXTURE_HOST_ADDRESS,
                host_assigned_addresses=[checker.FIXTURE_HOST_ADDRESS],
                host_machine_fingerprint="1" * 64,
                client_source_address=checker.FIXTURE_CLIENT_ADDRESS,
                client_assigned_address=checker.FIXTURE_CLIENT_ADDRESS,
                client_machine_fingerprint="2" * 64,
                client_identity_fingerprint="c" * 64,
                authorization=auth,
                source_safety=safety,
                transcript_events=transcript_events,
                session_security_hardening=hardening,
            )

            payload = checker.read_json(output)
            summary = checker.validate_bundle(output)
            event_hashes = {row["kind"]: row["payloadSha256"] for row in payload["transportTranscript"]["events"]}
            accepted = payload["commands"]["accepted"][0]
            case = payload["sessionSecurityHardening"]["cases"][0]

            self.assertTrue(summary["sessionSecurityHardeningPresent"])
            self.assertEqual(summary["sessionSecurityHardeningEvidenceMode"], "live-server-client-transcript")
            self.assertEqual(accepted["requestEvent"], "client_command_p2_forward")
            self.assertEqual(accepted["requestPayloadSha256"], event_hashes["client_command_p2_forward"])
            self.assertEqual(accepted["responseEvent"], "server_command_accepted")
            self.assertEqual(accepted["responsePayloadSha256"], event_hashes["server_command_accepted"])
            self.assertEqual(case["requestPayloadSha256ByEvent"][case["requestEvents"][0]], event_hashes[case["requestEvents"][0]])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["multiHostLanPlayProof"])

    def test_builder_rejects_documentation_networks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_lan = lan.make_bundle_fixture(root)
            auth = builder.make_authorization(bytes.fromhex("22" * 32), lan.sha256_file(private_lan), "c" * 64)
            safety = builder.make_source_safety(
                host_copied_profile_sha256="3" * 64,
                host_installed_game_sha256="4" * 64,
                client_copied_profile_sha256="5" * 64,
                client_installed_game_sha256="6" * 64,
            )
            with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
                builder.make_bundle_from_observation(
                    private_lan_proof_path=private_lan,
                    output_path=root / "bad.json",
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_bind_address="192.0.2.114",
                    host_assigned_addresses=["192.0.2.114"],
                    host_machine_fingerprint="1" * 64,
                    client_source_address=checker.FIXTURE_CLIENT_ADDRESS,
                    client_assigned_address=checker.FIXTURE_CLIENT_ADDRESS,
                    client_machine_fingerprint="2" * 64,
                    client_identity_fingerprint="c" * 64,
                    authorization=auth,
                    source_safety=safety,
                    transcript_events=[builder.make_event(kind, {"kind": kind}) for kind in checker.EXPECTED_TRANSCRIPT_EVENTS],
                )

    def test_builder_rejects_same_machine_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_lan = lan.make_bundle_fixture(root)
            auth = builder.make_authorization(bytes.fromhex("23" * 32), lan.sha256_file(private_lan), "c" * 64)
            safety = builder.make_source_safety(
                host_copied_profile_sha256="3" * 64,
                host_installed_game_sha256="4" * 64,
                client_copied_profile_sha256="5" * 64,
                client_installed_game_sha256="6" * 64,
            )
            with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
                builder.make_bundle_from_observation(
                    private_lan_proof_path=private_lan,
                    output_path=root / "bad.json",
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_bind_address=checker.FIXTURE_HOST_ADDRESS,
                    host_assigned_addresses=[checker.FIXTURE_HOST_ADDRESS],
                    host_machine_fingerprint="1" * 64,
                    client_source_address=checker.FIXTURE_CLIENT_ADDRESS,
                    client_assigned_address=checker.FIXTURE_CLIENT_ADDRESS,
                    client_machine_fingerprint="1" * 64,
                    client_identity_fingerprint="c" * 64,
                    authorization=auth,
                    source_safety=safety,
                    transcript_events=[builder.make_event(kind, {"kind": kind}) for kind in checker.EXPECTED_TRANSCRIPT_EVENTS],
                )

    def test_invitation_path_must_stay_private(self) -> None:
        publicish_path = builder.ROOT / "roadmap" / "leaked-second-host-invitation.json"

        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.require_private_invitation_path(publicish_path)

        accepted_path = builder.OS_TEMP_ROOT / "second-host-command-source-test" / "invitation.json"
        self.assertEqual(builder.require_private_invitation_path(accepted_path), accepted_path.resolve())

        repo_private_path = builder.PRIVATE_INVITATION_ROOT / "second-host-command-source-test" / "invitation.json"
        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.require_private_invitation_path(repo_private_path)

    def test_invitation_cleanup_deletes_os_temp_invitation_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            invitation = Path(tmp) / "second-host-command-source-test" / "invitation.json"
            invitation.parent.mkdir(parents=True)
            invitation.write_text('{"credentialHex":"private"}\n', encoding="utf-8")

            self.assertTrue(builder.delete_private_invitation(invitation))
            self.assertFalse(invitation.exists())
            self.assertFalse(builder.delete_private_invitation(invitation))

        repo_private_path = builder.PRIVATE_INVITATION_ROOT / "second-host-command-source-test" / "invitation.json"
        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.delete_private_invitation(repo_private_path)

    def test_invitation_write_is_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            invitation = Path(tmp) / "second-host-command-source-test" / "invitation.json"
            payload = {
                "schemaVersion": "winui-original-binary-second-host-command-source-invitation.private.v1",
                "issuedAtUnix": 1000,
                "expiresAtUnix": 1120,
                "nonceWindowSeconds": 30,
            }

            builder.write_private_invitation(invitation, payload)
            self.assertTrue(invitation.exists())
            with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
                builder.write_private_invitation(invitation, payload)

    def test_invitation_expiry_is_checked_before_client_connect(self) -> None:
        invitation = {
            "issuedAtUnix": 1000,
            "expiresAtUnix": 1120,
            "nonceWindowSeconds": 30,
        }

        builder.require_invitation_not_expired(invitation, now_unix=1000)
        builder.require_invitation_not_expired(invitation, now_unix=1120)

        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.require_invitation_not_expired(invitation, now_unix=1121)
        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.require_invitation_not_expired(invitation, now_unix=969)
        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.require_invitation_not_expired({"issuedAtUnix": 1000, "expiresAtUnix": 1000, "nonceWindowSeconds": 30}, now_unix=1000)

    def test_server_session_expiry_helper_is_fail_closed(self) -> None:
        authorization = {
            "issuedAtUnix": 1000,
            "expiresAtUnix": 1120,
            "nonceWindowSeconds": 30,
        }

        self.assertFalse(builder.session_is_expired(authorization, now_unix=1120))
        self.assertTrue(builder.session_is_expired(authorization, now_unix=1121))

        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.session_is_expired({"issuedAtUnix": 1000}, now_unix=1000)

    def test_payload_timestamp_window_is_relative_to_server_observation(self) -> None:
        authorization = {
            "issuedAtUnix": 1000,
            "expiresAtUnix": 1120,
            "nonceWindowSeconds": 30,
        }

        self.assertTrue(builder.payload_timestamp_in_window({"timestamp": 1030}, authorization, observed_at_unix=1050))
        self.assertTrue(builder.payload_timestamp_in_window({"timestamp": 1080}, authorization, observed_at_unix=1050))
        self.assertFalse(builder.payload_timestamp_in_window({"timestamp": 1081}, authorization, observed_at_unix=1050))
        self.assertFalse(builder.payload_timestamp_in_window({"timestamp": 1019}, authorization, observed_at_unix=1050))
        self.assertFalse(builder.payload_timestamp_in_window({"timestamp": 1121}, authorization, observed_at_unix=1091))
        self.assertFalse(builder.payload_timestamp_in_window({"timestamp": "not-int"}, authorization, observed_at_unix=1050))

    def make_valid_live_command_message(self) -> dict[str, object]:
        return {
            "type": "command",
            "protocolVersion": checker.EXPECTED_PROTOCOL,
            "compatibilityKey": "session-compatible",
            "commandId": checker.EXPECTED_COMMAND_ID,
            "remoteSlot": checker.EXPECTED_REMOTE_SLOT,
            "command": checker.EXPECTED_REMOTE_COMMAND,
            "sequence": 2,
            "nonce": "second-host-p2-forward-0001",
            "timestamp": 1000,
            "wouldForwardToPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
            "mac": "0" * 64,
        }

    def make_valid_live_session_hello_message(self) -> dict[str, object]:
        identity = builder.make_machine_identity_preflight("2" * 64, evidence_mode="self-test-fixture")
        return {
            "type": "session_hello",
            "protocolVersion": checker.EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": "b" * 64,
            "clientIdentityFingerprint": "c" * 64,
            "nonce": "second-host-session-hello-0001",
            "timestamp": 1000,
            "clientIdentity": {
                "machineFingerprint": identity["machineFingerprint"],
                "machineFingerprintComputedByPreflight": identity["machineFingerprintComputedByPreflight"],
                "machineFingerprintSource": identity["machineFingerprintSource"],
                "machineFingerprintInputsRedacted": identity["machineFingerprintInputsRedacted"],
                "observedSourceAddress": checker.FIXTURE_CLIENT_ADDRESS,
                "assignedPrivateAddresses": [checker.FIXTURE_CLIENT_ADDRESS],
                "hostnameFingerprint": identity["hostnameFingerprint"],
                "platformFingerprint": identity["platformFingerprint"],
                "runtimeHostKind": identity["runtimeHostKind"],
                "runtimeHostKindSource": identity["runtimeHostKindSource"],
                "runtimeHostKindInputsRedacted": identity["runtimeHostKindInputsRedacted"],
                "wslDetectedByPreflight": identity["wslDetectedByPreflight"],
                "containerDetectedByPreflight": identity["containerDetectedByPreflight"],
            },
            "clientSourceSafety": builder.make_source_safety_side_evidence(
                role="client",
                copied_profile_sha256="5" * 64,
                installed_game_sha256="6" * 64,
                evidence_mode="self-test-fixture",
            ),
            "mac": "0" * 64,
        }

    def test_live_message_schema_rejects_unknown_top_level_field(self) -> None:
        command = self.make_valid_live_command_message()
        command["ignoredButSignedOverclaim"] = True

        self.assertEqual(builder.incoming_message_schema_error(command), "message-schema-mismatch")

    def test_live_message_schema_rejects_unknown_nested_identity_field(self) -> None:
        hello = self.make_valid_live_session_hello_message()
        hello["clientIdentity"]["extraMachineClaim"] = True  # type: ignore[index]

        self.assertEqual(builder.incoming_message_schema_error(hello), "message-schema-mismatch")

    def test_live_message_schema_rejects_missing_runtime_host_kind(self) -> None:
        hello = self.make_valid_live_session_hello_message()
        del hello["clientIdentity"]["runtimeHostKind"]  # type: ignore[index]

        self.assertEqual(builder.incoming_message_schema_error(hello), "message-schema-mismatch")

    def test_live_message_schema_rejects_missing_required_field(self) -> None:
        command = self.make_valid_live_command_message()
        del command["nonce"]

        self.assertEqual(builder.incoming_message_schema_error(command), "message-schema-mismatch")

    def test_live_message_schema_rejects_unknown_command_id(self) -> None:
        command = self.make_valid_live_command_message()
        command["commandId"] = "second-host-p2-forward-9999"

        self.assertEqual(builder.incoming_message_schema_error(command), "message-schema-mismatch")

    def test_live_message_schema_accepts_direct_input_negative_case_fields(self) -> None:
        command = self.make_valid_live_command_message()
        command.update(
            {
                "commandId": "second-host-reject-direct-input-0001",
                "directInputAttempted": True,
                "gameInputSentBySecondHostClient": True,
                "hostHelperInputSent": True,
            }
        )

        self.assertIsNone(builder.incoming_message_schema_error(command))

    def test_jsonl_lines_are_bounded_and_object_only(self) -> None:
        self.assertEqual(builder.MAX_JSON_LINE_BYTES, 4096)

        class Reader:
            def __init__(self, data: bytes):
                self.data = data

            def readline(self, limit: int = -1) -> bytes:
                if limit >= 0:
                    return self.data[:limit]
                return self.data

        oversized = b"{" + (b'"x":' + b'"' + (b"a" * builder.MAX_JSON_LINE_BYTES) + b'"}\n')
        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.read_json_line(Reader(oversized))

        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.read_json_line(Reader(b'["not-an-object"]\n'))

    def test_invitation_contains_private_credential_but_bundle_does_not(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = self.make_valid_bundle(root)
            payload = checker.read_json(bundle)
            self.assertNotIn("credentialHex", str(payload))
            checker.validate_bundle(bundle)

    def test_bundle_write_rejects_hash_drift_without_leaving_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_lan = lan.make_bundle_fixture(root)
            auth = builder.make_authorization(bytes.fromhex("25" * 32), lan.sha256_file(private_lan), "c" * 64)
            source_safety = builder.make_source_safety(
                host_copied_profile_sha256="3" * 64,
                host_installed_game_sha256="4" * 64,
                client_copied_profile_sha256="5" * 64,
                client_installed_game_sha256="6" * 64,
            )
            source_safety["host"]["installedGameSha256After"] = "9" * 64  # type: ignore[index]
            transcript_events = [builder.make_event(kind, {"kind": kind}) for kind in checker.EXPECTED_TRANSCRIPT_EVENTS]
            output = root / "drifted-second-host-command-source-proof.json"

            with self.assertRaises(Exception):
                builder.make_bundle_from_observation(
                    private_lan_proof_path=private_lan,
                    output_path=output,
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_bind_address=checker.FIXTURE_HOST_ADDRESS,
                    host_assigned_addresses=[checker.FIXTURE_HOST_ADDRESS],
                    host_machine_fingerprint="1" * 64,
                    client_source_address=checker.FIXTURE_CLIENT_ADDRESS,
                    client_assigned_address=checker.FIXTURE_CLIENT_ADDRESS,
                    client_machine_fingerprint="2" * 64,
                    client_identity_fingerprint="c" * 64,
                    authorization=auth,
                    source_safety=source_safety,
                    transcript_events=transcript_events,
                )

            self.assertFalse(output.exists())

    def test_machine_identity_preflight_redacts_inputs(self) -> None:
        identity = builder.make_machine_identity_preflight()

        self.assertTrue(identity["machineFingerprintComputedByPreflight"])
        self.assertEqual(identity["machineFingerprintSource"], "local-hostname-platform-preflight")
        self.assertTrue(identity["machineFingerprintInputsRedacted"])
        self.assertTrue(checker.is_hex64(identity["machineFingerprint"]))
        self.assertTrue(checker.is_hex64(identity["hostnameFingerprint"]))
        self.assertTrue(checker.is_hex64(identity["platformFingerprint"]))
        self.assertIn(identity["runtimeHostKind"], builder.KNOWN_RUNTIME_HOST_KINDS)
        self.assertTrue(identity["runtimeHostKindInputsRedacted"])
        self.assertIs(identity["wslDetectedByPreflight"], identity["runtimeHostKind"] == "wsl-on-host")
        self.assertIs(identity["containerDetectedByPreflight"], identity["runtimeHostKind"] == "container-on-host")

    def test_runtime_host_kind_auto_detects_vm_markers_without_env_spoofing(self) -> None:
        self.assertEqual(
            builder.detect_runtime_host_kind(
                dockerenv_exists=False,
                env_container="",
                platform_system="Windows",
                platform_release="10",
                platform_description="Windows-10",
                vm_marker_texts=["Microsoft Corporation Virtual Machine"],
            ),
            "vm-guest",
        )
        self.assertEqual(
            builder.detect_runtime_host_kind(
                dockerenv_exists=False,
                env_container="",
                platform_system="Linux",
                platform_release="6.8.0",
                platform_description="Linux-6.8.0",
                vm_marker_texts=["VMware Virtual Platform"],
            ),
            "vm-guest",
        )
        self.assertEqual(
            builder.detect_runtime_host_kind(
                dockerenv_exists=False,
                env_container="",
                platform_system="Windows",
                platform_release="10",
                platform_description="Windows-10",
                vm_marker_texts=["Dell Inc. Precision Tower"],
            ),
            "windows-host",
        )
        self.assertEqual(
            builder.detect_runtime_host_kind(
                dockerenv_exists=False,
                env_container="",
                platform_system="Linux",
                platform_release="6.8.0-microsoft-standard-WSL2",
                platform_description="Linux-6.8.0-microsoft-standard-WSL2",
                vm_marker_texts=["VMware Virtual Platform"],
            ),
            "wsl-on-host",
        )
        self.assertEqual(
            builder.detect_runtime_host_kind(
                dockerenv_exists=True,
                env_container="",
                platform_system="Windows",
                platform_release="10",
                platform_description="Windows-10",
                vm_marker_texts=["Microsoft Corporation Virtual Machine"],
            ),
            "container-on-host",
        )

    def test_machine_identity_auto_vm_detection_stays_auto_preflight(self) -> None:
        original_detector = builder.detect_runtime_host_kind
        try:
            builder.detect_runtime_host_kind = lambda: "vm-guest"  # type: ignore[assignment]
            identity = builder.make_machine_identity_preflight()
        finally:
            builder.detect_runtime_host_kind = original_detector  # type: ignore[assignment]

        self.assertEqual(identity["runtimeHostKind"], "vm-guest")
        self.assertEqual(identity["runtimeHostKindSource"], "auto-platform-preflight")
        self.assertTrue(identity["runtimeHostKindInputsRedacted"])
        self.assertFalse(identity["wslDetectedByPreflight"])
        self.assertFalse(identity["containerDetectedByPreflight"])

    def test_source_safety_preflight_hashes_roots_without_serializing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied = root / "copied-profile"
            installed = root / "installed-game"
            (copied / "data").mkdir(parents=True)
            installed.mkdir()
            (copied / "BEA.exe").write_bytes(b"copied-exe")
            (copied / "data" / "base_res_PC.aya").write_bytes(b"copied-data")
            (installed / "BEA.exe").write_bytes(b"installed-exe")

            evidence = builder.make_source_safety_side_evidence(
                role="host",
                copied_profile_root=copied,
                installed_game_root=installed,
            )
            serialized = json.dumps(evidence, sort_keys=True)

            self.assertEqual(evidence["sourceEvidenceMode"], "local-preflight-computed")
            self.assertTrue(evidence["computedByPreflight"])
            self.assertEqual(evidence["copiedProfileHashMode"], "directory-manifest-sha256")
            self.assertEqual(evidence["installedGameHashMode"], "directory-manifest-sha256")
            self.assertEqual(evidence["copiedProfileFileCount"], 2)
            self.assertEqual(evidence["installedGameFileCount"], 1)
            self.assertEqual(evidence["prePostHashSamplingMode"], "single-sample-preflight")
            self.assertEqual(evidence["prePostHashSampleCount"], 1)
            self.assertFalse(evidence["prePostHashSamplesDistinct"])
            self.assertFalse(evidence["pathValuesPublished"])
            self.assertFalse(evidence["absolutePathsSerialized"])
            self.assertNotIn(str(copied), serialized)
            self.assertNotIn(str(installed), serialized)

    def test_two_phase_source_safety_records_distinct_pre_post_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied = root / "copied-profile"
            installed = root / "installed-game"
            copied.mkdir()
            installed.mkdir()
            (copied / "BEA.exe").write_bytes(b"copied-exe")
            (installed / "BEA.exe").write_bytes(b"installed-exe")

            before = builder.make_source_safety_side_evidence(
                role="host",
                copied_profile_root=copied,
                installed_game_root=installed,
            )
            after = builder.make_source_safety_side_evidence(
                role="host",
                copied_profile_root=copied,
                installed_game_root=installed,
            )

            merged = builder.make_two_phase_source_safety_side_evidence(
                role="host",
                before=before,
                after=after,
            )

            self.assertEqual(merged["prePostHashSamplingMode"], "live-pre-post")
            self.assertEqual(merged["prePostHashSampleCount"], 2)
            self.assertTrue(merged["prePostHashSamplesDistinct"])
            self.assertEqual(merged["copiedProfileSha256Before"], merged["copiedProfileSha256After"])
            self.assertEqual(merged["installedGameSha256Before"], merged["installedGameSha256After"])

    def test_two_phase_source_safety_rejects_file_count_drift(self) -> None:
        before = {
            "sourceEvidenceMode": "local-preflight-computed",
            "copiedProfileHashMode": "directory-manifest-sha256",
            "installedGameHashMode": "directory-manifest-sha256",
            "copiedProfileFileCount": 2,
            "installedGameFileCount": 1,
            "copiedProfileSha256Before": "1" * 64,
            "installedGameSha256Before": "2" * 64,
        }
        after = dict(before)
        after["copiedProfileFileCount"] = 3

        with self.assertRaises(builder.SecondHostCommandSourceBundleBuildError):
            builder.make_two_phase_source_safety_side_evidence(role="host", before=before, after=after)

    def test_listener_lifecycle_receipt_records_bind_teardown_evidence(self) -> None:
        receipt = builder.make_listener_lifecycle_receipt(
            bind_host=checker.FIXTURE_HOST_ADDRESS,
            port=49152,
            evidence_mode="live-server-socket-receipt",
            listener_closed=True,
            post_close_connect_rejected=True,
        )

        self.assertEqual(receipt["schemaVersion"], "winui-original-binary-second-host-listener-lifecycle.v1")
        self.assertEqual(receipt["evidenceMode"], "live-server-socket-receipt")
        self.assertEqual(receipt["bindAddress"], checker.FIXTURE_HOST_ADDRESS)
        self.assertEqual(receipt["bindAddressClass"], "private-lan-non-loopback")
        self.assertTrue(checker.is_hex64(receipt["sanitizedEndpointSha256"]))
        self.assertTrue(receipt["bindAttempted"])
        self.assertTrue(receipt["bindSucceeded"])
        self.assertTrue(receipt["boundHostMatchesTransport"])
        self.assertTrue(receipt["listenerClosedBeforeBundleWrite"])
        self.assertTrue(receipt["postCloseConnectRejected"])
        self.assertFalse(receipt["wildcardBind"])
        self.assertFalse(receipt["loopbackBind"])
        self.assertFalse(receipt["publicRoutableBind"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
