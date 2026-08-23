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
OWNER_PATH = ROOT / "tools/re_cround_handle_event_runtime.py"
SPEC = importlib.util.spec_from_file_location("re_cround_handle_event_runtime", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)

RUNTIME_OWNER = "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs"
TEST_OWNER = "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"
WRAPPER_OWNER = "tools/Invoke-TtdCallContextV2.ps1"
CURRENT_REPO_PINS = {
    RUNTIME_OWNER: (
        32_010,
        "8f8692250e70eea6bea0702dfd56d1c3c90ad17dd8dffd65acf639cec4ba6197",
    ),
    TEST_OWNER: (
        17_484,
        "cb64be81481a0d6712a13d7f7a16449974d38ba047617444b6f96c9d024c2bfc",
    ),
    WRAPPER_OWNER: (
        91_832,
        "0017181805a38cebfa82cd0ddd802aa7a23f06fda39f03ecc201729e4ad185d7",
    ),
}
PRIOR_OWNER_ROOT = ROOT / (
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-21-cround-move-runtime-v1/_reducer"
)


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
        for relative, expected in CURRENT_REPO_PINS.items():
            self.assertEqual(expected, owner.REPO_PINS[relative])
        self.assertEqual("C2_BOUNDED_RUNTIME", saved["adjudication"]["semanticGrade"])
        self.assertEqual("PARTIAL_CONTRACT", saved["rebuild"]["state"])
        self.assertFalse(saved["claimBoundary"]["event4002Observed"])

    def test_current_owner_bytes_pass_and_prior_owner_bytes_fail(self) -> None:
        for relative, expected in CURRENT_REPO_PINS.items():
            self.assertEqual(expected, owner.REPO_PINS[relative])
        current = owner.exact_inputs(ROOT, ROOT / owner.EVIDENCE_RELATIVE)
        for relative, expected in CURRENT_REPO_PINS.items():
            self.assertEqual(expected[1], current[relative]["sha256"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            for relative in CURRENT_REPO_PINS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            with (
                mock.patch.object(owner, "PINS", {}),
                mock.patch.object(owner, "REPO_PINS", dict(CURRENT_REPO_PINS)),
            ):
                inputs = owner.exact_inputs(root, evidence)
                for relative, expected in CURRENT_REPO_PINS.items():
                    self.assertEqual(expected[1], inputs[relative]["sha256"])

                (root / RUNTIME_OWNER).write_bytes((PRIOR_OWNER_ROOT / RUNTIME_OWNER).read_bytes())
                with self.assertRaisesRegex(owner.ProofError, f"repository input differs: {RUNTIME_OWNER}"):
                    owner.exact_inputs(root, evidence)

                (root / RUNTIME_OWNER).write_bytes((ROOT / RUNTIME_OWNER).read_bytes())
                (root / TEST_OWNER).write_bytes((PRIOR_OWNER_ROOT / TEST_OWNER).read_bytes())
                with self.assertRaisesRegex(owner.ProofError, f"repository input differs: {TEST_OWNER}"):
                    owner.exact_inputs(root, evidence)

                (root / TEST_OWNER).write_bytes((ROOT / TEST_OWNER).read_bytes())
                prior_wrapper = (ROOT / WRAPPER_OWNER).read_bytes().replace(b"\r\n", b"\n")
                self.assertEqual(
                    (89_821, "2fd3cfb962e19820fce8b0890f6b0e803255cde34f14bc9c1bcd3246f4f17bc3"),
                    (len(prior_wrapper), owner.sha256_bytes(prior_wrapper)),
                )
                (root / WRAPPER_OWNER).write_bytes(prior_wrapper)
                with self.assertRaisesRegex(owner.ProofError, f"repository input differs: {WRAPPER_OWNER}"):
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
            for relative in CURRENT_REPO_PINS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            with (
                mock.patch.object(owner, "PINS", {"READY": evidence_pin}),
                mock.patch.object(owner, "REPO_PINS", dict(CURRENT_REPO_PINS)),
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
        lane = "level512-holdout-exact-v1"
        rows = owner.read_jsonl(ROOT / owner.EVIDENCE_RELATIVE / lane / "call-context.jsonl")
        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("kind") == "metadata")["module_size"] = "0x1"
        with self.assertRaisesRegex(owner.ProofError, "module identity differs"):
            owner.validate_observations(forged, "forged-session", owner.RUNS[lane])

        forged = copy.deepcopy(rows)
        next(
            row for row in forged
            if row.get("kind") == "target" and row.get("target_index") == 0
        )["expected_entry_count"] = "25"
        with self.assertRaisesRegex(owner.ProofError, "target 0 expected entry differs"):
            owner.validate_observations(forged, "forged-count", owner.RUNS[lane])

    def test_claim_boundary_rejects_arm_effect_overclaim(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["armEffectsClaimed"] = True
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)

    def test_claim_boundary_rejects_stored_semantic_count_change(self) -> None:
        forged = copy.deepcopy(owner.EXPECTED_BOUNDARY)
        forged["observedEventIds"]["4000"] += 1
        with self.assertRaisesRegex(owner.ProofError, "claim boundary differs"):
            owner.validate_claim_boundary(forged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
