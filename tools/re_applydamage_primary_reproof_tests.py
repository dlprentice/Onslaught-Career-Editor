#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_applydamage_primary_reproof.py"
SPEC = importlib.util.spec_from_file_location("re_applydamage_primary_reproof", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


class ApplyDamagePrimaryReproofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ready_path = ROOT / owner.EVIDENCE_RELATIVE / owner.READY_NAME
        if not cls.ready_path.is_file():
            raise AssertionError(f"required ApplyDamage proof is missing: {cls.ready_path}")
        cls.saved = json.loads(cls.ready_path.read_text(encoding="utf-8"))

    def test_exact_saved_proof_rederives(self) -> None:
        owner.validate_saved(self.saved, ROOT)
        self.assertEqual("PASS", self.saved["verdict"])
        self.assertEqual("C2_BOUNDED_RUNTIME", self.saved["adjudication"]["semanticGrade"])
        self.assertEqual(owner.PARENT_READY_SHA256, self.saved["parent"]["readySha256"])

    def test_load_bearing_claim_tampers_are_refused(self) -> None:
        mutations = (
            ("paired return", lambda value: value["callContext"].update(returnAssociation="VALIDATED_RETURN")),
            ("different receiver", lambda value: value["callContext"].update(receiver="0x080dc634")),
            ("gap-free writes", lambda value: value["writes"].update(gapFree=True)),
            ("shield absorption", lambda value: value["writes"]["shields"].update(afterBits="0xbf800000")),
            ("stronger semantic grade", lambda value: value["adjudication"].update(semanticGrade="REBUILD_READY")),
            ("different parent", lambda value: value["parent"].update(readySha256="0" * 64)),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                poisoned = copy.deepcopy(self.saved)
                mutate(poisoned)
                with self.assertRaisesRegex(owner.ProofError, "proof content differs"):
                    owner.validate_saved(poisoned, ROOT)

    def test_runtime_events_replicate_and_count_poison_is_refused(self) -> None:
        result = owner.validate_writes(ROOT / owner.EVIDENCE_RELATIVE)
        self.assertEqual(owner.WRITES_NEUTRAL_SHA256, result["nonMetadataSha256"])
        self.assertEqual("LIFE_EXPECTED_TWO_WRITES_REFUSED", result["adverse"])
        self.assertFalse(result["gapFree"])
        self.assertEqual(2, result["eventPairs"])

    def test_call_entry_replicates_while_return_stays_withheld(self) -> None:
        result = owner.validate_call(ROOT, ROOT / owner.EVIDENCE_RELATIVE)
        self.assertEqual(owner.CALL_NEUTRAL_SHA256, result["nonMetadataSha256"])
        self.assertEqual("WITHHELD_RECORDED_GAP", result["returnAssociation"])
        self.assertEqual(1000.0, result["arguments"]["damageAmountF32"])
        self.assertEqual(-1, result["arguments"]["meshPartIndex"])

    def test_current_trace_is_only_size_checked_by_the_proof_owner(self) -> None:
        self.assertTrue(owner.TRACE_PATH.is_file())
        self.assertEqual(owner.TRACE_BYTES, owner.TRACE_PATH.stat().st_size)
        self.assertIn(
            "DUAL_WRAPPER_HASH_RECEIPTS_PLUS_CURRENT_SIZE_NOT_REHASHED_BY_PROOF",
            self.saved["trace"]["identityMode"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
