#!/usr/bin/env python3
"""Tests for the second-host live-readiness preflight helper."""

from __future__ import annotations

import copy
import unittest

import winui_original_binary_second_host_live_readiness as readiness


def ipv4(*octets: int) -> str:
    return ".".join(str(octet) for octet in octets)


class SecondHostLiveReadinessTests(unittest.TestCase):
    def test_classifies_private_wifi_candidate_and_excludes_wsl(self) -> None:
        payload = readiness.build_summary(
            interface_rows=[
                {"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": 4},
                {"InterfaceAlias": "vEthernet (WSL (Hyper-V firewall))", "IPAddress": ipv4(172, 26, 112, 1), "AddressState": 4},
            ]
        )

        summary = readiness.validate_summary(payload)

        self.assertEqual(summary["candidatePrivateBindAddressCount"], 1)
        self.assertEqual(summary["wslOnHostInterfaceCount"], 1)
        self.assertFalse(summary["baseOnlineMultiplayerReady"])
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
        self.assertFalse(summary["acceptedLiveSecondHostCommandSourceProof"])

    def test_reports_no_candidate_when_only_wsl_and_loopback_exist(self) -> None:
        payload = readiness.build_summary(
            interface_rows=[
                {"InterfaceAlias": "vEthernet (WSL)", "IPAddress": ipv4(172, 26, 112, 1), "AddressState": "Preferred"},
                {"InterfaceAlias": "Loopback", "IPAddress": ipv4(127, 0, 0, 1), "AddressState": "Preferred"},
            ]
        )

        summary = readiness.validate_summary(payload)

        self.assertEqual(summary["candidatePrivateBindAddressCount"], 0)
        self.assertEqual(summary["wslOnHostInterfaceCount"], 1)

    def test_rejects_online_overclaim(self) -> None:
        payload = readiness.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}]
        )
        payload["proofBooleans"]["baseOnlineMultiplayerReady"] = True

        with self.assertRaises(readiness.SecondHostLiveReadinessError):
            readiness.validate_summary(payload)

    def test_rejects_missing_live_receipt_requirement(self) -> None:
        payload = readiness.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}]
        )
        weakened = copy.deepcopy(payload)
        weakened["liveRunRequirements"]["requiresListenerLifecycleReceipt"] = False

        with self.assertRaises(readiness.SecondHostLiveReadinessError):
            readiness.validate_summary(weakened)

    def test_marks_server_inputs_complete_only_when_required_inputs_exist(self) -> None:
        incomplete = readiness.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}]
        )
        complete = readiness.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
            private_lan_proof=readiness.ROOT / "subagents" / "placeholder.json",
            client_identity_fingerprint="a" * 64,
            command_source_kind="distinct-vm-private-lan-labeled-vm-only",
            host_topology="vm-labeled-same-physical",
        )

        self.assertFalse(readiness.validate_summary(incomplete)["serverCommandInputsComplete"])
        self.assertTrue(readiness.validate_summary(complete)["serverCommandInputsComplete"])

    def test_marks_server_inputs_complete_with_explicit_eligible_bind_host(self) -> None:
        complete = readiness.build_summary(
            interface_rows=[
                {"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"},
                {"InterfaceAlias": "vEthernet (WSL)", "IPAddress": ipv4(172, 26, 112, 1), "AddressState": "Preferred"},
            ],
            bind_host=ipv4(172, 20, 10, 7),
            private_lan_proof=readiness.ROOT / "subagents" / "placeholder.json",
            client_identity_fingerprint="a" * 64,
            command_source_kind="distinct-vm-private-lan-labeled-vm-only",
            host_topology="vm-labeled-same-physical",
        )

        summary = readiness.validate_summary(complete)

        self.assertTrue(summary["serverCommandInputsComplete"])

    def test_rejects_complete_inputs_for_ineligible_selected_bind_host(self) -> None:
        fixture_rows = [
            {"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"},
            {"InterfaceAlias": "vEthernet (WSL)", "IPAddress": ipv4(172, 26, 112, 1), "AddressState": "Preferred"},
            {"InterfaceAlias": "Ethernet", "IPAddress": ipv4(169, 254, 10, 20), "AddressState": "Preferred"},
        ]

        for bind_host in (
            ipv4(172, 26, 112, 1),
            ipv4(169, 254, 10, 20),
            ipv4(192, 0, 2, 55),
            ipv4(10, 55, 55, 55),
        ):
            with self.subTest(bind_host=bind_host):
                payload = readiness.build_summary(
                    interface_rows=fixture_rows,
                    bind_host=bind_host,
                    private_lan_proof=readiness.ROOT / "subagents" / "placeholder.json",
                    client_identity_fingerprint="a" * 64,
                    command_source_kind="distinct-vm-private-lan-labeled-vm-only",
                    host_topology="vm-labeled-same-physical",
                )

                summary = readiness.validate_summary(payload)

                self.assertFalse(summary["serverCommandInputsComplete"])

    def test_does_not_treat_contract_allowed_physical_mode_as_locally_ready(self) -> None:
        payload = readiness.build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
            private_lan_proof=readiness.ROOT / "subagents" / "placeholder.json",
            client_identity_fingerprint="a" * 64,
            command_source_kind="distinct-physical-host-private-lan",
        )

        summary = readiness.validate_summary(payload)

        self.assertFalse(summary["serverCommandInputsComplete"])


if __name__ == "__main__":
    unittest.main()
