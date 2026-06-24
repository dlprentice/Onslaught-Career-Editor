#!/usr/bin/env python3
"""Tests for original-binary Host/Join enablement gate validation."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_host_join_enablement_check as checker
import winui_safe_copy_online_second_host_runtime_causality_check as causality_checker


class HostJoinEnablementCheckTests(unittest.TestCase):
    def test_accepts_disabled_composite_enablement_contract_fixture(self) -> None:
        payload = checker.make_fixture()

        summary = checker.validate_contract(payload)

        self.assertEqual(summary["schemaVersion"], "winui-original-binary-host-join-enablement.v1")
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
        self.assertFalse(summary["baseOnlineMultiplayerReady"])
        self.assertEqual(summary["requiredProofs"][0], "distinct-private-host-command-source-proof")
        self.assertEqual(summary["requiredProofs"][1], "host-runtime-delivery-from-source-bound-distinct-command-source")
        self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
        self.assertEqual(summary["metadataOnlySlots"], ["P3", "P4"])

    def test_rejects_host_join_enabled_before_composite_runtime_proof(self) -> None:
        payload = checker.make_fixture()
        payload["currentEvidence"]["hostJoinControlsMayBeEnabled"] = True

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_contract(payload)

    def test_rejects_command_source_only_enablement_requirement(self) -> None:
        payload = checker.make_fixture()
        payload["blockedActions"][0]["requires"] = "distinct-private-host-command-source-proof"

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_contract(payload)

    def test_rejects_missing_direct_runtime_causality_requirement(self) -> None:
        payload = checker.make_fixture()
        payload["requiredProofs"] = [
            row for row in payload["requiredProofs"] if row["id"] != "host-runtime-delivery-from-source-bound-distinct-command-source"
        ]

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_contract(payload)

    def test_rejects_fixture_or_posthoc_runtime_mode(self) -> None:
        payload = checker.make_fixture()
        payload["livePromotionRequirements"]["rejectsFixtureOrPosthocRuntimeBinding"] = False

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_contract(payload)

    def test_rejects_missing_runtime_promotion_guard_requirement(self) -> None:
        payload = checker.make_fixture()
        payload["livePromotionRequirements"]["requiresSecondHostRuntimePromotionGuard"] = False

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_contract(payload)

    def test_rejects_readiness_contract_that_uses_command_source_only_for_host_join(self) -> None:
        readiness = checker.make_readiness_fixture()
        readiness["blockedActions"][0]["requires"] = "distinct-private-host-command-source-proof"

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_readiness_contract(readiness)

    def test_repo_validation_requires_all_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checker.write_json(root / "enablement.json", checker.make_fixture())
            checker.write_json(root / "readiness.json", checker.make_readiness_fixture())
            summary = checker.validate_repo_contracts(
                enablement_path=root / "enablement.json",
                readiness_path=root / "readiness.json",
                command_source_path=None,
                runtime_executor_path=None,
            )

        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
        self.assertEqual(summary["requiredProofCount"], 2)

    def test_repo_validation_requires_runtime_causality_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checker.write_json(root / "enablement.json", checker.make_fixture())
            checker.write_json(root / "readiness.json", checker.make_readiness_fixture())
            checker.write_json(root / "causality.json", causality_checker.make_contract_fixture())
            summary = checker.validate_repo_contracts(
                enablement_path=root / "enablement.json",
                readiness_path=root / "readiness.json",
                command_source_path=None,
                runtime_executor_path=None,
                runtime_causality_path=root / "causality.json",
            )

        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])

    def test_repo_validation_rejects_missing_runtime_causality_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checker.write_json(root / "enablement.json", checker.make_fixture())
            checker.write_json(root / "readiness.json", checker.make_readiness_fixture())

            with self.assertRaises(checker.HostJoinEnablementError):
                checker.validate_repo_contracts(
                    enablement_path=root / "enablement.json",
                    readiness_path=root / "readiness.json",
                    command_source_path=None,
                    runtime_executor_path=None,
                    runtime_causality_path=root / "missing-causality.json",
                )

    def test_rejects_runtime_nonclaim_overclaim(self) -> None:
        payload = copy.deepcopy(checker.make_fixture())
        payload["nonClaims"]["nativeBeaNetcodeProof"] = True

        with self.assertRaises(checker.HostJoinEnablementError):
            checker.validate_contract(payload)

    def test_rejects_missing_current_evidence_or_nonclaim_keys(self) -> None:
        for section, key in (
            ("currentEvidence", "runtimeDrivenBySecondHostCommandSource"),
            ("nonClaims", "nativeBeaNetcodeProof"),
        ):
            payload = copy.deepcopy(checker.make_fixture())
            del payload[section][key]

            with self.assertRaises(checker.HostJoinEnablementError, msg=f"{section}.{key}"):
                checker.validate_contract(payload)


if __name__ == "__main__":
    unittest.main()
