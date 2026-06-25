#!/usr/bin/env python3
"""Tests for the rejected music audible-output replay diagnostic."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import winui_safe_copy_music_capture_source_correlation_check as correlation_check
import winui_safe_copy_music_rejected_replay_diagnostic_check as diagnostic
import winui_safe_copy_music_swap_preset_artifact_check as preset_check


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def clean_live_fixture() -> dict[str, Any]:
    payload = preset_check.fixture("use-bea02-for-bea04")
    payload["musicReplacement"] = None
    payload["launch"]["arguments"] = ["-skipfmv", "-level", "100"]
    payload["claimBoundary"] = "Clean same-level launch/capture/stop only; does not prove audible playback."
    return payload


def staged_live_fixture() -> dict[str, Any]:
    payload = preset_check.fixture("use-bea02-for-bea04")
    second_capture = dict(payload["captures"][0])
    second_capture["fileSize"] = int(second_capture["fileSize"]) + 1
    payload["captures"].append(second_capture)
    return payload


def timeline_fixture(live_path: Path, *, role: str) -> dict[str, Any]:
    return {
        "schemaVersion": "winui-safe-copy-music-cdb-decode-timeline.v1",
        "role": role,
        "timestampSource": "timestamped-cdb-log",
        "cdbLogTimestamped": True,
        "liveArtifactSha256": diagnostic.sha256_file(live_path),
        "rawCdbLogSha256": "a" * 64,
        "timestampedCdbLogPath": str(live_path.parent / "windbg.timestamped.log"),
        "timestampedCdbLogSha256": "b" * 64,
        "cdbLogSha256": "b" * 64,
        "exactPidCdbObserver": True,
        "levelId": 100,
        "selectionId": 2,
        "musicSelectionProvenance": "cgame-restart-loop-direct",
        "playMusicForCurrentLevelObserved": False,
        "restartLoopDirectMusicSelectionObserved": True,
        "playSelectionObserved": True,
        "asyncKickPathMatched": True,
        "oggOpenPathMatched": True,
        "decodedPcmPositiveRequestObserved": True,
        "decodeWindowStartUtc": "2026-06-24T18:51:00.000Z",
        "decodeWindowEndUtc": "2026-06-24T18:51:02.000Z",
        "cdbEvidenceRowCounts": {
            "gameMusicRows": 0,
            "playSelectionRows": 1,
            "asyncKickRows": 1,
            "oggOpenRows": 1,
            "oggReadRows": 1,
        },
        "claimBoundary": "Timestamped CDB timeline sidecar only; not audible-output proof by itself.",
    }


class MusicRejectedReplayDiagnosticTests(unittest.TestCase):
    def test_accepts_staged_decode_with_rejected_capture_correlation_without_promoting_proof(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-rejected-replay-") as temp_dir:
            root = Path(temp_dir)
            clean_live = write_json(root / "clean" / "live.json", clean_live_fixture())
            staged_live = write_json(root / "staged" / "live.json", staged_live_fixture())
            clean_timeline = write_json(root / "clean" / "timeline.json", timeline_fixture(clean_live, role="cleanBaseline"))
            staged_timeline = write_json(root / "staged" / "timeline.json", timeline_fixture(staged_live, role="stagedPositive"))
            rejection = write_json(root / "capture-source-correlation-rejection.json", correlation_check.rejection_fixture())

            summary = diagnostic.validate_from_paths(
                clean_live=clean_live,
                staged_live=staged_live,
                clean_timeline=clean_timeline,
                staged_timeline=staged_timeline,
                rejection_diagnostic=rejection,
            )

            self.assertEqual("winui-safe-copy-music-rejected-replay-diagnostic.v1", summary["schema"])
            self.assertFalse(summary["runtimeAudibleOutputProof"])
            self.assertTrue(summary["stagedFileLayoutProven"])
            self.assertTrue(summary["exactPidDecodeTimelineProven"])
            self.assertTrue(summary["captureSourceCorrelationRejected"])
            self.assertEqual("staged-positive-source-correlation-margin-too-weak", summary["rejectionReason"])
            self.assertEqual("BEA_04(Master).ogg", summary["stagedPositiveBestMatch"])
            self.assertIn("not materializer input", summary["nonClaims"])
            rendered = json.dumps(summary)
            self.assertNotIn(str(root), rendered)
            self.assertNotIn("timestampedCdbLogPath", rendered)
            self.assertNotIn("outputWav", rendered)

    def test_rejects_timeline_not_bound_to_live_artifact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-rejected-replay-") as temp_dir:
            root = Path(temp_dir)
            clean_live = write_json(root / "clean" / "live.json", clean_live_fixture())
            staged_live = write_json(root / "staged" / "live.json", staged_live_fixture())
            clean_timeline_payload = timeline_fixture(clean_live, role="cleanBaseline")
            clean_timeline_payload["liveArtifactSha256"] = "0" * 64
            clean_timeline = write_json(root / "clean" / "timeline.json", clean_timeline_payload)
            staged_timeline = write_json(root / "staged" / "timeline.json", timeline_fixture(staged_live, role="stagedPositive"))
            rejection = write_json(root / "capture-source-correlation-rejection.json", correlation_check.rejection_fixture())

            with self.assertRaises(diagnostic.RejectedReplayDiagnosticError):
                diagnostic.validate_from_paths(
                    clean_live=clean_live,
                    staged_live=staged_live,
                    clean_timeline=clean_timeline,
                    staged_timeline=staged_timeline,
                    rejection_diagnostic=rejection,
                )

    def test_rejects_accepted_correlation_instead_of_rejection(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-rejected-replay-") as temp_dir:
            root = Path(temp_dir)
            clean_live = write_json(root / "clean" / "live.json", clean_live_fixture())
            staged_live = write_json(root / "staged" / "live.json", staged_live_fixture())
            clean_timeline = write_json(root / "clean" / "timeline.json", timeline_fixture(clean_live, role="cleanBaseline"))
            staged_timeline = write_json(root / "staged" / "timeline.json", timeline_fixture(staged_live, role="stagedPositive"))
            accepted = write_json(root / "capture-source-correlation.json", correlation_check.fixture())

            with self.assertRaises(diagnostic.RejectedReplayDiagnosticError):
                diagnostic.validate_from_paths(
                    clean_live=clean_live,
                    staged_live=staged_live,
                    clean_timeline=clean_timeline,
                    staged_timeline=staged_timeline,
                    rejection_diagnostic=accepted,
                )


if __name__ == "__main__":
    unittest.main()
