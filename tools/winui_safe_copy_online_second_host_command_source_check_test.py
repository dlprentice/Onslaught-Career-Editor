#!/usr/bin/env python3
"""Tests for second-host private-LAN command-source proof validation."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_second_host_command_source_check as checker


class SecondHostCommandSourceCheckTests(unittest.TestCase):
    def test_validates_public_gate_contract_without_live_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gate = Path(tmp) / "gate.json"
            checker.write_json(gate, checker.make_gate_fixture())

            summary = checker.validate_gate(gate)

            self.assertEqual(summary["schemaVersion"], checker.EXPECTED_GATE_SCHEMA)
            self.assertFalse(summary["acceptedLiveSecondHostCommandSourceProof"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["multiHostLanPlayProof"])
            self.assertEqual(summary["newBeaLaunchCount"], 0)
            self.assertEqual(summary["cdbAttachCount"], 0)
            self.assertEqual(summary["nextRequiredProof"], "host-runtime-delivery-from-source-bound-distinct-command-source")

    def test_rejects_public_gate_host_join_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gate = Path(tmp) / "gate.json"
            payload = checker.make_gate_fixture()
            payload["currentEvidence"]["hostJoinControlsMayBeEnabled"] = True
            checker.write_json(gate, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_gate(gate)

    def test_accepts_valid_fixture_without_online_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            transcript_hashes = {row["kind"]: row["payloadSha256"] for row in payload["transportTranscript"]["events"]}
            accepted = payload["commands"]["accepted"][0]

            summary = checker.validate_bundle(bundle)

            self.assertEqual(summary["schemaVersion"], checker.EXPECTED_SCHEMA)
            self.assertEqual(summary["commandSourceKind"], "distinct-vm-private-lan-labeled-vm-only")
            self.assertTrue(summary["secondHostCommandSourceProof"])
            self.assertFalse(summary["acceptedLiveSecondHostCommandSourceProof"])
            self.assertFalse(summary["secondPhysicalHostProof"])
            self.assertTrue(payload["transport"]["samePhysicalMachineOnly"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["multiHostLanPlayProof"])
            self.assertFalse(summary["publicMatchmakingProof"])
            self.assertFalse(summary["nativeBeaNetcodeProof"])
            self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
            self.assertEqual(summary["metadataOnlySlots"], ["P3", "P4"])
            self.assertEqual(summary["acceptedCommandId"], checker.EXPECTED_COMMAND_ID)
            self.assertEqual(accepted["requestPayloadSha256"], transcript_hashes["client_command_p2_forward"])
            self.assertEqual(accepted["responsePayloadSha256"], transcript_hashes["server_command_accepted"])
            self.assertEqual(payload["networkIdentityEvidence"]["host"]["runtimeHostKind"], "windows-host")
            self.assertEqual(payload["networkIdentityEvidence"]["client"]["runtimeHostKind"], "vm-guest")
            self.assertFalse(summary["gameInputSentBySecondHostClient"])
            self.assertFalse(summary["hostHelperInputSent"])
            self.assertFalse(summary["sessionSecurityHardeningPresent"])

    def test_physical_and_vm_source_flags_stay_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="distinct-physical-host-private-lan")
            payload = checker.read_json(bundle)
            self.assertFalse(payload["transport"]["samePhysicalMachineOnly"])
            self.assertTrue(checker.validate_bundle(bundle)["secondPhysicalHostProof"])

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="distinct-physical-host-private-lan")
            payload = checker.read_json(bundle)
            payload["transport"]["samePhysicalMachineOnly"] = True
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="distinct-vm-private-lan-labeled-vm-only")
            payload = checker.read_json(bundle)
            payload["transport"]["samePhysicalMachineOnly"] = False
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_accepts_session_security_hardening_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), include_security_hardening=True)

            summary = checker.validate_bundle(bundle)

            self.assertTrue(summary["sessionSecurityHardeningPresent"])
            self.assertEqual(summary["sessionSecurityHardeningEvidenceMode"], "self-test-fixture")

    def test_rejects_tampered_session_security_hardening(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), include_security_hardening=True)
            payload = checker.read_json(bundle)
            payload["sessionSecurityHardening"]["replayNonceLiveRejected"] = False
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_live_hardening_without_observed_payload_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
            )
            payload = checker.read_json(bundle)
            del payload["sessionSecurityHardening"]["cases"][0]["requestPayloadSha256ByEvent"]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_live_validation_requires_live_hardening_and_local_source_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle, require_live=True)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
            )

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle, require_live=True)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
                source_safety_evidence_mode="local-preflight-computed",
            )

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle, require_live=True)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
                source_safety_evidence_mode="local-preflight-computed",
                listener_evidence_mode="self-test-fixture",
            )

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle, require_live=True)

    def test_live_validation_rejects_live_labeled_fixture_sentinels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
                source_safety_evidence_mode="local-preflight-computed",
            )
            payload = checker.read_json(bundle)
            for offset, row in enumerate(payload["transportTranscript"]["events"], start=1):
                row["serverObservedAtUnix"] = 1000 + offset
            for side in ("host", "client"):
                payload["networkIdentityEvidence"][side]["machineFingerprintSource"] = "local-hostname-platform-preflight"
                payload["networkIdentityEvidence"][side]["runtimeHostKindSource"] = "auto-platform-preflight"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle, require_live=True)

    def test_live_physical_validation_rejects_operator_supplied_runtime_host_kind(self) -> None:
        for side in ("host", "client"):
            with self.subTest(side=side):
                with tempfile.TemporaryDirectory() as tmp:
                    bundle = checker.make_bundle_fixture(
                        Path(tmp),
                        command_source_kind="distinct-physical-host-private-lan",
                        include_security_hardening=True,
                        security_hardening_evidence_mode="live-server-client-transcript",
                        source_safety_evidence_mode="local-preflight-computed",
                    )
                    payload = checker.read_json(bundle)
                    payload["networkIdentityEvidence"][side]["runtimeHostKindSource"] = "operator-supplied-runtime-host-kind"
                    checker.write_json(bundle, payload)

                    with self.assertRaises(checker.SecondHostCommandSourceProofError):
                        checker.validate_bundle(bundle, require_live=True)

    def test_rejects_loopback_or_same_host_source_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), client_source_address="127.0.0.1")
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), client_source_address=checker.FIXTURE_HOST_ADDRESS)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_documentation_or_fixture_only_addresses(self) -> None:
        for address in ("192.0.2.114", "198.51.100.114", "203.0.113.114"):
            with self.subTest(address=address):
                with tempfile.TemporaryDirectory() as tmp:
                    bundle = checker.make_bundle_fixture(Path(tmp), host_address=address)
                    with self.assertRaises(checker.SecondHostCommandSourceProofError):
                        checker.validate_bundle(bundle)

    def test_rejects_wsl_or_same_workstation_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="wsl-on-host")
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="same-workstation-process")
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_self_attested_same_host_identity_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["networkIdentityEvidence"]["client"]["machineFingerprint"] = payload["networkIdentityEvidence"]["host"]["machineFingerprint"]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["networkIdentityEvidence"]["runtimeMarkers"]["wslDetectedOnClient"] = True
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        for runtime_kind in ("wsl-on-host", "container-on-host", "unknown-host"):
            with self.subTest(runtime_kind=runtime_kind):
                with tempfile.TemporaryDirectory() as tmp:
                    bundle = checker.make_bundle_fixture(Path(tmp))
                    payload = checker.read_json(bundle)
                    payload["networkIdentityEvidence"]["client"]["runtimeHostKind"] = runtime_kind
                    checker.write_json(bundle, payload)

                    with self.assertRaises(checker.SecondHostCommandSourceProofError):
                        checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="distinct-vm-private-lan-labeled-vm-only")
            payload = checker.read_json(bundle)
            payload["networkIdentityEvidence"]["client"]["runtimeHostKind"] = "windows-host"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), command_source_kind="distinct-physical-host-private-lan")
            payload = checker.read_json(bundle)
            payload["networkIdentityEvidence"]["client"]["runtimeHostKind"] = "vm-guest"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["networkIdentityEvidence"]["client"]["machineFingerprintComputedByPreflight"] = False
            payload["networkIdentityEvidence"]["client"]["machineFingerprintSource"] = "operator-supplied-machine-fingerprint"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            del payload["networkIdentityEvidence"]["host"]["hostnameFingerprint"]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_p3_p4_gameplay_or_runtime_overclaims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), p3_gameplay_claim=True)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), multi_host_play_claim=True)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), native_netcode_claim=True)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_missing_two_sided_source_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), copied_hashes=False)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp), installed_hashes=False)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["sourceSafety"]["computedByPreflight"] = False
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["sourceSafety"]["client"]["sourceEvidenceMode"] = "operator-supplied-hash"
            payload["sourceSafety"]["client"]["computedByPreflight"] = False
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["sourceSafety"]["host"]["absolutePathsSerialized"] = True
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["sourceSafety"]["host"]["installedGameSha256After"] = "0" * 64
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_live_validation_rejects_one_sample_source_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
                source_safety_evidence_mode="local-preflight-computed",
            )
            payload = checker.read_json(bundle)
            for side in ("host", "client"):
                payload["sourceSafety"][side]["prePostHashSamplingMode"] = "single-sample-preflight"
                payload["sourceSafety"][side]["prePostHashSampleCount"] = 1
                payload["sourceSafety"][side]["prePostHashSamplesDistinct"] = False
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle, require_live=True)

    def test_rejects_missing_invitation_lifecycle_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            del payload["invitationLifecycle"]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_missing_or_unsafe_listener_lifecycle_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            del payload["listenerLifecycle"]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        for key, value in (
            ("wildcardBind", True),
            ("loopbackBind", True),
            ("publicRoutableBind", True),
            ("listenerAcceptLimit", 2),
            ("listenerClosedBeforeBundleWrite", False),
            ("teardownObserved", False),
            ("postCloseConnectRejected", False),
        ):
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory() as tmp:
                    bundle = checker.make_bundle_fixture(Path(tmp))
                    payload = checker.read_json(bundle)
                    payload["listenerLifecycle"][key] = value
                    checker.write_json(bundle, payload)

                    with self.assertRaises(checker.SecondHostCommandSourceProofError):
                        checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["invitationLifecycle"]["deletionSucceeded"] = False
            payload["invitationLifecycle"]["postDeleteExists"] = True
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_serialized_credentials_or_private_publication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["authorization"]["rawCredential"] = "not-allowed"
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["releaseBoundary"]["rawPrivateAddressPublishedToPublicDocs"] = True
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["nonClaims"]["hostJoinControlsMayBeEnabled"] = True
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        for hidden_value in ("true", "yes", 1):
            with self.subTest(hidden_value=hidden_value):
                with tempfile.TemporaryDirectory() as tmp:
                    bundle = checker.make_bundle_fixture(Path(tmp))
                    payload = checker.read_json(bundle)
                    payload["networkIdentityEvidence"]["client"]["hostJoinControlsMayBeEnabled"] = hidden_value
                    checker.write_json(bundle, payload)
                    with self.assertRaises(checker.SecondHostCommandSourceProofError):
                        checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["authorization"]["authKeyFingerprint"] = "z" * 64
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["authorization"]["credentialStorage"] = "ephemeral-env-or-stdin-not-serialized"
            checker.write_json(bundle, payload)
            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_transcript_count_or_sequence_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["transportTranscript"]["events"].append({"kind": "wsl_client_forward", "payloadSha256": "7" * 64})
            payload["transportTranscript"]["messageCount"] += 1
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["transportTranscript"]["events"][4], payload["transportTranscript"]["events"][5] = (
                payload["transportTranscript"]["events"][5],
                payload["transportTranscript"]["events"][4],
            )
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_missing_required_rejection_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = checker.read_json(bundle)
            payload["commands"]["rejected"] = [
                row for row in payload["commands"]["rejected"] if row["reason"] != "public-internet-host-not-allowed"
            ]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_mutated_accepted_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            payload["commands"]["accepted"][0]["wouldForwardToPrivateLanCommandId"] = "wrong-target"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            del payload["commands"]["accepted"][0]["requestPayloadSha256"]
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            payload["commands"]["accepted"][0]["responsePayloadSha256"] = "0" * 64
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            payload["commands"]["accepted"][0]["requestEvent"] = "client_command_p3_forward"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_extra_accepted_command_or_rejected_row_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            payload["commands"]["accepted"][0]["ignoredButSignedOverclaim"] = True
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            payload["commands"]["rejected"][0]["debugAcceptedRoute"] = "P3"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_extra_transcript_event_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = checker.make_bundle_fixture(Path(tmp))
            payload = copy.deepcopy(checker.read_json(bundle))
            payload["transportTranscript"]["events"][0]["rawPayload"] = {"type": "server_bound"}
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)

    def test_rejects_private_lan_reference_escaping_proof_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = checker.make_bundle_fixture(root / "proof")
            payload = checker.read_json(bundle)
            payload["privateLanTransportProofBundle"] = "../proof/private-lan/private-transport-smoke-proof.json"
            checker.write_json(bundle, payload)

            with self.assertRaises(checker.SecondHostCommandSourceProofError):
                checker.validate_bundle(bundle)


if __name__ == "__main__":
    unittest.main(verbosity=2)
