#!/usr/bin/env python3
"""Regression tests for reviewed RE contract and stale-mutator boundaries."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools import re_behavior_contract_guard as guard


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "ghidra-reviewed-correction-plan-2026-07-13.json"
CANDIDATE = ROOT / "reverse-engineering" / "binary-analysis" / "first-flight-camera-movement-morph-contract-candidate.v1.json"
MOVEMENT_MUTATOR = ROOT / "tools" / "ApplyMovementJetPartSignatureCorrection.java"
WAVE1187_MUTATOR = ROOT / "tools" / "ApplyCMonitorMovementAudioAnimationRenderCurrentRiskWave1187.java"

SUPERSEDED = {
    "0x00411630": {
        "forbiddenName": "CMonitor__IntegrateMovementAgainstTerrain",
        "acceptedName": "CBattleEngineJetPart__HandleGroundEffect",
        "forbiddenCommentTokens": (
            "CMonitor__UpdateMovementTransitionAndEffects",
            "monitor movement/terrain helper",
        ),
    },
    "0x00411aa0": {
        "forbiddenName": "CMonitor__ComputeTerrainVelocityScalar",
        "acceptedName": "CBattleEngineJetPart__GetFriction",
        "forbiddenCommentTokens": (
            "CMonitor__UpdateMovementTransitionAndEffects",
            "monitor terrain/velocity scalar helper",
        ),
    },
}

EXPECTED_REMAINING = {
    MOVEMENT_MUTATOR: {
        ("0x00411a60", "Vec3__Cross"),
        ("0x00411b70", "CBattleEngineJetPart__IsStateMachineActive"),
        ("0x00411e70", "CBattleEngineJetPart__ChangeWeapon"),
        ("0x00412000", "CBattleEngineJetPart__LoseWeaponCharge"),
        ("0x00412050", "CBattleEngineJetPart__WeaponFired"),
        ("0x004121b0", "CBattleEngineJetPart__GetWeaponAmmoPercentage"),
        ("0x004122b0", "CBattleEngineJetPart__IsWeaponOverheated"),
        ("0x00412310", "CBattleEngineJetPart__IsEnergyWeapon"),
        ("0x00412370", "CBattleEngineJetPart__GetWeaponCharge"),
        ("0x00412480", "CBattleEngineJetPart__GetWeaponPhysicsName"),
        ("0x004124d0", "CBattleEngineJetPart__GetCurrentWeaponNameField04"),
        ("0x00412520", "CBattleEngineJetPart__GetWeaponIconName"),
        ("0x00412570", "CBattleEngineJetPart__CanWeaponFire"),
        ("0x00412610", "CBattleEngineJetPart__GetCurrentWeapon"),
    },
    WAVE1187_MUTATOR: {
        ("0x00409950", "CMonitor__UpdateSoundEventPlaybackForReader"),
        ("0x0044e2c0", "CMonitor__CheckSVFAnimationAndAdvanceState"),
        ("0x0047d3b0", "CMonitor__TryQueuePrefireAnimation"),
        ("0x005078f0", "CMonitor__UpdateTrackedRenderPair"),
    },
}

class ReviewedCorrectionGuardTests(unittest.TestCase):
    def test_candidate_keeps_evidence_compartments_and_runtime_gate_explicit(self) -> None:
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))

        self.assertEqual(
            "first-flight-camera-movement-morph-contract-candidate.v1",
            candidate["schemaVersion"],
        )
        self.assertEqual("candidate-static-runtime-required", candidate["status"])
        self.assertFalse(candidate["rebuildChangeAuthorized"])
        self.assertFalse(candidate["retry13Authorized"])
        self.assertEqual(
            [
                "camera_reference_frame",
                "walker_directional_response",
                "jet_directional_response",
                "morph_request_result_correlation",
            ],
            candidate["observationOrder"],
        )

        required = {
            "sourceHypothesis",
            "steamStaticCorroboration",
            "copiedRuntimeMeasurement",
            "tolerances",
            "rebuildRequirement",
            "nonclaims",
        }
        observations = candidate["observations"]
        self.assertEqual(candidate["observationOrder"], [row["id"] for row in observations])
        for row in observations:
            with self.subTest(observation=row["id"]):
                self.assertTrue(required.issubset(row))
                self.assertEqual("required-not-measured", row["copiedRuntimeMeasurement"]["status"])
                self.assertEqual("not-established", row["tolerances"]["status"])
                self.assertEqual("blocked-until-runtime-accepted", row["rebuildRequirement"]["status"])
                self.assertTrue(row["nonclaims"])

    def test_authoritative_rows_explicitly_supersede_exact_names(self) -> None:
        plan = json.loads(PLAN.read_text(encoding="utf-8"))

        for address, expected in SUPERSEDED.items():
            with self.subTest(address=address):
                matching = [record for record in plan["records"] if record["address"] == address]
                self.assertEqual(1, len(matching))
                record = matching[0]
                self.assertEqual("confirmed-apply", record["classification"])
                self.assertEqual(expected["forbiddenName"], record["currentName"])
                self.assertEqual(expected["acceptedName"], record["correctedName"])
                self.assertIn("name", record["correctedFields"])
                self.assertIn("comment", record["correctedFields"])
                self.assertIn(expected["acceptedName"], record["correctedSignature"])
                self.assertNotIn(expected["forbiddenName"], record["correctedComment"])
                self.assertIn(expected["acceptedName"].replace("__", "::"), record["correctedComment"])
                for token in expected["forbiddenCommentTokens"]:
                    self.assertNotIn(token, record["correctedComment"])

    def test_active_mutators_do_not_contain_superseded_address_records(self) -> None:
        for path in (MOVEMENT_MUTATOR, WAVE1187_MUTATOR):
            text = path.read_text(encoding="utf-8")
            for address, forbidden in SUPERSEDED.items():
                with self.subTest(path=path.name, address=address):
                    self.assertFalse(guard.contains_forbidden_pair(text, address, forbidden))

    def test_unrelated_mixed_helper_operations_remain(self) -> None:
        markers = {
            MOVEMENT_MUTATOR: "applySignature",
            WAVE1187_MUTATOR: "new Target",
        }
        for path, expected in EXPECTED_REMAINING.items():
            with self.subTest(path=path.name):
                self.assertEqual(
                    expected,
                    set(guard.extract_literal_mutation_pairs(path.read_text(encoding="utf-8"), markers[path])),
                )

    def test_literal_pair_parser_ignores_comment_addresses_and_requires_target_literals(self) -> None:
        synthetic = '''
        // Earlier comment mentions 0x00411630 but is not a mutation.
        // applySignature("0x00412050", "CBattleEngineJetPart__WeaponFired", "__thiscall");
        applySignature("0x00411a60", "Vec3__Cross", "__cdecl");
        applySignature("0x00411630", "CMonitor__IntegrateMovementAgainstTerrain", "__thiscall");
        '''
        self.assertEqual(
            [
                ("0x00411a60", "Vec3__Cross"),
                ("0x00411630", "CMonitor__IntegrateMovementAgainstTerrain"),
            ],
            guard.extract_literal_mutation_pairs(synthetic, "applySignature"),
        )
        self.assertEqual(2, guard.count_marker_calls(synthetic, "applySignature"))

        indirect = '''
        String address = "0x00411630";
        String name = "CMonitor__IntegrateMovementAgainstTerrain";
        applySignature(address, name, "__thiscall");
        '''
        self.assertTrue(guard.contains_forbidden_pair(indirect, "0x00411630", SUPERSEDED["0x00411630"]))

        concatenated = '''
        String address = "0x0041" + "1630";
        String name = "CMonitor__IntegrateMovement" + "AgainstTerrain";
        applySignature(address, name, "__thiscall");
        '''
        self.assertEqual([], guard.extract_literal_mutation_pairs(concatenated, "applySignature"))
        self.assertEqual(1, guard.count_marker_calls(concatenated, "applySignature"))


if __name__ == "__main__":
    unittest.main()
