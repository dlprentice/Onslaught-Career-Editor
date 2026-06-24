#!/usr/bin/env python3
"""Tests for the second-host live run kit helper."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import winui_original_binary_second_host_command_source_client as client
import winui_original_binary_second_host_live_run_kit as kit
import winui_safe_copy_online_private_lan_transport_smoke_check as private_lan


def ipv4(*octets: int) -> str:
    return ".".join(str(octet) for octet in octets)


class SecondHostLiveRunKitTests(unittest.TestCase):
    def make_client_preflight(
        self,
        root: Path,
        *,
        runtime_host_kind: str | None = None,
        auto_runtime_host_kind: str | None = None,
    ) -> dict[str, object]:
        copied = root / "client-copied-profile"
        installed = root / "client-installed-game"
        (copied / "data").mkdir(parents=True, exist_ok=True)
        installed.mkdir(exist_ok=True)
        (copied / "BEA.exe").write_bytes(b"client copied exe")
        (copied / "data" / "base_res_PC.aya").write_bytes(b"client copied resource")
        (installed / "BEA.exe").write_bytes(b"client installed exe")
        if auto_runtime_host_kind is None:
            return client.build_identity_preflight_summary(
                client_copied_profile_root=copied,
                client_installed_game_root=installed,
                client_runtime_host_kind=runtime_host_kind,
            )
        original_detector = client.builder.detect_runtime_host_kind
        try:
            client.builder.detect_runtime_host_kind = lambda: auto_runtime_host_kind  # type: ignore[assignment]
            return client.build_identity_preflight_summary(
                client_copied_profile_root=copied,
                client_installed_game_root=installed,
                client_runtime_host_kind=runtime_host_kind,
            )
        finally:
            client.builder.detect_runtime_host_kind = original_detector  # type: ignore[assignment]

    def make_host_roots(self, root: Path) -> tuple[Path, Path]:
        copied = root / "host-copied-profile"
        installed = root / "host-installed-game"
        (copied / "data").mkdir(parents=True)
        installed.mkdir()
        (copied / "BEA.exe").write_bytes(b"host copied exe")
        (copied / "data" / "base_res_PC.aya").write_bytes(b"host copied resource")
        (installed / "BEA.exe").write_bytes(b"host installed exe")
        return copied, installed

    def make_live_candidate_private_lan_proof(self, root: Path) -> Path:
        path = private_lan.make_bundle_fixture(root)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["transport"]["bindHost"] = ipv4(10, 77, 20, 114)
        payload["authorization"]["authKeyFingerprint"] = "0123456789abcdef" * 4
        payload["authorization"]["serverIdentityFingerprint"] = "fedcba9876543210" * 4
        payload["transportTranscript"]["serverIdentityFingerprint"] = payload["authorization"]["serverIdentityFingerprint"]
        payload["transportTranscript"]["events"][0]["bindHost"] = ipv4(10, 77, 20, 114)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_ready_kit_requires_host_inputs_and_computed_client_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = self.make_live_candidate_private_lan_proof(root / "private-lan")
            payload = kit.build_summary(
                interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                bind_host=ipv4(172, 20, 10, 7),
                command_source_kind="distinct-physical-host-private-lan",
                host_topology="distinct-physical-private-host",
                private_lan_proof=private_lan_proof,
                client_preflight_payload=self.make_client_preflight(root),
                host_copied_profile_root=host_copied,
                host_installed_game_root=host_installed,
                invitation_path=invitation_path,
            )

            summary = kit.validate_summary(payload, require_ready=True)

            self.assertTrue(summary["readyToRunLiveCommandSource"])
            self.assertTrue(summary["serverCommandInputsComplete"])
            self.assertTrue(summary["clientPreflightProvided"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
            self.assertFalse(summary["acceptedLiveSecondHostCommandSourceProof"])
            self.assertTrue(payload["privateRunInputs"]["privateLanProofValidated"])
            self.assertTrue(payload["privateLanProof"]["liveValidationCandidate"])
            self.assertTrue(payload["hostSourceSafety"]["computedByPreflight"])
            self.assertEqual(payload["hostSourceSafety"]["sourceEvidenceMode"], "local-preflight-computed")
            self.assertTrue(payload["privateRunInputs"]["invitationPathValidatedUnderOsTempOutsideRepo"])
            self.assertTrue(payload["clientPreflight"]["runtimeKindCompatibleWithCommandSourceKind"])
            self.assertTrue(payload["clientPreflight"]["runtimeKindLiveValidationCompatible"])

    def test_fixture_private_lan_proof_is_attempt_only_not_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = private_lan.make_bundle_fixture(root / "private-lan")
            payload = kit.build_summary(
                interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                bind_host=ipv4(172, 20, 10, 7),
                command_source_kind="distinct-physical-host-private-lan",
                host_topology="distinct-physical-private-host",
                private_lan_proof=private_lan_proof,
                client_preflight_payload=self.make_client_preflight(root),
                host_copied_profile_root=host_copied,
                host_installed_game_root=host_installed,
                invitation_path=invitation_path,
            )

            checked = kit.validate_summary(payload)

            self.assertTrue(checked["readyToAttemptHarness"])
            self.assertFalse(checked["readyForLiveValidationCandidate"])
            self.assertFalse(checked["readyToRunLiveCommandSource"])
            self.assertFalse(payload["privateLanProof"]["liveValidationCandidate"])
            self.assertIn("documentation-or-reserved-bind-host", payload["privateLanProof"]["liveValidationCompatibilityReason"])
            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.validate_summary(payload, require_ready=True)

    def test_vm_labeled_operator_runtime_is_attempt_only_not_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = self.make_live_candidate_private_lan_proof(root / "private-lan")
            payload = kit.build_summary(
                interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                bind_host=ipv4(172, 20, 10, 7),
                command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                host_topology="vm-labeled-same-physical",
                private_lan_proof=private_lan_proof,
                client_preflight_payload=self.make_client_preflight(root, runtime_host_kind="vm-guest"),
                host_copied_profile_root=host_copied,
                host_installed_game_root=host_installed,
                invitation_path=invitation_path,
            )

            checked = kit.validate_summary(payload)

            self.assertTrue(checked["readyToAttemptHarness"])
            self.assertFalse(checked["readyForLiveValidationCandidate"])
            self.assertFalse(checked["readyToRunLiveCommandSource"])
            self.assertTrue(payload["clientPreflight"]["runtimeKindCompatibleWithCommandSourceKind"])
            self.assertFalse(payload["clientPreflight"]["runtimeKindLiveValidationCompatible"])
            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.validate_summary(payload, require_ready=True)

    def test_vm_labeled_auto_detected_vm_client_can_be_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = self.make_live_candidate_private_lan_proof(root / "private-lan")
            payload = kit.build_summary(
                interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                bind_host=ipv4(172, 20, 10, 7),
                command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                host_topology="vm-labeled-same-physical",
                private_lan_proof=private_lan_proof,
                client_preflight_payload=self.make_client_preflight(root, auto_runtime_host_kind="vm-guest"),
                host_copied_profile_root=host_copied,
                host_installed_game_root=host_installed,
                invitation_path=invitation_path,
            )

            checked = kit.validate_summary(payload, require_ready=True)

            self.assertTrue(checked["readyToRunLiveCommandSource"])
            self.assertFalse(checked["baseOnlineMultiplayerReady"])
            self.assertFalse(checked["hostJoinControlsMayBeEnabled"])
            self.assertEqual(payload["clientPreflight"]["runtimeHostKind"], "vm-guest")
            self.assertEqual(payload["clientPreflight"]["runtimeHostKindSource"], "auto-platform-preflight")
            self.assertTrue(payload["clientPreflight"]["runtimeKindLiveValidationCompatible"])

    def test_ready_vm_kit_requires_vm_guest_client_runtime_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = private_lan.make_bundle_fixture(root / "private-lan")
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"

            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.build_summary(
                    interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                    bind_host=ipv4(172, 20, 10, 7),
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_topology="vm-labeled-same-physical",
                    private_lan_proof=private_lan_proof,
                    client_preflight_payload=self.make_client_preflight(root),
                    host_copied_profile_root=host_copied,
                    host_installed_game_root=host_installed,
                    invitation_path=invitation_path,
                )

    def test_ready_physical_kit_rejects_operator_supplied_client_runtime_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = private_lan.make_bundle_fixture(root / "private-lan")
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"

            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.build_summary(
                    interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                    bind_host=ipv4(172, 20, 10, 7),
                    command_source_kind="distinct-physical-host-private-lan",
                    host_topology="distinct-physical-private-host",
                    private_lan_proof=private_lan_proof,
                    client_preflight_payload=self.make_client_preflight(root, runtime_host_kind="windows-host"),
                    host_copied_profile_root=host_copied,
                    host_installed_game_root=host_installed,
                    invitation_path=invitation_path,
                )

    def test_default_check_is_not_ready_and_does_not_claim_netplay(self) -> None:
        payload = kit.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}]
        )

        summary = kit.validate_summary(payload)

        self.assertFalse(summary["readyToRunLiveCommandSource"])
        self.assertFalse(summary["baseOnlineMultiplayerReady"])
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
        with self.assertRaises(kit.SecondHostLiveRunKitError):
            kit.validate_summary(payload, require_ready=True)

    def test_rejects_operator_hash_only_client_preflight_for_ready_kit(self) -> None:
        payload = client.build_identity_preflight_summary(
            client_copied_profile_sha256="a" * 64,
            client_installed_game_sha256="b" * 64,
        )

        with self.assertRaises(kit.SecondHostLiveRunKitError):
            kit.validate_client_preflight(payload)

    def test_rejects_operator_machine_fingerprint_client_preflight_for_ready_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = self.make_client_preflight(root)
            payload["clientIdentityFingerprint"] = "c" * 64
            payload["machineIdentity"]["machineFingerprint"] = "c" * 64  # type: ignore[index]
            payload["machineIdentity"]["machineFingerprintComputedByPreflight"] = False  # type: ignore[index]
            payload["machineIdentity"]["machineFingerprintSource"] = "operator-supplied-machine-fingerprint"  # type: ignore[index]

            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.validate_client_preflight(payload)

    def test_redacted_templates_do_not_serialize_source_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            client_payload = self.make_client_preflight(root)
            payload = kit.build_summary(
                interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                client_preflight_payload=client_payload,
            )
            serialized = json.dumps(payload, sort_keys=True)

            self.assertNotIn(str(root), serialized)
            self.assertIn("<host-private-ip>", serialized)
            self.assertIn("<client-copied-profile-root>", serialized)

    def test_rejects_online_overclaim(self) -> None:
        payload = kit.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}]
        )
        payload["proofBooleans"]["baseOnlineMultiplayerReady"] = True

        with self.assertRaises(kit.SecondHostLiveRunKitError):
            kit.validate_summary(payload)

    def test_ready_kit_rejects_repo_invitation_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            host_copied, host_installed = self.make_host_roots(root)
            private_lan_proof = private_lan.make_bundle_fixture(root / "private-lan")

            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.build_summary(
                    interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                    bind_host=ipv4(172, 20, 10, 7),
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_topology="vm-labeled-same-physical",
                    private_lan_proof=private_lan_proof,
                    client_preflight_payload=self.make_client_preflight(root, runtime_host_kind="vm-guest"),
                    host_copied_profile_root=host_copied,
                    host_installed_game_root=host_installed,
                    invitation_path=kit.ROOT / "roadmap" / "leaked-second-host-invitation.json",
                )

    def test_ready_kit_rejects_missing_private_lan_proof_or_host_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            host_copied, host_installed = self.make_host_roots(root)
            invitation_path = Path(tempfile.gettempdir()) / "bea-second-host-live-run-kit-test" / "invitation.json"

            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.build_summary(
                    interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                    bind_host=ipv4(172, 20, 10, 7),
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_topology="vm-labeled-same-physical",
                    private_lan_proof=root / "missing-private-lan-proof.json",
                    client_preflight_payload=self.make_client_preflight(root, runtime_host_kind="vm-guest"),
                    host_copied_profile_root=host_copied,
                    host_installed_game_root=host_installed,
                    invitation_path=invitation_path,
                )

            private_lan_proof = private_lan.make_bundle_fixture(root / "private-lan")
            with self.assertRaises(kit.SecondHostLiveRunKitError):
                kit.build_summary(
                    interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
                    bind_host=ipv4(172, 20, 10, 7),
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_topology="vm-labeled-same-physical",
                    private_lan_proof=private_lan_proof,
                    client_preflight_payload=self.make_client_preflight(root, runtime_host_kind="vm-guest"),
                    host_copied_profile_root=root / "missing-host-copied-profile",
                    host_installed_game_root=host_installed,
                    invitation_path=invitation_path,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
