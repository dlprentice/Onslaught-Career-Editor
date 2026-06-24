#!/usr/bin/env python3
"""Tests for second-host runtime promotion guard."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_second_host_runtime_executor_bundle as executor_builder
import winui_safe_copy_online_second_host_runtime_promotion_guard as guard


class SecondHostRuntimePromotionGuardTests(unittest.TestCase):
    def test_rejects_synthetic_future_fixture_in_default_live_mode(self) -> None:
        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(guard.make_future_candidate_fixture())

    def test_accepts_future_source_bound_causality_fixture_when_explicitly_allowed(self) -> None:
        summary = guard.validate_promotion_candidate(
            guard.make_future_candidate_fixture(),
            allow_synthetic_fixture=True,
        )

        self.assertTrue(summary["shapePreflightAccepted"])
        self.assertNotIn("runtimeDrivenBySecondHostCommandSource", summary)
        self.assertNotIn("acceptedLiveSecondHostRuntimeDeliveryProof", summary)
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])

    def test_rejects_current_compatibility_executor_fixture(self) -> None:
        with tempfile.TemporaryDirectory(dir=executor_builder.PRIVATE_PROOF_ROOT) as raw_tmp:
            payload = guard.make_current_compatibility_executor_fixture(Path(raw_tmp))

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload)

    def test_rejects_missing_synthetic_fixture_marker_in_fixture_mode(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["sourceBoundRuntimeCausalityReceipt"]["fixtureOrPosthocBinding"] = False

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_missing_second_host_driven_runtime_flag(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["secondHostRuntimeExecutor"]["runtimeDrivenBySecondHostCommandSource"] = False

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_missing_runtime_input_window_payload_binding(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["sourceBoundRuntimeCausalityReceipt"]["runtimeInputWindowReceipt"][
            "acceptedSecondHostCommandRequestPayloadSha256"
        ] = "b" * 64

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_missing_invitation_lifecycle_binding(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["sourceBoundRuntimeCausalityReceipt"]["bridgeReceipt"][
            "secondHostInvitationLifecycleSha256"
        ] = "c" * 64

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_missing_exact_pid_cdb_receipt(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["sourceBoundRuntimeCausalityReceipt"]["exactPidCdbReceipt"]["present"] = False

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_missing_mapped_p2_sequence_receipt(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["sourceBoundRuntimeCausalityReceipt"].pop("mappedP2SequenceReceipt", None)

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_second_host_client_direct_game_input_bypass(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["runtimeEvidence"]["gameInputSentBySecondHostClient"] = True

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)

    def test_rejects_wrong_host_helper_mapped_p2_sequence(self) -> None:
        payload = guard.make_future_candidate_fixture()
        payload["runtimeEvidence"]["hostHelperMappedInputSequence"] = "down:Q,wait:500,up:Q"

        with self.assertRaises(guard.SecondHostRuntimePromotionGuardError):
            guard.validate_promotion_candidate(payload, allow_synthetic_fixture=True)


if __name__ == "__main__":
    unittest.main()
