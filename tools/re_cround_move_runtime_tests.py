#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_cround_move_runtime.py"
SPEC = importlib.util.spec_from_file_location("re_cround_move_runtime", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)

RUNTIME_OWNER = "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs"
TEST_OWNER = "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"
CURRENT_OWNER_PINS = {
    RUNTIME_OWNER: (
        32_010,
        "8f8692250e70eea6bea0702dfd56d1c3c90ad17dd8dffd65acf639cec4ba6197",
    ),
    TEST_OWNER: (
        17_484,
        "cb64be81481a0d6712a13d7f7a16449974d38ba047617444b6f96c9d024c2bfc",
    ),
}
PRIOR_OWNER_ROOT = ROOT / (
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-21-cround-move-runtime-v1/_reducer"
)


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

    def test_frozen_proof_preserves_prior_owner_identity_receipt(self) -> None:
        if not (self.proof / owner.READY_NAME).is_file():
            self.skipTest("proof is built after the owner tests are introduced")
        saved = json.loads((self.proof / owner.READY_NAME).read_text(encoding="utf-8"))
        self.assertEqual(
            (31_466, "7942536b60d3bab2d0e534f2030fa74b4329b3bf9c2c19324e244c91aa33597b"),
            (saved["inputs"][RUNTIME_OWNER]["bytes"], saved["inputs"][RUNTIME_OWNER]["sha256"]),
        )
        self.assertEqual(
            (17_883, "2232bde202407035adc81317058b5594ad69e038d0889e8fb2762058d7e7529c"),
            (saved["inputs"][TEST_OWNER]["bytes"], saved["inputs"][TEST_OWNER]["sha256"]),
        )
        self.assertEqual(CURRENT_OWNER_PINS[RUNTIME_OWNER], owner.REPO_PINS[RUNTIME_OWNER])
        self.assertEqual(CURRENT_OWNER_PINS[TEST_OWNER], owner.REPO_PINS[TEST_OWNER])
        self.assertEqual("C2_BOUNDED_RUNTIME", saved["adjudication"]["semanticGrade"])
        self.assertEqual("PARTIAL_CONTRACT", saved["rebuild"]["state"])

    def test_current_owner_bytes_pass_and_prior_owner_bytes_fail(self) -> None:
        self.assertEqual(CURRENT_OWNER_PINS[RUNTIME_OWNER], owner.REPO_PINS[RUNTIME_OWNER])
        self.assertEqual(CURRENT_OWNER_PINS[TEST_OWNER], owner.REPO_PINS[TEST_OWNER])
        current = owner.exact_inputs(ROOT, ROOT / owner.EVIDENCE_RELATIVE)
        self.assertEqual(CURRENT_OWNER_PINS[RUNTIME_OWNER][1], current[RUNTIME_OWNER]["sha256"])
        self.assertEqual(CURRENT_OWNER_PINS[TEST_OWNER][1], current[TEST_OWNER]["sha256"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            for relative in CURRENT_OWNER_PINS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            with (
                mock.patch.object(owner, "PINS", {}),
                mock.patch.object(owner, "REPO_PINS", dict(CURRENT_OWNER_PINS)),
            ):
                inputs = owner.exact_inputs(root, evidence)
                self.assertEqual(CURRENT_OWNER_PINS[RUNTIME_OWNER][1], inputs[RUNTIME_OWNER]["sha256"])
                self.assertEqual(CURRENT_OWNER_PINS[TEST_OWNER][1], inputs[TEST_OWNER]["sha256"])

                (root / RUNTIME_OWNER).write_bytes((PRIOR_OWNER_ROOT / RUNTIME_OWNER).read_bytes())
                with self.assertRaisesRegex(owner.ProofError, f"repository input differs: {RUNTIME_OWNER}"):
                    owner.exact_inputs(root, evidence)

                (root / RUNTIME_OWNER).write_bytes((ROOT / RUNTIME_OWNER).read_bytes())
                (root / TEST_OWNER).write_bytes((PRIOR_OWNER_ROOT / TEST_OWNER).read_bytes())
                with self.assertRaisesRegex(owner.ProofError, f"repository input differs: {TEST_OWNER}"):
                    owner.exact_inputs(root, evidence)

    def test_input_identity_rejects_owner_mutation_wrong_path_and_forged_evidence(self) -> None:
        marker = b"hash-bound evidence\n"
        evidence_pin = (len(marker), owner.sha256_bytes(marker))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            marker_path = evidence / "READY"
            marker_path.write_bytes(marker)
            for relative in CURRENT_OWNER_PINS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            with (
                mock.patch.object(owner, "PINS", {"READY": evidence_pin}),
                mock.patch.object(owner, "REPO_PINS", dict(CURRENT_OWNER_PINS)),
            ):
                inputs = owner.exact_inputs(root, evidence)
                self.assertEqual(RUNTIME_OWNER, inputs[RUNTIME_OWNER]["path"])

                runtime_path = root / RUNTIME_OWNER
                runtime = bytearray(runtime_path.read_bytes())
                runtime[0] ^= 1
                runtime_path.write_bytes(runtime)
                with self.assertRaisesRegex(owner.ProofError, f"repository input differs: {RUNTIME_OWNER}"):
                    owner.exact_inputs(root, evidence)

                runtime_path.write_bytes((ROOT / RUNTIME_OWNER).read_bytes())
                wrong_path = root / "wrong" / Path(RUNTIME_OWNER).name
                wrong_path.parent.mkdir()
                runtime_path.replace(wrong_path)
                with self.assertRaisesRegex(owner.ProofError, "missing file"):
                    owner.exact_inputs(root, evidence)

                wrong_path.replace(runtime_path)
                marker_path.write_bytes(b"forged evidence\n")
                with self.assertRaisesRegex(owner.ProofError, "evidence identity differs: READY"):
                    owner.exact_inputs(root, evidence)

    def test_runtime_projection_rejects_session_identity_and_expected_count_changes(self) -> None:
        lane = "level522-exact-v1"
        rows = owner.read_jsonl(ROOT / owner.EVIDENCE_RELATIVE / lane / "call-context.jsonl")
        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("kind") == "metadata")["module_size"] = "0x1"
        with self.assertRaisesRegex(owner.ProofError, "module identity differs"):
            owner.validate_observations(forged, "forged-session", owner.RUNS[lane])

        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("kind") == "target")["expected_call_count"] = "232"
        with self.assertRaisesRegex(owner.ProofError, "expected_call_count differs"):
            owner.validate_observations(forged, "forged-count", owner.RUNS[lane])

    def test_claim_boundary_rejects_complete_move_overclaim(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["completeMoveSemanticsClaimed"] = True
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)

    def test_claim_boundary_rejects_stored_semantic_count_change(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["slot66CallsObserved"] += 1
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
