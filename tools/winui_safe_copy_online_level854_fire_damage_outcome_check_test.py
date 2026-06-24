#!/usr/bin/env python3
"""Focused tests for level-854 fire-to-damage/outcome observer semantics."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_level854_fire_damage_outcome_bundle as builder
import winui_safe_copy_online_level854_fire_damage_outcome_check as checker


class Level854FireDamageOutcomeCheckerTests(unittest.TestCase):
    def test_accepts_fire_observer_without_damage_or_outcome(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            summary = checker.validate_bundle(checker.make_fixture(Path(tmp)), allow_fixture=True)
            self.assertGreater(summary["button19DispatchCount"], 0)
            self.assertGreater(summary["sameWindowFireHandoffWindowCount"], 0)
            self.assertGreater(summary["sameWindowFireBurstPointerChainWindowCount"], 0)
            self.assertEqual(summary["sameWindowUnitApplyDamageWindowCount"], 0)
            self.assertFalse(summary["damageProof"])
            self.assertFalse(summary["runtimeOutcomeProof"])

    def test_promotes_damage_only_with_same_window_unit_damage_and_wait_negative(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            summary = checker.validate_bundle(
                checker.make_fixture(Path(tmp), unit_damage=True, round_collision=True),
                allow_fixture=True,
            )
            self.assertTrue(summary["damageProof"])
            self.assertFalse(summary["runtimeOutcomeProof"])
            self.assertGreater(summary["sameWindowDamageSurfaceWindowCount"], 0)

    def test_promotes_damage_and_outcome_only_when_same_window(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            summary = checker.validate_bundle(
                checker.make_fixture(Path(tmp), unit_damage=True, round_collision=True, outcome=True),
                allow_fixture=True,
            )
            self.assertTrue(summary["damageProof"])
            self.assertTrue(summary["runtimeOutcomeProof"])
            self.assertTrue(summary["fireToDamageOutcomePromotion"])

    def test_wait_window_damage_blocks_damage_promotion(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            summary = checker.validate_bundle(
                checker.make_fixture(Path(tmp), unit_damage=True, wait_damage=True),
                allow_fixture=True,
            )
            self.assertGreater(summary["waitWindowDamageHitCount"], 0)
            self.assertFalse(summary["damageProof"])

    def test_wait_window_outcome_blocks_outcome_promotion(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            summary = checker.validate_bundle(
                checker.make_fixture(Path(tmp), unit_damage=True, outcome=True, wait_outcome=True),
                allow_fixture=True,
            )
            self.assertGreater(summary["waitWindowOutcomeHitCount"], 0)
            self.assertFalse(summary["runtimeOutcomeProof"])

    def test_rejects_missing_fire_prerequisites(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for kwargs in ({"no_button19": True}, {"no_fire": True}, {"no_pointer_chain": True}):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                with self.assertRaises(builder.Level854FireDamageOutcomeBuildError):
                    checker.make_fixture(Path(tmp), **kwargs)

    def test_rejects_external_cdb_wrong_command_and_background_input(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for kwargs in ({"external_cdb_log": True}, {"wrong_command_file": True}):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                with self.assertRaises(builder.Level854FireDamageOutcomeBuildError):
                    checker.make_fixture(Path(tmp), **kwargs)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp), background_window_messages=True)
            with self.assertRaises(checker.Level854FireDamageOutcomeError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_online_overclaims(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for section, key in (
            ("nonClaims", "baseOnlineMultiplayerReady"),
            ("nonClaims", "nativeBeaNetcodeProof"),
            ("slotBoundary", "activeP3P4OriginalBinaryGameplayProof"),
        ):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                path = checker.make_fixture(Path(tmp))
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload[section][key] = True
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(checker.Level854FireDamageOutcomeError):
                    checker.validate_bundle(path, allow_fixture=True)

    def test_public_json_guard_rejects_raw_runtime_identity(self) -> None:
        checker.require_public_json_release_boundary(
            {
                "fireDamageOutcome": {
                    "damageProof": False,
                    "runtimeOutcomeProof": False,
                },
                "releaseBoundary": {
                    "rawRuntimePointerPublishedInPublicDocs": False,
                },
            }
        )
        for payload in (
            {"fireDamageOutcome": {"damageSource": "04aa0000"}},
            {"runtimeEvidence": {"pid": 1234}},
            {"sourceArtifacts": {"logPath": "C:/Users/david/private/cdb.log"}},
            {"identity": "04aa0000"},
        ):
            with self.assertRaises(checker.Level854FireDamageOutcomeError):
                checker.require_public_json_release_boundary(payload)

    def test_rejects_private_tools_in_public_allowlist(self) -> None:
        classification = "\n".join(
            list(checker.PUBLIC_RELEASE_ALLOW_ROWS) + list(checker.PRIVATE_RELEASE_DENY_ROWS)
        )
        public_allowlist = "\n".join(
            list(checker.PUBLIC_RELEASE_ALLOW_ROWS)
            + ["tools/winui_safe_copy_online_level854_fire_damage_outcome_check.py\tR4_DENY"]
        )
        private_inventory = "\n".join(checker.PRIVATE_RELEASE_DENY_ROWS)
        release_profile = "\n".join(row.split("\t", 1)[0] for row in checker.PRIVATE_RELEASE_DENY_ROWS)
        with self.assertRaises(checker.Level854FireDamageOutcomeError):
            checker.require_release_boundaries(
                classification,
                public_allowlist,
                private_inventory,
                release_profile,
            )


if __name__ == "__main__":
    unittest.main()
