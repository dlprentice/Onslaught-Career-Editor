#!/usr/bin/env python3
"""Regression tests for the current targeting source/read-back bridge."""

from __future__ import annotations

import unittest
from unittest import mock

import battleengine_targeting_source_readback_bridge_probe as probe


class BattleEngineTargetingSourceReadbackBridgeProbeTests(unittest.TestCase):
    def test_current_repo_bridge_passes_six_current_authority_checks(self) -> None:
        report = probe.build_report()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["checksPassed"], 6)
        self.assertEqual(report["checksTotal"], 6)
        self.assertIn("CBattleEngine__HandleLocks", " ".join(report["whatIsProven"]))
        self.assertNotIn("projectile helper", " ".join(report["whatIsProven"]).lower())

    def test_default_output_is_ignored_local_lab(self) -> None:
        relative = probe.DEFAULT_OUT.resolve().relative_to(probe.ROOT.resolve()).as_posix()
        self.assertTrue(relative.startswith("local-lab/"))

    def test_standalone_bridge_rejects_wrong_initialized_source_revision(self) -> None:
        with mock.patch.object(probe.static_contract, "_source_revision", return_value="0" * 40):
            report = probe.build_report()
        self.assertEqual(report["status"], "blocked")
        source_result = next(
            item for item in report["results"] if item["key"] == "source_target_lock_anchor"
        )
        self.assertEqual(source_result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
