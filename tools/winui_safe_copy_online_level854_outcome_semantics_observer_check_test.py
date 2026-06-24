#!/usr/bin/env python3
"""Focused tests for the level-854 multiplayer outcome-semantics observer checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_level854_outcome_semantics_observer_bundle as builder
import winui_safe_copy_online_level854_outcome_semantics_observer_check as checker


class Level854OutcomeSemanticsObserverCheckerTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        return checker.make_fixture(root)

    def test_accepts_builder_fixture(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertEqual(summary["renderPlayers"], 2)
            self.assertEqual(summary["renderLevel"], 854)
            self.assertTrue(summary["outcomeObserverSurfaceProven"])
            self.assertEqual(summary["selectedRuntimeCandidate"], 854)
            self.assertEqual(summary["outcomeHookTargetCount"], len(builder.OUTCOME_TARGETS))
            self.assertFalse(summary["naturalOutcomeTransitionObserved"])
            self.assertFalse(summary["runtimeOutcomeProof"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["activeP3P4OriginalBinaryGameplayProof"])

    def test_live_command_focuses_window_before_visual_capture(self) -> None:
        command = builder.live_smoke_command(
            Path("artifact-root"),
            exe_override=Path(r"C:\game\BEA.exe.original.backup"),
        )

        self.assertIn("--input-sequence", command)
        input_index = command.index("--input-sequence")
        self.assertEqual(command[input_index + 1], "wait:1")
        capture_index = command.index("--capture-count")
        self.assertLess(input_index, capture_index)

    def test_rejects_wrong_level_or_candidate(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtimeEvidence"]["safeCopyLaunchLevel"] = 850
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level854OutcomeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = self.build_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["outcomeSemanticsSurface"]["selectedRuntimeCandidate"] = 851
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.Level854OutcomeSemanticsObserverError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_online_native_netcode_or_p3p4_claims(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for section, key in (
            ("nonClaims", "baseOnlineMultiplayerReady"),
            ("nonClaims", "nativeBeaNetcodeProof"),
            ("slotBoundary", "activeP3P4OriginalBinaryGameplayProof"),
        ):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                path = self.build_fixture(Path(tmp))
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload[section][key] = True
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(checker.Level854OutcomeSemanticsObserverError):
                    checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_forced_or_mode_overclaim(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for key, value in (
            ("forcedOutcomeTransition", True),
            ("naturalOutcomeTransitionObserved", True),
            ("runtimeOutcomeProof", True),
            ("modeRuntimeProofSlicesAdded", 1),
            ("coOpVersusModeRuntimeProofSlicesAdded", 1),
        ):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                path = self.build_fixture(Path(tmp))
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["outcomeSemanticsSurface"][key] = value
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(checker.Level854OutcomeSemanticsObserverError):
                    checker.validate_bundle(path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()
