#!/usr/bin/env python3
"""Focused tests for level-854 input-assisted outcome transition proof semantics."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_level854_input_assisted_outcome_bundle as builder
import winui_safe_copy_online_level854_input_assisted_outcome_check as checker


class Level854InputAssistedOutcomeCheckerTests(unittest.TestCase):
    def test_accepts_stimulus_attempt_without_outcome_transition(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp), transition_in_stimulus_window=False)
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertTrue(summary["inputAssistedOutcomeAttempted"])
            self.assertTrue(summary["stimulusAttemptOnly"])
            self.assertEqual(summary["inputWindowOutcomeTransitionHitCount"], 0)
            self.assertFalse(summary["runtimeOutcomeProof"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])

    def test_accepts_transition_only_inside_stimulus_window_as_runtime_outcome_proof(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp), transition_in_stimulus_window=True)
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertTrue(summary["inputAssistedOutcomeAttempted"])
            self.assertFalse(summary["stimulusAttemptOnly"])
            self.assertGreater(summary["inputWindowOutcomeTransitionHitCount"], 0)
            self.assertTrue(summary["runtimeOutcomeProof"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])

    def test_rejects_wait_window_outcome_transition_as_causal_proof(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854InputAssistedOutcomeBuildError):
                checker.make_fixture(Path(tmp), transition_in_wait_window=True)

    def test_rejects_stimulus_transition_without_same_window_input_assist(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854InputAssistedOutcomeBuildError):
                checker.make_fixture(
                    Path(tmp),
                    transition_in_stimulus_window=True,
                    transition_without_input_assist=True,
                )

    def test_rejects_external_cdb_log_path(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854InputAssistedOutcomeBuildError):
                checker.make_fixture(Path(tmp), external_cdb_log=True)

    def test_rejects_wrong_cdb_command_file_path(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854InputAssistedOutcomeBuildError):
                checker.make_fixture(Path(tmp), wrong_command_file=True)

    def test_rejects_background_window_message_input(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp), background_window_messages=True)
            with self.assertRaises(checker.Level854InputAssistedOutcomeError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_online_native_netcode_or_p3p4_claims(self) -> None:
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
                with self.assertRaises(checker.Level854InputAssistedOutcomeError):
                    checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_public_text_overclaim_tokens(self) -> None:
        good_text = " ".join(checker.PUBLIC_REQUIRED_FALSE_TOKENS)
        checker.require_public_claim_tokens(good_text, "fixture")
        with self.assertRaises(checker.Level854InputAssistedOutcomeError):
            checker.require_public_claim_tokens(
                good_text + " baseOnlineMultiplayerReady=true",
                "fixture",
            )

    def test_rejects_private_level854_tools_in_public_allowlist(self) -> None:
        classification = "\n".join(
            list(checker.PUBLIC_RELEASE_ALLOW_ROWS) + list(checker.PRIVATE_RELEASE_DENY_ROWS)
        )
        public_allowlist = "\n".join(
            list(checker.PUBLIC_RELEASE_ALLOW_ROWS)
            + ["tools/winui_safe_copy_online_level854_input_assisted_outcome_check.py\tR4_DENY"]
        )
        private_inventory = "\n".join(checker.PRIVATE_RELEASE_DENY_ROWS)
        release_profile = "\n".join(row.split("\t", 1)[0] for row in checker.PRIVATE_RELEASE_DENY_ROWS)
        with self.assertRaises(checker.Level854InputAssistedOutcomeError):
            checker.require_release_boundaries(
                classification,
                public_allowlist,
                private_inventory,
                release_profile,
            )


if __name__ == "__main__":
    unittest.main()
