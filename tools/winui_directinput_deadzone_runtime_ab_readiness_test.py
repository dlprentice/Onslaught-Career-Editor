#!/usr/bin/env python3
"""Tests for the DirectInput deadzone runtime A/B readiness checker."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "winui_directinput_deadzone_runtime_ab_readiness.py"


class DirectInputDeadzoneRuntimeAbReadinessTests(unittest.TestCase):
    def test_checker_self_test_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gamepad_artifact_mode_accepts_blocked_preflight_without_runtime_proof(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "gamepad-readiness.json"
            artifact.write_text(
                json.dumps(
                    {
                        "schemaVersion": "winui-safe-copy-local-multiplayer-gamepad-readiness.v1",
                        "status": "blocked_no_present_gamepad",
                        "physicalGamepadRuntimeProofReady": False,
                        "presentGamepadCandidateCount": 0,
                        "registryGamepadCandidateCount": 0,
                        "claimBoundary": "Hardware presence is a precondition, not BEA runtime proof.",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(CHECKER), "--gamepad-artifact", str(artifact)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "blocked_no_present_gamepad")
            self.assertFalse(payload["physicalGamepadRuntimeProofReady"])

    def test_gamepad_artifact_mode_rejects_runtime_proof_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "gamepad-readiness.json"
            artifact.write_text(
                json.dumps(
                    {
                        "schemaVersion": "winui-safe-copy-local-multiplayer-gamepad-readiness.v1",
                        "status": "ready_for_physical_gamepad_runtime_attempt",
                        "physicalGamepadRuntimeProofReady": True,
                        "presentGamepadCandidateCount": 1,
                        "registryGamepadCandidateCount": 1,
                        "claimBoundary": "Hardware presence is a precondition.",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(CHECKER), "--gamepad-artifact", str(artifact)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("must not be treated as runtime proof", result.stdout)


if __name__ == "__main__":
    unittest.main()
