#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_cround_handle_event_arm_effects.py"
SPEC = importlib.util.spec_from_file_location("re_cround_handle_event_arm_effects", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class CRoundHandleEventArmEffectsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.campaign = ROOT / owner.CAMPAIGN_RELATIVE
        cls.evidence = ROOT / owner.EVIDENCE_RELATIVE

    def test_selftest_refuses_scope_and_grade_overclaims(self) -> None:
        result = owner.selftest(ROOT, self.campaign)
        self.assertEqual(4, result["count"])
        self.assertEqual(
            {
                "universal-event4000",
                "external-write-overclaim",
                "gapfree-overclaim",
                "rebuild-ready-overclaim",
            },
            set(result["attacks"]),
        )

    def test_exact_write_lanes_rederive_counts_and_grades(self) -> None:
        results = {
            key: owner.validate_write_lane(self.evidence, key, spec)
            for key, spec in owner.WRITE_SPECS.items()
        }
        self.assertEqual(
            43,
            sum(results[key]["pairCount"] for key in (
                "default3000ShardA", "default3000ShardB", "default3000ShardC"
            )),
        )
        self.assertEqual(4, results["event4003"]["pairCount"])
        self.assertEqual(9, results["event4001"]["pairCount"])
        self.assertEqual(12, results["event4000Level521"]["pairCount"])
        self.assertEqual(16, results["event4000Level512"]["pairCount"])
        self.assertTrue(results["event4003"]["grade"].startswith("GAP_FREE"))
        self.assertTrue(results["event4001"]["grade"].startswith("WITNESSED"))

    def test_event4000_preserves_cross_session_divergence(self) -> None:
        level521 = owner.validate_write_lane(
            self.evidence, "event4000Level521", owner.WRITE_SPECS["event4000Level521"]
        )
        level512 = owner.validate_write_lane(
            self.evidence, "event4000Level512", owner.WRITE_SPECS["event4000Level512"]
        )
        self.assertEqual(owner.EXPECTED_BOUNDARY["event4000CommonReceiverOffsets"], level521["receiverOffsets"])
        self.assertEqual(level521["receiverOffsets"], level512["receiverOffsets"])
        self.assertNotEqual(level521["sequenceSha256"], level512["sequenceSha256"])
        self.assertEqual(3, len(level521["writerBodyRanges"]))
        self.assertEqual(6, len(level512["writerBodyRanges"]))

    def test_rejected_controls_contribute_no_positive_evidence(self) -> None:
        result = owner.validate_rejected_controls(self.evidence)
        self.assertEqual(4, result["count"])
        self.assertTrue(all(not row["accepted"] for row in result["controls"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
