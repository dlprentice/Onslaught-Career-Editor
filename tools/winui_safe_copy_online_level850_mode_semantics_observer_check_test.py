#!/usr/bin/env python3
"""Focused tests for the level-850 mode-semantics observer checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_level850_mode_semantics_observer_bundle as builder
import winui_safe_copy_online_level850_mode_semantics_observer_check as checker


class Level850ModeSemanticsObserverCheckerTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        return checker.make_fixture(root)

    def test_accepts_builder_fixture(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertEqual(summary["renderPlayers"], 2)
            self.assertEqual(summary["renderLevel"], 850)
            self.assertEqual(summary["hookTargetCount"], len(builder.TARGETS))
            self.assertFalse(summary["baseOnlineMultiplayerReady"])

    def test_rejects_online_ready_and_native_netcode_claims(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["baseOnlineMultiplayerReady"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level850ModeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["nativeBeaNetcodeProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level850ModeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_mode_or_transition_overclaim(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["modeSemanticsSurface"]["modeRuntimeProofSlicesAdded"] = 1
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level850ModeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["modeSemanticsSurface"]["forcedWinDeathRespawn"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level850ModeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_p3p4_or_render_overclaim(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["slotBoundary"]["activeP3P4OriginalBinaryGameplayProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level850ModeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeEvidence"]["renderPlayers"] = 4
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level850ModeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()
