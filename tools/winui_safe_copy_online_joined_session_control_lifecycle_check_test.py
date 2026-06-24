#!/usr/bin/env python3
"""Unit tests for the joined-session control-lifecycle checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_joined_session_control_lifecycle_check as checker


class JoinedSessionControlLifecycleCheckerTests(unittest.TestCase):
    def load_contract(self) -> dict:
        return checker.read_json(checker.CONTRACT)

    def assert_rejects(self, mutate) -> None:
        value = self.load_contract()
        mutate(value)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.json"
            checker.write_json(path, value)
            with self.assertRaises(checker.JoinedSessionControlLifecycleError):
                checker.validate_contract(path)

    def test_accepts_current_contract(self) -> None:
        summary = checker.validate_contract(checker.CONTRACT)
        self.assertEqual(summary["schemaVersion"], checker.EXPECTED_SCHEMA)
        self.assertTrue(summary["sessionControlLifecycleProven"])
        self.assertFalse(summary["baseOnlineMultiplayerReady"])

    def test_rejects_base_online_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("baseOnlineMultiplayerReady", True))

    def test_rejects_new_runtime_launch_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("newBeaLaunchCount", 1))

    def test_rejects_p3_gameplay_slot_acceptance(self) -> None:
        self.assert_rejects(
            lambda value: value["proofBoundary"].__setitem__(
                "acceptedOriginalBinaryGameplaySlots",
                ["P1", "P2", "P3"],
            )
        )

    def test_rejects_direct_session_control_game_input(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("gameInputSentBySessionControl", True))

    def test_rejects_weakened_reconnect_boundary(self) -> None:
        self.assert_rejects(
            lambda value: value["controlLifecycle"].__setitem__(
                "reconnectProofScope",
                "runtime-reconnect-proven",
            )
        )

    def test_rejects_public_bind(self) -> None:
        self.assert_rejects(lambda value: value["controlSecurity"].__setitem__("publicBind", True))

    def test_rejects_public_socket(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("publicNetworkSocketsOpened", True))

    def test_rejects_second_physical_host_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("secondPhysicalHostProof", True))

    def test_rejects_multi_host_lan_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("multiHostLanProof", True))

    def test_rejects_public_matchmaking_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("publicMatchmakingProof", True))

    def test_rejects_native_netcode_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["proofBoundary"].__setitem__("nativeBeaNetcodeProof", True))

    def test_rejects_coop_mode_runtime_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["nonClaims"].__setitem__("coOpModeRuntimeProof", True))

    def test_rejects_versus_mode_runtime_overclaim(self) -> None:
        self.assert_rejects(lambda value: value["nonClaims"].__setitem__("versusModeRuntimeProof", True))

    def test_rejects_missing_replay_guard(self) -> None:
        self.assert_rejects(lambda value: value["controlSecurity"].__setitem__("ticketReplayRejectionProof", False))

    def test_rejects_accepted_rejection_case(self) -> None:
        self.assert_rejects(lambda value: value["rejectedControlCases"][0].__setitem__("accepted", True))

    def test_rejects_missing_nonclaim_key(self) -> None:
        self.assert_rejects(lambda value: value["nonClaims"].pop("nativeBeaNetcodeProof", None))

    def test_rejects_wrong_package_scope(self) -> None:
        self.assert_rejects(
            lambda value: value["proofBoundary"].__setitem__(
                "sessionControlScope",
                "joined-session-control-lifecycle-online-play-ready",
            )
        )

    def test_rejects_status_overclaim(self) -> None:
        self.assert_rejects(lambda value: value.__setitem__("status", "true online multiplayer proof accepted"))

    def test_rejects_collapsed_rejection_case_map(self) -> None:
        def mutate(value: dict) -> None:
            value["rejectedControlCases"][5]["caseId"] = "p3-gameplay-activation"

        self.assert_rejects(mutate)

    def test_rejects_wrong_same_host_session_control_scope(self) -> None:
        self.assert_rejects(
            lambda value: value["proofBoundary"].__setitem__(
                "sameHostSessionControlScope",
                "joined-session-same-host-session-control-online-play-ready",
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
