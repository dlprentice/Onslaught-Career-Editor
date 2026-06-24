#!/usr/bin/env python3
"""Tests for the safe-copy control-feel telemetry bundle checker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import winui_control_feel_telemetry_bundle_check as checker


class ControlFeelTelemetryBundleCheckerTests(unittest.TestCase):
    def test_self_test_accepts_bundle_and_rejects_no_input_overclaim(self) -> None:
        checker.run_self_test()

    def test_rejects_reused_baseline_as_repeat(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assignments = {}
            process_id = 3000
            for scenario in checker.matrix.SCENARIOS:
                process_id += 1
                assignments[scenario.scenario_id] = checker.make_artifact(
                    root / scenario.scenario_id,
                    scenario,
                    process_id=process_id,
                )
            no_input = checker.make_no_input_artifact(root / "no_input")

            with self.assertRaises(checker.TelemetryBundleError):
                checker.validate_bundle(
                    assignments,
                    repeat_baseline=assignments["baseline_config1"],
                    no_input_control=no_input,
                    require_visual=True,
                    require_files=True,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
