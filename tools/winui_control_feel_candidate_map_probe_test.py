#!/usr/bin/env python3
"""Tests for the control-feel candidate map probe."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "roadmap" / "original-binary-control-feel-candidate-map.v1.json"
PROBE_PATH = ROOT / "tools" / "winui_control_feel_candidate_map_probe.py"


class ControlFeelCandidateMapProbeTests(unittest.TestCase):
    def test_candidate_map_has_required_boundaries_and_next_rung(self) -> None:
        self.assertTrue(MAP_PATH.is_file(), "candidate map JSON is missing")
        payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "original-binary-control-feel-candidate-map.v1")
        self.assertEqual(payload["scope"], "copied-profile original-binary control-feel candidates")
        self.assertFalse(payload["visiblePatchRowAdded"])
        self.assertFalse(payload["improvedControlFeelProof"])
        self.assertFalse(payload["physicalGamepadProof"])
        self.assertEqual(payload["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
        self.assertEqual(payload["metadataOnlySlots"], ["P3", "P4"])
        risk_levels = {row["risk"] for row in payload["riskModel"]}
        self.assertGreaterEqual(risk_levels, {"highest", "high", "medium-high", "lower"})

        candidates = {row["id"]: row for row in payload["candidates"]}
        self.assertEqual(len(candidates), 6)
        for required in (
            "copied_defaultoptions_mouse_sensitivity",
            "copied_defaultoptions_controller_config",
            "platform_input_directinput_deadzone_0x96",
            "controller_mapping_engine",
            "mouse_look_angle_update",
            "player_receive_button_action_observer",
        ):
            self.assertIn(required, candidates)

        self.assertEqual(candidates["platform_input_directinput_deadzone_0x96"]["classification"], "file_backed_static_candidate_runtime_blocked")
        self.assertEqual(candidates["mouse_look_angle_update"]["classification"], "needs_runtime_trace")
        deadzone_text = json.dumps(candidates["platform_input_directinput_deadzone_0x96"], sort_keys=True).lower()
        self.assertIn("0x00513167", deadzone_text)
        self.assertIn("0x113167", deadzone_text)
        self.assertIn("0x11316d", deadzone_text)
        self.assertIn("file-backed", deadzone_text)
        self.assertIn("runtime blocked", deadzone_text)
        self.assertIn("physical gamepad", deadzone_text)
        self.assertIn("not patchable yet", deadzone_text)

        self.assertEqual(payload["recommendedNextRung"]["id"], "directinput-deadzone-runtime-a-b-proof")
        self.assertFalse(payload["recommendedNextRung"]["addsPatchRow"])

    def test_probe_self_test_and_check_pass(self) -> None:
        self.assertTrue(PROBE_PATH.is_file(), "candidate map probe is missing")
        for args in (["--self-test"], ["--check"]):
            result = subprocess.run(
                [sys.executable, str(PROBE_PATH), *args],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
