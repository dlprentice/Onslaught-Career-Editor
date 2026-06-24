#!/usr/bin/env python3
"""Tests for second-host online readiness contract validation."""

from __future__ import annotations

import copy
import unittest

import winui_safe_copy_online_second_host_readiness_check as checker


class SecondHostReadinessCheckTests(unittest.TestCase):
    def test_accepts_valid_second_host_readiness_contract_fixture(self) -> None:
        payload = checker.make_fixture()

        summary = checker.validate_contract(payload)

        self.assertEqual(summary["schemaVersion"], "winui-original-binary-second-host-readiness.v1")
        self.assertEqual(summary["readinessScope"], "second-host-command-source-readiness-not-runtime-proof")
        self.assertFalse(summary["baseOnlineMultiplayerReady"])
        self.assertFalse(summary["secondHostProof"])
        self.assertFalse(summary["multiHostLanProof"])
        self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
        self.assertEqual(summary["metadataOnlySlots"], ["P3", "P4"])
        self.assertEqual(summary["minimumRequiredNextEvidence"], "distinct-private-host-command-source-proof")

    def test_rejects_second_host_overclaim(self) -> None:
        payload = checker.make_fixture()
        payload["readiness"]["secondHostProof"] = True

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_enabled_host_join_action(self) -> None:
        payload = checker.make_fixture()
        payload["blockedActions"][0]["enabled"] = True

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_missing_distinct_host_requirement(self) -> None:
        payload = checker.make_fixture()
        payload["requiredNextEvidence"] = [
            row for row in payload["requiredNextEvidence"] if row["id"] != "distinct-private-host-command-source-proof"
        ]

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_mutated_public_server_claim(self) -> None:
        payload = copy.deepcopy(checker.make_fixture())
        payload["nonClaims"]["publicServerProof"] = True

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_loopback_or_wsl_as_second_host_source(self) -> None:
        payload = checker.make_fixture()
        payload["secondHostAcceptanceCriteria"]["forbiddenCommandSourceKinds"].remove("loopback")

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

        payload = checker.make_fixture()
        payload["secondHostAcceptanceCriteria"]["forbiddenCommandSourceKinds"].remove("wsl-on-host")

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_missing_two_sided_source_safety(self) -> None:
        payload = checker.make_fixture()
        payload["secondHostAcceptanceCriteria"]["requiresInstalledGamePrePostHashesOnBothSides"] = False

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_missing_live_listener_lifecycle_requirement(self) -> None:
        payload = checker.make_fixture()
        payload["secondHostAcceptanceCriteria"]["requiresListenerLifecycleReceipt"] = False

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_missing_live_readiness_preflight_next_evidence(self) -> None:
        payload = checker.make_fixture()
        payload["requiredNextEvidence"] = [
            row for row in payload["requiredNextEvidence"] if row["id"] != "host-live-run-readiness-preflight"
        ]

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)

    def test_rejects_missing_sanitized_interface_evidence(self) -> None:
        payload = checker.make_fixture()
        payload["secondHostAcceptanceCriteria"]["requiresSanitizedHostAndClientInterfaceEvidence"] = False

        with self.assertRaises(checker.SecondHostReadinessError):
            checker.validate_contract(payload)


if __name__ == "__main__":
    unittest.main()
