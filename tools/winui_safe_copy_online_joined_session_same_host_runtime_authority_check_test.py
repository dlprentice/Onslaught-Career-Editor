#!/usr/bin/env python3
"""Focused tests for the joined-session same-host runtime-authority checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_joined_session_same_host_runtime_authority_check as checker


class JoinedSessionRuntimeAuthorityCheckerTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        return checker.make_fixture(root)

    def test_accepts_builder_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            summary = checker.validate_bundle(path)
            self.assertTrue(summary["joinedSessionSameHostRuntimeAuthorityChainProven"])
            self.assertTrue(summary["joinTicketRuntimeRelayHashMatched"])
            self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
            self.assertFalse(summary["publicMatchmakingProof"])
            self.assertFalse(summary["joinedSessionVisibleMovementCausalityProof"])

    def test_rejects_public_matchmaking_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["publicMatchmakingProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeAuthorityError):
                checker.validate_bundle(path)

    def test_rejects_p3_p4_runtime_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["counts"]["activeP3P4OriginalBinaryGameplayProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeAuthorityError):
                checker.validate_bundle(path)

    def test_rejects_joined_visible_causality_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeAuthority"]["joinedSessionVisibleMovementCausalityProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeAuthorityError):
                checker.validate_bundle(path)

    def test_rejects_wrapper_launch_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["counts"]["wrapperNewBeaLaunchCount"] = 1
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeAuthorityError):
                checker.validate_bundle(path)

    def test_rejects_fake_ticket_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["joinedSession"]["acceptedJoinTicketFingerprint"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeAuthorityError):
                checker.validate_bundle(path)

    def test_rejects_absolute_source_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["sourceArtifacts"]["sessionDirectoryProof"] = str((Path(tmp) / "absolute.json").resolve())
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.JoinedSessionRuntimeAuthorityError):
                checker.validate_bundle(path)


if __name__ == "__main__":
    unittest.main()
