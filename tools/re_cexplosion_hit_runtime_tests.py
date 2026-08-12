#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_cexplosion_hit_runtime.py"
SPEC = importlib.util.spec_from_file_location("re_cexplosion_hit_runtime", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class CExplosionHitRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.campaign = ROOT / owner.CAMPAIGN_RELATIVE
        cls.proof = ROOT / owner.EVIDENCE_RELATIVE / "proof-v1"

    def test_selftest_refuses_carrier_and_scope_overclaims(self) -> None:
        result = owner.selftest(ROOT, self.campaign)
        self.assertEqual(6, result["count"])
        self.assertEqual(
            {"source", "shield", "part", "entry-overclaim", "warehouse-overclaim", "universal-overclaim"},
            set(result["attacks"]),
        )

    def test_runtime_sample_and_poison_are_exact(self) -> None:
        result = owner.validate_runtime(ROOT, ROOT / owner.EVIDENCE_RELATIVE)
        self.assertEqual(10, len(result["calls"]))
        self.assertEqual({"smallArm0044c08e": 8, "largeArm0044c061": 2}, result["callSiteCounts"])
        self.assertEqual({"CUnit": 6, "CTree": 2, "CBattleEngine": 2}, result["targetClassCounts"])
        self.assertEqual([8, 0, 1, 0, 0, 8], result["directParts"])
        self.assertTrue(result["poisonControl"]["eventStreamPreserved"])
        self.assertFalse(result["poisonControl"]["readyPublished"])

    def test_static_carrier_and_segment_boundary_are_exact(self) -> None:
        result = owner.validate_static(ROOT)
        self.assertEqual(owner.EXPLOSION_BODY_SHA256, result["function"]["sha256"])
        self.assertEqual("0x0044c061", result["carrierSites"]["largeArm"]["call"])
        self.assertEqual("0x0044c08e", result["carrierSites"]["smallArm"]["call"])
        self.assertTrue(result["segmentController"]["minusOneSkipsIndexedSegmentDamage"])

    def test_saved_proof_rederives_when_present(self) -> None:
        if not (self.proof / owner.READY_NAME).is_file():
            self.skipTest("proof is built after the owner tests are introduced")
        saved = json.loads((self.proof / owner.READY_NAME).read_text(encoding="utf-8"))
        owner.validate_saved(saved, ROOT, self.campaign)
        self.assertEqual("C2_BOUNDED_RUNTIME", saved["adjudication"]["semanticGrade"])
        self.assertEqual("PARTIAL_CONTRACT", saved["rebuild"]["state"])

    def test_claim_boundary_rejects_warehouse_overclaim(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["warehouseOrSegmentControllerReceiverObserved"] = True
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
