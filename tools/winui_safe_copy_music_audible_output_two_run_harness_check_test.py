#!/usr/bin/env python3
"""Tests for the two-run safe-copy music audible-output proof harness checker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_music_audible_output_two_run_harness_check as checker


class MusicAudibleOutputTwoRunHarnessCheckTests(unittest.TestCase):
    def test_positive_fixture_validates_required_proof_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            summary = checker.validate_artifact(payload)

        self.assertEqual("winui-safe-copy-music-audible-output-proof.v1", summary["schema"])
        self.assertEqual("use-bea02-for-bea04", summary["presetId"])
        self.assertEqual(100, summary["levelId"])
        self.assertTrue(summary["runtimeAudibleOutputProof"])
        self.assertTrue(summary["positiveDiffersFromCleanBaseline"])

    def test_missing_clean_baseline_difference_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir), positive_differs_from_baseline=False)

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_silent_clean_baseline_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            payload["runs"]["cleanBaseline"]["audioCapture"]["audioStats"]["nonSilent"] = False

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_missing_cdb_decode_on_baseline_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir), clean_has_decode=False)

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_capture_window_must_cover_cdb_decode_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            payload["runs"]["stagedPositive"]["audioCapture"]["captureStartedUtc"] = "2026-06-22T00:00:03Z"

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_endpoint_or_format_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            payload["runs"]["stagedPositive"]["audioCapture"]["sanitizedEndpoint"]["endpointFingerprint"] = "b" * 64

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_raw_device_identifier_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            payload["runs"]["cleanBaseline"]["audioCapture"]["deviceStableId"] = "SWD\\MMDEVAPI\\{private-endpoint-guid}"

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_missing_negative_controls_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir), include_controls=False)

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_weak_source_audio_correlation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir), source_audio_correlation=False)

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_source_audio_margin_below_minimum_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            payload["sourceAudioCorrelation"]["cleanBaselineMargin"] = 0.01

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_source_audio_private_payload_publication_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir))
            payload["sourceAudioCorrelation"]["rawAudioPublished"] = True

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)

    def test_source_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = checker.fixture(Path(temp_dir), source_hashes_unchanged=False)

        with self.assertRaises(checker.ProofError):
            checker.validate_artifact(payload)


if __name__ == "__main__":
    unittest.main()
