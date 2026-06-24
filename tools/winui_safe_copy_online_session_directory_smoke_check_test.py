#!/usr/bin/env python3
"""Focused tests for the online session-directory smoke checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_online_session_directory_smoke_bundle as builder
import winui_safe_copy_online_session_directory_smoke_check as checker


class SessionDirectorySmokeCheckerTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        path = root / "online-session-directory-smoke-proof.json"
        builder.build_bundle(path)
        return path

    def test_accepts_builder_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            summary = checker.validate_bundle(path)
            self.assertEqual(summary["registeredSessionCount"], 1)
            self.assertEqual(summary["acceptedJoinTicketCount"], 1)
            self.assertFalse(summary["publicMatchmakingProof"])
            self.assertFalse(summary["nativeBeaNetcodeProof"])

    def test_rejects_public_matchmaking_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["publicMatchmakingProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.SessionDirectorySmokeError):
                checker.validate_bundle(path)

    def test_rejects_public_bind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["directory"]["publicBind"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.SessionDirectorySmokeError):
                checker.validate_bundle(path)

    def test_rejects_p3_join_ticket_as_active_gameplay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["joinTickets"]["accepted"][0]["clientSlot"] = "P3"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.SessionDirectorySmokeError):
                checker.validate_bundle(path)


if __name__ == "__main__":
    unittest.main()
