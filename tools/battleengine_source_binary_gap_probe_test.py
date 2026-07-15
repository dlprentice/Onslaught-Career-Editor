#!/usr/bin/env python3
"""Regression tests for current BattleEngine source/binary gap accounting."""

from __future__ import annotations

import unittest

import battleengine_source_binary_gap_probe as probe


class BattleEngineSourceBinaryGapProbeTests(unittest.TestCase):
    def test_default_output_is_ignored_local_lab(self) -> None:
        relative = probe.DEFAULT_OUT.resolve().relative_to(probe.ROOT.resolve()).as_posix()
        self.assertTrue(relative.startswith("local-lab/"))

    def test_target_lock_root_identity_is_current(self) -> None:
        report = probe.build_report()
        self.assertEqual(report["status"], "pass")
        target = next(
            item
            for item in report["partialRetailCandidates"]
            if item["key"] == "target_lock_modes_and_stealth_range"
        )
        self.assertEqual(
            target["status"],
            "RETAIL_STATIC_ROOT_IDENTITY_ACCEPTED_DEPENDENT_HYPOTHESES_PENDING",
        )
        self.assertIn("CBattleEngine__HandleLocks retail-static root identity is accepted", target["summary"])
        self.assertNotIn("exact HandleLocks control-flow identity remains unresolved", target["summary"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
