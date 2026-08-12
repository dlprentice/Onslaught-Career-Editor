#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_cround_move_runtime.py"
SPEC = importlib.util.spec_from_file_location("re_cround_move_runtime", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class CRoundMoveRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.campaign = ROOT / owner.CAMPAIGN_RELATIVE
        cls.proof = ROOT / owner.EVIDENCE_RELATIVE / "proof-v1"

    def test_selftest_refuses_placement_envelope_and_scope_overclaims(self) -> None:
        result = owner.selftest(ROOT, self.campaign)
        self.assertEqual(6, result["count"])
        self.assertEqual(
            {
                "cmissile-vtable",
                "receiver-discontinuity",
                "return-outside-body",
                "complete-move-overclaim",
                "all-subclass-overclaim",
                "rebuild-ready-overclaim",
            },
            set(result["attacks"]),
        )

    def test_runtime_samples_and_poison_are_exact(self) -> None:
        result = owner.validate_runtime(ROOT, ROOT / owner.EVIDENCE_RELATIVE)
        self.assertEqual(7_513, result["exactReplayCalls"])
        self.assertEqual(7_204, result["gapFreeReturns"])
        self.assertEqual(309, result["rawOrphanReturns"])
        self.assertEqual(71, result["sessionLocalReceiverInstances"])
        self.assertTrue(result["strictCRoundVtableAllCalls"])
        self.assertFalse(result["cmissileStyleVtableObserved"])
        self.assertTrue(result["poisonControl"]["eventStreamPreserved"])
        self.assertFalse(result["poisonControl"]["readyPublished"])

    def test_static_slot_identity_and_fingerprint_are_exact(self) -> None:
        result = owner.validate_static(ROOT)
        self.assertEqual(owner.BODY_SHA256, result["function"]["sha256"])
        self.assertEqual("0x005de82c", result["placements"]["strictCRound"]["vtable"])
        self.assertEqual("0x005e3ba4", result["placements"]["cmissileStyle"]["vtable"])
        self.assertEqual("CRound__Move", result["currentSavedProjectName"])
        self.assertTrue(result["pcDemo"]["exactZeroNormalized"])
        self.assertEqual("OPEN_NOT_PROMOTED_BY_THIS_PROOF", result["sourceSpellingStatus"])

    def test_saved_proof_rederives_when_present(self) -> None:
        if not (self.proof / owner.READY_NAME).is_file():
            self.skipTest("proof is built after the owner tests are introduced")
        saved = json.loads((self.proof / owner.READY_NAME).read_text(encoding="utf-8"))
        owner.validate_saved(saved, ROOT, self.campaign)
        self.assertEqual("C2_BOUNDED_RUNTIME", saved["adjudication"]["semanticGrade"])
        self.assertEqual("PARTIAL_CONTRACT", saved["rebuild"]["state"])

    def test_claim_boundary_rejects_complete_move_overclaim(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["completeMoveSemanticsClaimed"] = True
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
