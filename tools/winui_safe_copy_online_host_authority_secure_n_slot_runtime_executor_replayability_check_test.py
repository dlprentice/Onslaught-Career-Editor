#!/usr/bin/env python3
"""Tests for secure N-slot runtime executor replayability checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check as checker


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for child in value.values():
            strings.extend(flatten_strings(child))
        return strings
    if isinstance(value, list):
        strings = []
        for child in value:
            strings.extend(flatten_strings(child))
        return strings
    return []


class SecureNSlotRuntimeExecutorReplayabilityCheckerTests(unittest.TestCase):
    def test_accepts_distinct_fixture_pair(self) -> None:
        root = checker.executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            base = Path(tmp)
            session_path = base / "shared-session" / "host-authority-n-slot-session-security-smoke-proof.json"
            checker.executor.security_builder.build_bundle(session_path)
            summary = checker.validate_replayability(
                [
                    checker.make_executor_fixture(base / "first", session_path=session_path),
                    checker.make_executor_fixture(base / "second", distinct=True, session_path=session_path),
                ],
                allow_fixture=True,
            )

            self.assertEqual(summary["schemaVersion"], checker.EXPECTED_SCHEMA)
            self.assertEqual(summary["proofCount"], 2)
            self.assertFalse(summary["secureNSlotRuntimeExecutorReplayabilityProven"])
            self.assertFalse(summary["liveReplayabilityProof"])
            self.assertTrue(summary["selfTestFixtureOnly"])
            self.assertTrue(summary["sessionSecurityProofSha256"])
            self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
        self.assertEqual(summary["metadataOnlySlots"], ["P3", "P4"])
        self.assertEqual(summary["secureSessionAcceptedCommandCount"], 2)
        self.assertEqual(
            summary["secureSessionSecurityRejectionCount"],
            len(checker.executor.security.EXPECTED_SECURITY_REJECTION_CASES),
        )
        self.assertTrue(summary["hostHelperInputSent"])
        self.assertFalse(summary["gameInputSentByNSlotScheduler"])
        self.assertEqual(summary["nPlayerOriginalBinaryRuntimeProof"], 0)
        self.assertFalse(summary["activeP3P4OriginalBinaryGameplayProof"])
        self.assertFalse(summary["visibleMovementDeltaClaim"])
        self.assertTrue(summary["distinctLiveRuntimeArtifactHashes"])
        self.assertTrue(summary["distinctProcessIds"])
        self.assertTrue(summary["distinctCdbLogs"])
        self.assertFalse(summary["absolutePrivatePathPublished"])
        self.assertFalse(summary["rawPrivateProofPathPublished"])
        self.assertFalse(summary["rawPrivateArtifactContentPublished"])
        self.assertFalse(summary["releaseIncludedPrivateArtifact"])
        output_strings = flatten_strings(summary)
        self.assertFalse(any(str(root).lower() in text.lower() for text in output_strings))
        self.assertFalse(any("subagents/" in text.replace("\\", "/") for text in output_strings))
        self.assertFalse(any("C:\\Users\\" in text for text in output_strings))

    def test_rejects_fixture_pair_by_default(self) -> None:
        root = checker.executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            base = Path(tmp)
            session_path = base / "shared-session" / "host-authority-n-slot-session-security-smoke-proof.json"
            checker.executor.security_builder.build_bundle(session_path)

            with self.assertRaises(checker.executor.SecureNSlotRuntimeExecutorProofError):
                checker.validate_replayability(
                    [
                        checker.make_executor_fixture(base / "first", session_path=session_path),
                        checker.make_executor_fixture(base / "second", distinct=True, session_path=session_path),
                    ]
                )

    def test_rejects_duplicate_proof_path(self) -> None:
        root = checker.executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            proof_path = checker.make_executor_fixture(Path(tmp) / "duplicate")

            with self.assertRaises(checker.SecureNSlotRuntimeExecutorReplayabilityError):
                checker.validate_replayability([proof_path, proof_path], allow_fixture=True)

    def test_rejects_duplicate_runtime_pointer_tuple(self) -> None:
        root = checker.executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            base = Path(tmp)
            session_path = base / "shared-session" / "host-authority-n-slot-session-security-smoke-proof.json"
            checker.executor.security_builder.build_bundle(session_path)

            with self.assertRaises(checker.SecureNSlotRuntimeExecutorReplayabilityError):
                checker.validate_replayability(
                    [
                        checker.make_executor_fixture(base / "first", session_path=session_path),
                        checker.make_executor_fixture(base / "second", session_path=session_path),
                    ],
                    allow_fixture=True,
                )

    def test_rejects_visible_movement_overclaim(self) -> None:
        root = checker.executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            base = Path(tmp)
            session_path = base / "shared-session" / "host-authority-n-slot-session-security-smoke-proof.json"
            checker.executor.security_builder.build_bundle(session_path)
            first = checker.make_executor_fixture(base / "first", session_path=session_path)
            second = checker.make_executor_fixture(base / "second", distinct=True, session_path=session_path)
            proof = checker.executor.read_json(second)
            proof["execution"]["visibleMovementDeltaClaim"] = True
            checker.executor.write_json(second, proof)

            with self.assertRaises(checker.executor.SecureNSlotRuntimeExecutorProofError):
                checker.validate_replayability([first, second], allow_fixture=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
