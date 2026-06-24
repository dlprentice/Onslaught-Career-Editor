#!/usr/bin/env python3
"""Tests for the dual-safe-copy topology contract checker."""

from __future__ import annotations

import copy
import unittest

import winui_safe_copy_online_dual_safe_copy_topology_check as checker


class DualSafeCopyTopologyCheckerTests(unittest.TestCase):
    def test_accepts_public_safe_same_workstation_dual_safe_copy_fixture(self) -> None:
        summary = checker.validate_contract(checker.make_fixture())

        self.assertEqual(summary["schemaVersion"], checker.SCHEMA)
        self.assertEqual(summary["safeCopyCount"], 2)
        self.assertEqual(summary["roles"], ["host", "joiner"])
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
        self.assertFalse(summary["baseOnlineMultiplayerReady"])
        self.assertEqual(summary["beaLaunchCount"], 0)
        self.assertEqual(summary["cdbAttachCount"], 0)

    def test_rejects_host_join_enablement_overclaim(self) -> None:
        payload = checker.make_fixture()
        payload["proofBoundary"]["hostJoinControlsMayBeEnabled"] = True

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)

    def test_rejects_single_root_for_both_safe_copies(self) -> None:
        payload = checker.make_fixture()
        payload["safeCopies"][1]["safeCopyRootLabel"] = payload["safeCopies"][0]["safeCopyRootLabel"]

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)

    def test_rejects_private_or_absolute_path_leakage(self) -> None:
        payload = checker.make_fixture()
        payload["safeCopies"][0]["safeCopyRootLabel"] = r"C:\Users\david\AppData\Local\OnslaughtCareerEditor\host"

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)

    def test_rejects_runtime_or_network_side_effect_claims(self) -> None:
        for key, value in (
            ("beaLaunchCount", 1),
            ("cdbAttachCount", 1),
            ("listenerOpened", True),
            ("invitationCreated", True),
            ("inputSent", True),
        ):
            with self.subTest(key=key):
                payload = checker.make_fixture()
                payload["sideEffects"][key] = value
                with self.assertRaises(checker.DualSafeCopyTopologyError):
                    checker.validate_contract(payload)

    def test_rejects_truthy_non_claims(self) -> None:
        payload = checker.make_fixture()
        payload["nonClaims"]["multiHostLanPlayProof"] = True

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)

    def test_rejects_missing_future_evidence_gate(self) -> None:
        payload = checker.make_fixture()
        payload["requiredFutureEvidence"] = [
            row
            for row in payload["requiredFutureEvidence"]
            if row["id"] != checker.SOURCE_BOUND_RUNTIME_CAUSALITY_ID
        ]

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)

    def test_rejects_secret_like_keys_anywhere(self) -> None:
        payload = checker.make_fixture()
        payload["safeCopies"][0]["token"] = "not-allowed"

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)

    def test_rejects_mutated_copy_policy(self) -> None:
        payload = checker.make_fixture()
        host_row = copy.deepcopy(payload["safeCopies"][0])
        host_row["installedGameMutationAllowed"] = True
        payload["safeCopies"][0] = host_row

        with self.assertRaises(checker.DualSafeCopyTopologyError):
            checker.validate_contract(payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
