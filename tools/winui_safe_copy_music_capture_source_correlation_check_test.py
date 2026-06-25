#!/usr/bin/env python3
"""Tests for the music capture-to-source correlation adapter checker."""

from __future__ import annotations

import unittest

import winui_safe_copy_music_capture_source_correlation_check as checker


class MusicCaptureSourceCorrelationCheckTests(unittest.TestCase):
    def test_positive_fixture_validates_and_emits_harness_adapter(self) -> None:
        payload = checker.fixture()
        summary = checker.validate_artifact(payload)

        self.assertEqual("winui-safe-copy-music-capture-source-correlation.v1", summary["schema"])
        self.assertEqual("use-bea02-for-bea04", summary["presetId"])
        self.assertEqual("BEA_04(Master).ogg", summary["cleanBaselineBestMatch"])
        self.assertEqual("BEA_02(Master).ogg", summary["stagedPositiveBestMatch"])
        self.assertEqual(payload["sourceAudioCorrelation"], summary["sourceAudioCorrelation"])
        self.assertFalse(summary["runtimeAudibleOutputProof"])

    def test_runtime_audible_output_claim_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["runtimeAudibleOutputProof"] = True

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_private_path_leak_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["captureAnalysis"]["cleanBaselinePath"] = (
            r"C:\Users\david\source\Onslaught-Career-Editor-private\subagents\capture.wav"
        )

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_raw_audio_payload_leak_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["captureAnalysis"]["spectrogramBins"] = [0.1, 0.2, 0.3]

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_weak_clean_baseline_margin_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["sourceAudioCorrelation"]["cleanBaselineMargin"] = 0.04
        payload["sourceAudioCorrelation"]["scoreMatrix"]["cleanBaselineVsTarget"] = 0.54
        payload["sourceAudioCorrelation"]["scoreMatrix"]["cleanBaselineVsReplacement"] = 0.50

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_score_matrix_must_match_declared_best_matches(self) -> None:
        payload = checker.fixture()
        payload["sourceAudioCorrelation"]["scoreMatrix"]["cleanBaselineVsTarget"] = 0.20
        payload["sourceAudioCorrelation"]["scoreMatrix"]["cleanBaselineVsReplacement"] = 0.90

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_preference_booleans_must_match_scores(self) -> None:
        payload = checker.fixture()
        payload["sourceAudioCorrelation"]["stagedPositiveReplacementCorrelationGtTarget"] = False

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_active_window_count_too_small_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["captureAnalysis"]["cleanBaselineActiveWindowCount"] = 4

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_rms_peak_only_method_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["captureAnalysis"]["method"] = "rms-peak-delta"
        payload["sourceAudioCorrelation"]["method"] = "rms-peak-delta"

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_missing_adapter_non_claim_fails_closed(self) -> None:
        payload = checker.fixture()
        payload["nonClaims"].remove("not standalone audible-output proof")

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(payload)

    def test_rejection_fixture_validates_as_local_diagnostic_only(self) -> None:
        payload = checker.rejection_fixture()
        summary = checker.validate_rejection_diagnostic(payload)

        self.assertEqual("winui-safe-copy-music-capture-source-correlation-rejection.v1", summary["schema"])
        self.assertEqual("rejected", summary["status"])
        self.assertEqual("staged-positive-source-correlation-margin-too-weak", summary["rejectionReason"])
        self.assertFalse(summary["runtimeAudibleOutputProof"])

    def test_rejection_fixture_is_not_accepted_adapter(self) -> None:
        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_artifact(checker.rejection_fixture())

    def test_rejection_diagnostic_rejects_accepted_adapter_shape(self) -> None:
        payload = checker.rejection_fixture()
        payload["sourceAudioCorrelation"] = {}

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_rejection_diagnostic(payload)

    def test_rejection_diagnostic_private_path_leak_fails_closed(self) -> None:
        payload = checker.rejection_fixture()
        payload["sanitizedError"] = r"failed at C:\Users\david\private\capture.wav"

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_rejection_diagnostic(payload)

    def test_rejection_diagnostic_reason_must_match_margin(self) -> None:
        payload = checker.rejection_fixture()
        payload["rejectionReason"] = "clean-baseline-source-correlation-margin-too-weak"

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_rejection_diagnostic(payload)

    def test_rejection_diagnostic_raw_payload_key_fails_closed(self) -> None:
        payload = checker.rejection_fixture()
        payload["sourceAudioCorrelationDiagnostics"]["samples"] = [0, 1]

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_rejection_diagnostic(payload)

    def test_rejection_diagnostic_requires_materializer_non_claim(self) -> None:
        payload = checker.rejection_fixture()
        payload["nonClaims"] = [item for item in payload["nonClaims"] if item != "not materializer input"]

        with self.assertRaises(checker.CorrelationAdapterError):
            checker.validate_rejection_diagnostic(payload)


if __name__ == "__main__":
    unittest.main()
