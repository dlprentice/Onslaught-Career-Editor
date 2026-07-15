#!/usr/bin/env python3
"""Tests for the BattleEngine target-acquisition static contract gate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import battleengine_target_acquisition_static_contract as contract


SOURCE_PIN = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"

EXPECTED_LOCK_PATH_CLAIMS = (
    "The sole reviewed caller is CBattleEngine__Move, which enters 0x00406560 with the BattleEngine pointer and no explicit stack arguments.",
    "The helper selects the current JetPart or WalkerPart weapon from the BattleEngine state before maintaining or acquiring locks.",
    "The helper removes null, dying, or out-of-deflection entries from the tracked lock set at BattleEngine +0x294.",
    "New acquisition is bounded by current-weapon fire readiness and maximum-lock gates; numeric thresholds and runtime timing remain unproven.",
    "The body contains distinct direct, proximity, and sequence lock-mode paths without establishing their live selection or gameplay outcomes.",
    "Four calls from HandleLocks pass a target, lock-time value, and direct-lock flag to 0x00406fc0; this is lock-entry creation structure, not projectile emission proof.",
)

EXPECTED_CANDIDATE_ORDER_CLAIMS = (
    "0x00406da0 traverses the global candidate set rooted at DAT_008550d0.",
    "Each candidate first passes an address-bound side/team compatibility helper.",
    "The candidate then passes the saved weapon/profile target-mask eligibility helper.",
    "Squared distance from the caller-supplied origin is checked against a scaled range and the current nearest-so-far value.",
    "A BattleEngine-relative normalized direction is compared with a cosine-derived deflection threshold.",
    "The candidate is excluded when it already appears in the tracked set at BattleEngine +0x294.",
    "The helper returns the best retained candidate pointer or null when none survives.",
)

EXPECTED_PROVES_CLAIMS = (
    "the reviewed retail-static identity and bounded lock-maintenance phases of CBattleEngine__HandleLocks at 0x00406560",
    "the address-bound candidate-filter ordering retained by the saved 0x00406da0 helper body",
    "the target, lock-time, and direct-lock call shape of the saved 0x00406fc0 dependent helper",
)

EXPECTED_DOES_NOT_PROVE_CLAIMS = (
    "runtime target choice",
    "lock timing",
    "Core behavior",
    "exact helper source identity",
    "the retail semantic meaning of the source stealth expression",
    "projectile emission or weapon firing",
    "exact object or field layouts",
    "gameplay outcomes",
    "visual behavior",
    "rebuild parity",
)


def valid_payload() -> dict[str, object]:
    return {
        "schemaVersion": "battleengine-target-acquisition-static-contract.v1",
        "contractId": "M2.3-target-acquisition-static-contract",
        "status": "accepted-static-contract-not-runtime-proof",
        "evidenceHierarchy": [
            "reviewed-retail-static",
            "saved-retail-structure",
            "pinned-source-hypothesis",
            "runtime-required",
        ],
        "sourceReference": {
            "repository": "dlprentice/Onslaught",
            "commit": SOURCE_PIN,
            "path": "BattleEngine.cpp",
            "role": "pinned-source-hypothesis-only",
        },
        "anchors": [
            {
                "address": "0x00406560",
                "currentRetailName": "CBattleEngine__HandleLocks",
                "retailNameStatus": "reviewed-current",
                "sourceCandidate": "CBattleEngine::HandleLocks",
                "sourceCandidateStatus": "reviewed-source-aligned-retail-static",
            },
            {
                "address": "0x00406da0",
                "currentRetailName": "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
                "retailNameStatus": "saved-descriptive",
                "sourceCandidate": "CBattleEngine::GetClosestLockableUnit",
                "sourceCandidateStatus": "hypothesis-only",
            },
            {
                "address": "0x00406fc0",
                "currentRetailName": "CBattleEngine__AddProjectile",
                "retailNameStatus": "saved-dependent-name-semantic-role-superseded",
                "sourceCandidate": "CBattleEngine::StartLock",
                "sourceCandidateStatus": "hypothesis-only",
            },
        ],
        "lockPathRows": [
            {
                "ordinal": ordinal,
                "id": row_id,
                "evidenceTier": tier,
                "claim": claim,
            }
            for ordinal, ((row_id, tier), claim) in enumerate(
                zip(contract.LOCK_PATH_ROWS, EXPECTED_LOCK_PATH_CLAIMS), start=1
            )
        ],
        "candidateOrder": [
            {
                "ordinal": ordinal,
                "id": row_id,
                "evidenceTier": tier,
                "claim": claim,
            }
            for ordinal, ((row_id, tier), claim) in enumerate(
                zip(contract.CANDIDATE_ORDER_ROWS, EXPECTED_CANDIDATE_ORDER_CLAIMS), start=1
            )
        ],
        "sourceHypotheses": [
            {"id": "stealth-adjusted-effective-lock-range", "evidenceTier": "pinned-source-hypothesis", "retailRuntimeAccepted": False},
            {"id": "helper-00406da0-is-get-closest-lockable-unit", "evidenceTier": "pinned-source-hypothesis", "retailRuntimeAccepted": False},
            {"id": "helper-00406fc0-is-start-lock", "evidenceTier": "pinned-source-hypothesis", "retailRuntimeAccepted": False},
        ],
        "evidencePaths": list(contract.REQUIRED_EVIDENCE_PATHS),
        "guardSummary": {
            "runtimeObservation": False,
            "beaLaunch": False,
            "debuggerAttachment": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "targetChoiceCausalityProven": False,
            "lockTimingProven": False,
            "exactLayoutProven": False,
            "exactHelperSourceIdentityProven": False,
            "coreImplementation": False,
            "godotImplementation": False,
            "visualProof": False,
            "rebuildParityProven": False,
            "releasePublicationOccurred": False,
            "runtimeObservationRows": 0,
            "coreImplementationRows": 0,
        },
        "claimBoundary": {
            "proves": list(EXPECTED_PROVES_CLAIMS),
            "doesNotProve": list(EXPECTED_DOES_NOT_PROVE_CLAIMS),
        },
    }


def valid_markdown(payload: dict[str, object]) -> str:
    tokens = [
        payload["schemaVersion"],
        payload["contractId"],
        SOURCE_PIN,
        *(anchor["address"] for anchor in payload["anchors"]),
        *(anchor["currentRetailName"] for anchor in payload["anchors"]),
        *(anchor["sourceCandidate"] for anchor in payload["anchors"]),
        *(row["id"] for row in payload["lockPathRows"]),
        *(row["claim"] for row in payload["lockPathRows"]),
        *(row["id"] for row in payload["candidateOrder"]),
        *(row["claim"] for row in payload["candidateOrder"]),
        *(row["id"] for row in payload["sourceHypotheses"]),
        *payload["evidenceHierarchy"],
        *payload["claimBoundary"]["proves"],
        *payload["claimBoundary"]["doesNotProve"],
    ]
    return "\n".join(f"`{token}`" for token in tokens)


def write_authority_tree(root: Path, *, corrected_name: str = "CBattleEngine__HandleLocks") -> None:
    for relative in contract.REQUIRED_EVIDENCE_PATHS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")

    correction = root / contract.CORRECTION_PLAN_PATH
    correction.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "address": "0x00406560",
                        "classification": "confirmed-apply",
                        "correctedName": corrected_name,
                        "correctedSignature": "void __fastcall CBattleEngine__HandleLocks(void * this)",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (root / contract.CORRECTION_DECISIONS_PATH).write_text(
        json.dumps({"address": "0x00406560", "classification": "confirmed-apply"}) + "\n",
        encoding="utf-8",
    )
    required_doc_text = {
        contract.HANDLE_LOCKS_DOC_PATH: "CBattleEngine__HandleLocks\nlock-entry creation\n",
        contract.NEAREST_HELPER_DOC_PATH: "CBattleEngine::GetClosestLockableUnit\nhypothesis-only\n",
        contract.LOCK_ENTRY_DOC_PATH: "saved Ghidra\nlock-entry creation\nCBattleEngine::StartLock\n",
        contract.UNIT_STATIC_CONTRACT_PATH: "battleengine-target-acquisition-static-contract-v1.json\nCBattleEngine__HandleLocks\n",
        contract.SOURCE_AUDIT_PATH: f"{SOURCE_PIN}\nStuart source suggests architecture\n",
    }
    for relative, text in required_doc_text.items():
        (root / relative).write_text(text, encoding="utf-8")


class BattleEngineTargetAcquisitionStaticContractTests(unittest.TestCase):
    def validate(self, payload: dict[str, object], markdown: str | None = None) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root)
            return contract.validate_contract(payload, markdown or valid_markdown(payload), root=root)

    def test_accepts_canonical_contract(self) -> None:
        report = self.validate(valid_payload())
        self.assertTrue(report["passed"])
        self.assertEqual(report["anchorCount"], 3)
        self.assertEqual(report["candidateOrderCount"], 7)

    def test_v1_claim_oracle_is_independent_and_exact(self) -> None:
        self.assertEqual(contract.LOCK_PATH_CLAIMS, EXPECTED_LOCK_PATH_CLAIMS)
        self.assertEqual(contract.CANDIDATE_ORDER_CLAIMS, EXPECTED_CANDIDATE_ORDER_CLAIMS)
        self.assertEqual(contract.PROVES_CLAIMS, EXPECTED_PROVES_CLAIMS)
        self.assertEqual(contract.DOES_NOT_PROVE_CLAIMS, EXPECTED_DOES_NOT_PROVE_CLAIMS)

    def test_rejects_superseded_primary_anchor_name(self) -> None:
        payload = valid_payload()
        payload["anchors"][0]["currentRetailName"] = "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"
        with self.assertRaisesRegex(contract.ContractError, "canonical anchors"):
            self.validate(payload)

    def test_rejects_exact_source_identity_promotion_for_helper(self) -> None:
        payload = valid_payload()
        payload["anchors"][1]["sourceCandidateStatus"] = "reviewed-source-aligned-retail-static"
        with self.assertRaisesRegex(contract.ContractError, "canonical anchors"):
            self.validate(payload)

    def test_rejects_candidate_order_change(self) -> None:
        payload = valid_payload()
        payload["candidateOrder"][3], payload["candidateOrder"][4] = (
            payload["candidateOrder"][4],
            payload["candidateOrder"][3],
        )
        with self.assertRaisesRegex(contract.ContractError, "candidateOrder"):
            self.validate(payload)

    def test_rejects_truthy_runtime_guard(self) -> None:
        for key in contract.FALSE_GUARDS:
            with self.subTest(key=key):
                payload = valid_payload()
                payload["guardSummary"][key] = True
                with self.assertRaisesRegex(contract.ContractError, "guardSummary"):
                    self.validate(payload)

    def test_rejects_non_integer_zero_counters(self) -> None:
        for key in contract.ZERO_GUARDS:
            for value in (False, 0.0, "0"):
                with self.subTest(key=key, value=repr(value)):
                    payload = valid_payload()
                    payload["guardSummary"][key] = value
                    with self.assertRaisesRegex(contract.ContractError, "guardSummary"):
                        self.validate(payload)

    def test_rejects_absolute_evidence_path(self) -> None:
        payload = valid_payload()
        payload["evidencePaths"][0] = "C:/private/evidence.json"
        with self.assertRaisesRegex(contract.ContractError, "evidencePaths"):
            self.validate(payload)

    def test_rejects_missing_markdown_contract_token(self) -> None:
        payload = valid_payload()
        markdown = valid_markdown(payload).replace("existing-lock-exclusion", "missing-row")
        with self.assertRaisesRegex(contract.ContractError, "Markdown"):
            self.validate(payload, markdown)

    def test_rejects_missing_markdown_bounded_proves_claim(self) -> None:
        payload = valid_payload()
        markdown = valid_markdown(payload).replace(EXPECTED_PROVES_CLAIMS[0], "missing-claim")
        with self.assertRaisesRegex(contract.ContractError, "Markdown"):
            self.validate(payload, markdown)

    def test_rejects_contradictory_markdown_runtime_claim(self) -> None:
        payload = valid_payload()
        markdown = valid_markdown(payload) + "\nRuntime target choice is proven.\n"
        with self.assertRaisesRegex(contract.ContractError, "forbidden claim"):
            self.validate(payload, markdown)

    def test_rejects_lock_path_order_change(self) -> None:
        payload = valid_payload()
        payload["lockPathRows"][1], payload["lockPathRows"][2] = (
            payload["lockPathRows"][2],
            payload["lockPathRows"][1],
        )
        with self.assertRaisesRegex(contract.ContractError, "lockPathRows"):
            self.validate(payload)

    def test_rejects_runtime_promotion_inside_static_row_claim(self) -> None:
        payload = valid_payload()
        payload["lockPathRows"][0]["claim"] = "This proves runtime target choice."
        with self.assertRaisesRegex(contract.ContractError, "lockPathRows"):
            self.validate(payload)

    def test_rejects_runtime_promotion_inside_proves_boundary(self) -> None:
        payload = valid_payload()
        payload["claimBoundary"]["proves"].append("runtime target choice")
        with self.assertRaisesRegex(contract.ContractError, "claimBoundary"):
            self.validate(payload)

    def test_rejects_drive_relative_and_uri_paths(self) -> None:
        for value in ("C:private\\evidence.json", "file:private/evidence.json"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(contract.ContractError, "path"):
                    contract._safe_relative(value, "path")

    def test_rejects_unaccepted_correction_record(self) -> None:
        payload = valid_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root, corrected_name="CBattleEngine__UpdateAutoTargetSetAndFireProjectiles")
            with self.assertRaisesRegex(contract.ContractError, "correction plan"):
                contract.validate_contract(payload, valid_markdown(payload), root=root)

    def test_rejects_conflicting_correction_plan_row(self) -> None:
        payload = valid_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root)
            plan_path = root / contract.CORRECTION_PLAN_PATH
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["records"].append(
                {
                    "address": "0x00406560",
                    "classification": "rejected-manifest-error",
                    "correctedName": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
                    "correctedSignature": "void __fastcall CBattleEngine__HandleLocks(void * this)",
                }
            )
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(contract.ContractError, "correction plan"):
                contract.validate_contract(payload, valid_markdown(payload), root=root)

    def test_rejects_conflicting_correction_decision_row(self) -> None:
        payload = valid_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root)
            decision_path = root / contract.CORRECTION_DECISIONS_PATH
            with decision_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "address": "0x00406560",
                            "classification": "rejected-manifest-error",
                        }
                    )
                    + "\n"
                )
            with self.assertRaisesRegex(contract.ContractError, "correction decisions"):
                contract.validate_contract(payload, valid_markdown(payload), root=root)

    def test_rejects_runtime_projectile_promotion_in_current_helper_note(self) -> None:
        payload = valid_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root)
            helper_path = root / contract.LOCK_ENTRY_DOC_PATH
            with helper_path.open("a", encoding="utf-8") as handle:
                handle.write("Runtime projectile emission is proven by the saved helper.\n")
            with self.assertRaisesRegex(contract.ContractError, "forbidden claim"):
                contract.validate_contract(payload, valid_markdown(payload), root=root)

    def test_rejects_initialized_source_at_wrong_revision(self) -> None:
        payload = valid_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root)
            source_path = root / contract.SOURCE_PATH
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text("\n".join(contract.SOURCE_TOKEN_REQUIREMENTS), encoding="utf-8")
            with mock.patch.object(contract, "_source_revision", return_value="0" * 40):
                with self.assertRaisesRegex(contract.ContractError, "pinned source revision"):
                    contract.validate_contract(payload, valid_markdown(payload), root=root)

    def test_uses_committed_source_text_instead_of_dirty_worktree(self) -> None:
        payload = valid_payload()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_authority_tree(root)
            source_path = root / contract.SOURCE_PATH
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text("\n".join(contract.SOURCE_TOKEN_REQUIREMENTS), encoding="utf-8")
            with (
                mock.patch.object(contract, "_source_revision", return_value=SOURCE_PIN),
                mock.patch.object(
                    contract,
                    "_source_text_at_revision",
                    return_value="committed text without expected tokens",
                ),
            ):
                with self.assertRaisesRegex(contract.ContractError, "pinned source commit"):
                    contract.validate_contract(payload, valid_markdown(payload), root=root)

    def test_tracked_contract_passes(self) -> None:
        report = contract.validate_tracked_contract()
        self.assertTrue(report["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
