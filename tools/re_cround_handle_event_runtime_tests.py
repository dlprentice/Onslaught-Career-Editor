#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_cround_handle_event_runtime.py"
SPEC = importlib.util.spec_from_file_location("re_cround_handle_event_runtime", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class CRoundHandleEventRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.campaign = ROOT / owner.CAMPAIGN_RELATIVE
        cls.proof = ROOT / owner.EVIDENCE_RELATIVE / "proof-v1"

    def test_selftest_refuses_routing_and_scope_overclaims(self) -> None:
        result = owner.selftest(ROOT, self.campaign)
        self.assertEqual(9, result["count"])
        self.assertEqual(
            {
                "cmissile-vtable",
                "receiver-discontinuity",
                "event-argument-discontinuity",
                "arm-id-mismatch",
                "return-outside-body",
                "event4002-overclaim",
                "arm-effects-overclaim",
                "complete-subclass-overclaim",
                "rebuild-ready-overclaim",
            },
            set(result["attacks"]),
        )

    def test_runtime_samples_arms_and_poison_are_exact(self) -> None:
        result = owner.validate_runtime(ROOT, ROOT / owner.EVIDENCE_RELATIVE)
        self.assertEqual(2_555, result["slot0CallsObserved"])
        self.assertEqual(2_555, result["armEntries"])
        self.assertEqual(1_972, result["gapFreeReturns"])
        self.assertEqual(583, result["rawOrphanReturns"])
        self.assertEqual([40, 6], result["sessionLocalReceiverInstancesByTrace"])
        self.assertEqual([412, 18], result["sessionLocalEventPointersByTrace"])
        self.assertEqual(
            {"2000": 167, "3000": 2_190, "4000": 120, "4001": 3, "4003": 75},
            result["observedEventIds"],
        )
        self.assertTrue(result["strictCRoundVtableAllCalls"])
        self.assertFalse(result["cmissileStyleVtableObserved"])
        self.assertFalse(result["event4002Observed"])
        self.assertTrue(result["poisonControl"]["eventStreamPreserved"])
        self.assertFalse(result["poisonControl"]["readyPublished"])

    def test_static_switch_placements_and_fingerprint_are_exact(self) -> None:
        result = owner.validate_static(ROOT)
        self.assertEqual(owner.BODY_SHA256, result["function"]["sha256"])
        self.assertEqual("0x005de82c", result["placements"]["strictCRound"]["vtable"])
        self.assertEqual("0x005e3ba4", result["placements"]["cmissileStyle"]["vtable"])
        self.assertEqual("0x004d995e", result["switch"]["fixedArms"]["4002"])
        self.assertEqual("CRound__HandleEvent", result["trackedStaticLabel"])
        self.assertEqual(owner.CURRENT_NAME, result["campaignNameRetained"])
        self.assertTrue(result["pcDemo"]["exactZeroNormalized"])
        self.assertEqual("OPEN_NOT_PROMOTED_BY_THIS_PROOF", result["sourceSpellingStatus"])

    def test_saved_proof_rederives_when_present(self) -> None:
        if not (self.proof / owner.READY_NAME).is_file():
            self.skipTest("proof is built after the owner tests are introduced")
        saved = json.loads((self.proof / owner.READY_NAME).read_text(encoding="utf-8"))
        owner.validate_saved(saved, ROOT, self.campaign)
        self.assertEqual("C2_BOUNDED_RUNTIME", saved["adjudication"]["semanticGrade"])
        self.assertEqual("PARTIAL_CONTRACT", saved["rebuild"]["state"])
        self.assertFalse(saved["claimBoundary"]["event4002Observed"])

    def test_claim_boundary_rejects_arm_effect_overclaim(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["armEffectsClaimed"] = True
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
