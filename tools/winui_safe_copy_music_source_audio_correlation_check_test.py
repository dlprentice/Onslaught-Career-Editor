#!/usr/bin/env python3
"""Tests for source-audio fingerprint/correlation proof helper output."""

from __future__ import annotations

import unittest

import winui_safe_copy_music_source_audio_correlation_check as checker


class SourceAudioCorrelationCheckTests(unittest.TestCase):
    def test_positive_fixture_validates_public_safe_summary(self) -> None:
        payload = checker.fixture()
        summary = checker.validate_artifact(payload)

        self.assertEqual("winui-safe-copy-music-source-audio-correlation.v1", summary["schema"])
        self.assertEqual(["BEA_02(Master).ogg", "BEA_04(Master).ogg"], summary["trackIds"])
        self.assertTrue(summary["sourceTracksDistinct"])
        self.assertFalse(summary["runtimeAudibleOutputProof"])

    def test_rejects_private_source_path_leak(self) -> None:
        payload = checker.fixture()
        payload["tracks"][0]["sourcePath"] = r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\data\Music\BEA_02(Master).ogg"

        with self.assertRaises(checker.CorrelationError):
            checker.validate_artifact(payload)

    def test_rejects_identical_fingerprints(self) -> None:
        payload = checker.fixture()
        payload["tracks"][1]["fingerprintSha256"] = payload["tracks"][0]["fingerprintSha256"]
        payload["sourcePair"]["fingerprintsDiffer"] = False

        with self.assertRaises(checker.CorrelationError):
            checker.validate_artifact(payload)

    def test_rejects_runtime_audible_output_claim(self) -> None:
        payload = checker.fixture()
        payload["runtimeAudibleOutputProof"] = True

        with self.assertRaises(checker.CorrelationError):
            checker.validate_artifact(payload)

    def test_rejects_weak_source_margin(self) -> None:
        payload = checker.fixture()
        payload["sourcePair"]["sourceDistinctMargin"] = 0.01
        payload["sourcePair"]["scoreMatrix"]["replacementVsTarget"] = 0.99
        payload["sourcePair"]["scoreMatrix"]["targetVsReplacement"] = 0.99

        with self.assertRaises(checker.CorrelationError):
            checker.validate_artifact(payload)

    def test_rejects_swapped_track_roles(self) -> None:
        payload = checker.fixture()
        payload["tracks"][0]["role"] = "target"

        with self.assertRaises(checker.CorrelationError):
            checker.validate_artifact(payload)

    def test_rejects_raw_payload_leakage(self) -> None:
        payload = checker.fixture()
        payload["tracks"][0]["rawPcmBase64"] = "AAAA"

        with self.assertRaises(checker.CorrelationError):
            checker.validate_artifact(payload)


if __name__ == "__main__":
    unittest.main()
