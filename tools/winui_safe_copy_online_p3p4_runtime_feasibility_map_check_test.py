#!/usr/bin/env python3
"""Focused tests for the P3/P4 runtime feasibility map checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_p3p4_runtime_feasibility_map_check as checker


class P3P4RuntimeFeasibilityMapCheckerTests(unittest.TestCase):
    def write_fixture(self, root: Path) -> Path:
        path = root / "map.json"
        payload = json.loads(checker.CONTRACT.read_text(encoding="utf-8"))
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_accepts_current_map_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = checker.validate_contract(self.write_fixture(Path(tmp)))
            self.assertEqual(summary["maxOriginalBinaryActiveSlotsProven"], 2)
            self.assertEqual(summary["mapProofClass"], "static-blast-radius-map-not-runtime-proof")
            self.assertEqual(summary["nPlayerOriginalBinaryRuntimeProof"], 0)
            self.assertEqual(summary["newBeaLaunchCount"], 0)
            self.assertEqual(summary["cdbAttachCount"], 0)
            self.assertTrue(summary["p3p4GameplayInputRejected"])
            self.assertFalse(summary["permanentImpossibilityClaim"])

    def test_rejects_source_only_max_players_as_runtime_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["sourceOnlyMaxPlayersIsRuntimeProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_quad_split_branch_as_runtime_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["quadSplitBranchIsRuntimeProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_raising_runtime_slot_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["maxOriginalBinaryActiveSlotsProven"] = 4
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_raising_retail_viewpoint_or_n_player_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["retailViewpointsProven"] = 4
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["nPlayerOriginalBinaryRuntimeProof"] = 1
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_p3_p4_gameplay_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["acceptedOriginalBinaryGameplaySlots"] = ["P1", "P2", "P3"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["p3p4GameplayInputRejected"] = False
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_runtime_attempt_ready_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["proofBoundary"]["mapCompleteForRuntimeAttempt"] = True
            payload["proofBoundary"]["safeToPatchMPlayersAbove2"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_source_row_runtime_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["blastRadiusRows"][0]["supportsOriginalBinaryRuntimeProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_missing_viewpoint_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["blastRadiusRows"] = [
                row for row in payload["blastRadiusRows"] if row["id"] != "engine-viewpoints-two"
            ]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_weakened_required_proof_class(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["requiredNewProofClassForP3P4"] = payload["requiredNewProofClassForP3P4"][:2]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)

    def test_rejects_public_online_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_fixture(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["nonClaims"]["publicMatchmakingProof"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(checker.P3P4FeasibilityMapError):
                checker.validate_contract(path)


if __name__ == "__main__":
    unittest.main()
