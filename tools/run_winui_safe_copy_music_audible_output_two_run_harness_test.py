#!/usr/bin/env python3
"""Tests for the public-safe two-run music audible-output harness plan builder."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import run_winui_safe_copy_music_audible_output_two_run_harness as harness


class MusicAudibleOutputTwoRunHarnessPlanTests(unittest.TestCase):
    def test_plan_contains_required_fail_closed_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = harness.build_plan(Path(temp_dir) / "music-audible")

        self.assertEqual("winui-safe-copy-music-audible-output-two-run-plan.v1", plan["schemaVersion"])
        self.assertFalse(plan["runtimeAudibleOutputProof"])
        self.assertEqual("use-bea02-for-bea04", plan["presetId"])
        self.assertEqual(100, plan["levelId"])
        self.assertEqual(
            ["ambientNoBea", "cleanBaseline", "stagedPositive", "muteControl"],
            [stage["role"] for stage in plan["stages"]],
        )
        positive = next(stage for stage in plan["stages"] if stage["role"] == "stagedPositive")
        self.assertIn("--music-swap-preset-id", positive["liveSmokeCommand"])
        self.assertIn("use-bea02-for-bea04", positive["liveSmokeCommand"])
        self.assertNotIn("--play-calibration-tone", " ".join(positive["audioCommand"]))
        mute = next(stage for stage in plan["stages"] if stage["role"] == "muteControl")
        self.assertIn("--launch-nomusic", mute["liveSmokeCommand"])
        self.assertNotIn("<requires-mute-launch-arg-support>", mute["liveSmokeCommand"])
        self.assertEqual(
            r"tools\winui_safe_copy_music_audible_output_materializer.py",
            plan["acceptedProofMaterializer"],
        )
        self.assertEqual(
            r"tools\winui_safe_copy_music_audible_output_two_run_harness_check.py",
            plan["acceptedProofShapeChecker"],
        )

    def test_plan_records_unresolved_live_acceptance_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = harness.build_plan(Path(temp_dir) / "music-audible")

        blockers = set(plan["blockedUntil"])
        self.assertIn("live raw artifacts exist and pass the materializer plus final checker", blockers)
        self.assertNotIn("source-audio fingerprint/correlation helper exists", blockers)
        self.assertIn("live capture-to-source correlation adapter artifact exists and passes the adapter checker", blockers)
        self.assertIn("mute-control runtime path is captured with -nomusic or -nosound", blockers)


if __name__ == "__main__":
    unittest.main()
