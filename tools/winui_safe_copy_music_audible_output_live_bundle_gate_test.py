#!/usr/bin/env python3
"""Tests for the music audible-output live raw-bundle gate."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_music_audible_output_live_bundle_gate as gate


class MusicAudibleOutputLiveBundleGateTests(unittest.TestCase):
    def test_gate_records_required_inputs_and_blocks_live_arm_until_runtime_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = gate.build_gate(
                artifact_root=Path(temp_dir) / "music-audible-live",
                source_root=Path(temp_dir) / "source-game",
            )

        summary = gate.validate_gate(payload)

        self.assertEqual("winui-safe-copy-music-audible-output-live-bundle-gate.v1", payload["schemaVersion"])
        self.assertFalse(payload["runtimeAudibleOutputProof"])
        self.assertTrue(payload["producerCoverageComplete"])
        self.assertFalse(payload["readyToRunLiveAttempt"])
        self.assertFalse(payload["liveArmAllowed"])
        self.assertEqual("prearm-readiness-not-proven", payload["preArmReadiness"]["status"])
        self.assertEqual(
            "RUN PRIVATE MUSIC AUDIBLE LIVE BUNDLE",
            payload["preArmReadiness"]["runtimeProofAuthority"]["requiredArmPhrase"],
        )
        self.assertEqual(
            "winui-safe-copy-music-audible-output-live-bundle-prearm-readiness.v1",
            payload["preArmReadiness"]["runtimeProofAuthority"]["privatePrearmReadinessSchema"],
        )
        self.assertTrue(payload["preArmReadiness"]["runtimeProofAuthority"]["explicitRuntimeProofAuthorityRequired"])
        self.assertEqual(
            ["bea-runtime", "cdb-debugger", "audio-loopback", "proof-root"],
            payload["preArmReadiness"]["requiredResourceLeases"],
        )
        self.assertTrue(payload["preArmReadiness"]["processPreflight"]["noPreexistingBeaOrCdbRequired"])
        self.assertTrue(payload["preArmReadiness"]["processPreflight"]["passiveProcessCensusOnly"])
        self.assertTrue(payload["preArmReadiness"]["proofRootPreflight"]["emptyIsolatedPrivateProofRootRequired"])
        self.assertTrue(payload["preArmReadiness"]["proofRootPreflight"]["localIgnoredRawProofOnly"])
        self.assertTrue(payload["preArmReadiness"]["sourceMutationPolicy"]["installedGameAndOriginalBeaReadOnly"])
        capture_span = payload["preArmReadiness"]["captureSpanDecodeWindowPreflight"]
        self.assertTrue(capture_span["captureStartedUtcStopwatchAlignmentRequired"])
        self.assertTrue(capture_span["wavWallClockDurationMustCoverCdbDecodeWindow"])
        self.assertTrue(capture_span["helperAuthoredWallClockPaddingMetadataRequired"])
        self.assertTrue(capture_span["capturedBytesPlusSilencePaddingBytesMustEqualBytesRecorded"])
        self.assertTrue(capture_span["canonicalWavHeaderAndDataFrameConsistencyRequired"])
        self.assertTrue(capture_span["outOfRangeDecodeWindowRejectedByMaterializer"])
        failure_policy = payload["preArmReadiness"]["readinessFailurePolicy"]
        self.assertEqual("runtimeAudibleOutputProof", failure_policy["proofBooleanForcedFalse"])
        self.assertIn("audible-output proof", failure_policy["forbiddenFailureClaimText"])
        self.assertEqual(13, summary["requiredRawInputCount"])
        self.assertEqual(0, summary["unresolvedProducerGapCount"])
        self.assertFalse(payload["producerGapBlocksLiveAttempt"])
        self.assertEqual("<private-proof-root>\\music-audible-live", payload["artifactRootHint"])
        self.assertEqual("<read-only-source-game-root>", payload["sourceRootHint"])
        self.assertNotIn("artifactRoot", payload)
        self.assertNotIn("sourceRoot", payload)
        self.assertNotIn("preferredPrivateRuntimeProofRoot", payload)
        self.assertEqual(
            [
                "cleanLive",
                "stagedLive",
                "muteLive",
                "cleanTimeline",
                "stagedTimeline",
                "cleanSourceMusicSafety",
                "muteSourceMusicSafety",
                "ambientCensus",
                "ambientAudio",
                "cleanAudio",
                "stagedAudio",
                "muteAudio",
                "captureSourceCorrelation",
            ],
            [item["key"] for item in payload["requiredRawInputs"]],
        )
        self.assertEqual([], payload["unresolvedProducerGaps"])
        clean_safety = next(item for item in payload["requiredRawInputs"] if item["key"] == "cleanSourceMusicSafety")
        mute_safety = next(item for item in payload["requiredRawInputs"] if item["key"] == "muteSourceMusicSafety")
        self.assertEqual(r"tools\winui_safe_copy_music_source_music_safety_sidecar.py", clean_safety["producer"])
        self.assertEqual(r"tools\winui_safe_copy_music_source_music_safety_sidecar.py", mute_safety["producer"])
        ambient = next(item for item in payload["requiredRawInputs"] if item["key"] == "ambientCensus")
        self.assertEqual(r"tools\winui_safe_copy_music_ambient_no_bea_census.py", ambient["producer"])
        capture_correlation = next(item for item in payload["requiredRawInputs"] if item["key"] == "captureSourceCorrelation")
        self.assertEqual(r"tools\winui_safe_copy_music_capture_source_correlation_builder.py", capture_correlation["producer"])
        self.assertIn("npm run test:winui-safe-copy-music-timestamped-cdb-log-producer", payload["preflightCommands"])
        self.assertIn("py -3 tools\\winui_safe_copy_music_audible_output_materializer.py", " ".join(payload["promotionCommandTemplate"]))
        serialized = json_dump(payload)
        self.assertNotIn("Program Files", serialized)
        self.assertNotIn("steamapps", serialized)
        self.assertNotIn("G:\\", serialized)
        self.assertNotIn("C:\\", serialized)

    def test_gate_rejects_proof_claims_and_reintroduced_producer_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = gate.build_gate(
                artifact_root=Path(temp_dir) / "music-audible-live",
                source_root=Path(temp_dir) / "source-game",
            )

        claimed = copy.deepcopy(payload)
        claimed["runtimeAudibleOutputProof"] = True
        with self.assertRaises(gate.MusicAudibleOutputLiveBundleGateError):
            gate.validate_gate(claimed)

        extra_gap = copy.deepcopy(payload)
        extra_gap["unresolvedProducerGaps"] = [{"id": "timestamped-cdb-log-producer"}]
        with self.assertRaises(gate.MusicAudibleOutputLiveBundleGateError):
            gate.validate_gate(extra_gap)

        blocked = copy.deepcopy(payload)
        blocked["producerGapBlocksLiveAttempt"] = True
        with self.assertRaises(gate.MusicAudibleOutputLiveBundleGateError):
            gate.validate_gate(blocked)

        falsely_armed = copy.deepcopy(payload)
        falsely_armed["liveArmAllowed"] = True
        with self.assertRaises(gate.MusicAudibleOutputLiveBundleGateError):
            gate.validate_gate(falsely_armed)

        extra_claim = copy.deepcopy(payload)
        extra_claim["runtimeAudioProof"] = True
        with self.assertRaises(gate.MusicAudibleOutputLiveBundleGateError):
            gate.validate_gate(extra_claim)

        missing_lease = copy.deepcopy(payload)
        missing_lease["preArmReadiness"]["requiredResourceLeases"].remove("proof-root")
        with self.assertRaises(gate.MusicAudibleOutputLiveBundleGateError):
            gate.validate_gate(missing_lease)

    def test_cli_self_test_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(Path(gate.__file__)), "--self-test"],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("live-bundle-gate self-test passed", result.stdout)


def json_dump(payload: dict[str, object]) -> str:
    import json

    return json.dumps(payload, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
