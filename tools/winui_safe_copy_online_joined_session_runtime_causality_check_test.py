#!/usr/bin/env python3
"""Focused tests for the joined-session runtime-causality checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_joined_session_runtime_causality_bundle as builder
import winui_safe_copy_online_joined_session_runtime_causality_check as checker


class JoinedSessionRuntimeCausalityCheckerTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        return checker.make_fixture(root)

    def test_accepts_builder_fixture(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertTrue(summary["joinedSessionRuntimeCausalityProven"])
            self.assertEqual(summary["newBeaLaunchCount"], 1)
            self.assertEqual(summary["cdbAttachCount"], 1)
            self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["publicMatchmakingProof"])

    def test_rejects_online_ready_claim(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["baseOnlineMultiplayerReady"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_p3_p4_runtime_claim(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeEvidence"]["activeP3P4OriginalBinaryGameplayProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_direct_joined_client_input_claim(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeEvidence"]["gameInputSentByJoinedSessionClient"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_native_netcode_and_public_server_claims(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["nativeBeaNetcodeProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["publicServerProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_visible_delta_and_ticket_fingerprint_overclaims(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeEvidence"]["visibleMovementDeltaClaim"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["joinedSessionCausality"]["acceptedJoinTicketFingerprint"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_missing_fresh_launch(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeEvidence"]["newBeaLaunchCount"] = 0
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_absolute_source_reference(self) -> None:
        builder.PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["sourceArtifacts"]["secureRuntimeExecutorProof"] = str((Path(tmp) / "absolute.json").resolve())
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeCausalityError):
                checker.validate_bundle(path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()
