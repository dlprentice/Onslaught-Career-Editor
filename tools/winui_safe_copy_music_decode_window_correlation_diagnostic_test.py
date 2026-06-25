#!/usr/bin/env python3
"""Tests for the music decode-window/sliding-source replay diagnostic."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_music_decode_window_correlation_diagnostic as diagnostic
from winui_safe_copy_music_audible_output_materializer_test import write_audio_json
from winui_safe_copy_music_rejected_replay_diagnostic_check_test import timeline_fixture, write_json


class MusicDecodeWindowCorrelationDiagnosticTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> dict[str, Path]:
        clean_audio = write_audio_json(
            root / "clean" / "cleanBaseline.json",
            start="2026-06-24T18:49:58Z",
            end="2026-06-24T18:52:10Z",
            non_silent=True,
        )
        staged_audio = write_audio_json(
            root / "staged" / "stagedPositive.json",
            start="2026-06-24T18:50:58Z",
            end="2026-06-24T18:52:10Z",
            non_silent=True,
        )
        clean_live = write_json(root / "clean" / "live.json", {"schemaVersion": "winui-safe-copy-live-runtime-smoke.v1"})
        staged_live = write_json(root / "staged" / "live.json", {"schemaVersion": "winui-safe-copy-live-runtime-smoke.v1"})
        clean_timeline = write_json(root / "clean" / "timeline.json", timeline_fixture(clean_live, role="cleanBaseline"))
        staged_timeline = write_json(root / "staged" / "timeline.json", timeline_fixture(staged_live, role="stagedPositive"))
        source_root = root / "source-game"
        (source_root / "data" / "Music").mkdir(parents=True)
        (source_root / "data" / "Music" / "BEA_04(Master).ogg").write_bytes(b"OggS-target")
        (source_root / "data" / "Music" / "BEA_02(Master).ogg").write_bytes(b"OggS-replacement")
        out = root / "out"
        out.mkdir()
        return {
            "clean_audio": clean_audio,
            "staged_audio": staged_audio,
            "clean_timeline": clean_timeline,
            "staged_timeline": staged_timeline,
            "source_root": source_root,
            "allowed_output_root": out,
            "output": out / "decode-window-correlation.json",
        }

    def test_builds_sanitized_replay_diagnostic_without_promoting_audible_proof(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-decode-window-") as temp_dir:
            paths = self.build_fixture(Path(temp_dir))

            def fake_runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                self.assertEqual(diagnostic.RUNNER_TIMEOUT_SECONDS, kwargs["timeout"])
                self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
                output_json = Path(command[command.index("--") + 1])
                output_json.write_text(json.dumps(diagnostic.runner_fixture()), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            artifact = diagnostic.build_diagnostic(
                clean_audio=paths["clean_audio"],
                staged_audio=paths["staged_audio"],
                clean_timeline=paths["clean_timeline"],
                staged_timeline=paths["staged_timeline"],
                source_root=paths["source_root"],
                allowed_output_root=paths["allowed_output_root"],
                output=paths["output"],
                runner_invoker=fake_runner,
            )

            summary = diagnostic.validate_artifact(artifact)
            self.assertEqual("winui-safe-copy-music-decode-window-correlation-diagnostic.v1", summary["schema"])
            self.assertFalse(summary["runtimeAudibleOutputProof"])
            self.assertEqual("BEA_04(Master).ogg", summary["cleanBestMatch"])
            self.assertEqual("BEA_02(Master).ogg", summary["stagedBestMatch"])
            self.assertIn("not materializer input", summary["nonClaims"])
            rendered = json.dumps(artifact)
            self.assertNotIn(str(paths["source_root"]), rendered)
            self.assertNotIn(str(paths["allowed_output_root"]), rendered)
            self.assertNotIn("outputWav", rendered)
            self.assertNotIn("samples", rendered)
            self.assertNotIn("sourcePath", rendered)

    def test_rejects_private_path_leak_from_runner(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-decode-window-") as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            payload = diagnostic.runner_fixture()
            payload["analysisRows"][0]["privatePath"] = str(paths["source_root"])
            with self.assertRaises(diagnostic.DecodeWindowCorrelationError):
                diagnostic.validate_runner_payload(payload)

    def test_all_skipped_rows_are_unavailable_not_measured_preference(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-decode-window-") as temp_dir:
            paths = self.build_fixture(Path(temp_dir))

            def fake_runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                payload = diagnostic.runner_fixture()
                payload["analysisRows"] = [
                    {
                        "role": "cleanBaseline",
                        "captureOffsetMs": -4000,
                        "skipped": True,
                        "skipReason": "capture-window-out-of-range",
                    },
                    {
                        "role": "cleanBaseline",
                        "captureOffsetMs": 0,
                        "skipped": True,
                        "skipReason": "capture-window-out-of-range",
                    },
                    {
                        "role": "stagedPositive",
                        "captureOffsetMs": -4000,
                        "skipped": True,
                        "skipReason": "capture-window-out-of-range",
                    },
                    {
                        "role": "stagedPositive",
                        "captureOffsetMs": 0,
                        "skipped": True,
                        "skipReason": "capture-window-out-of-range",
                    },
                ]
                output_json = Path(command[command.index("--") + 1])
                output_json.write_text(json.dumps(payload), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            artifact = diagnostic.build_diagnostic(
                clean_audio=paths["clean_audio"],
                staged_audio=paths["staged_audio"],
                clean_timeline=paths["clean_timeline"],
                staged_timeline=paths["staged_timeline"],
                source_root=paths["source_root"],
                allowed_output_root=paths["allowed_output_root"],
                output=paths["output"],
                runner_invoker=fake_runner,
            )

            summary = diagnostic.validate_artifact(artifact)
            self.assertFalse(summary["decodeWindowInsideRawAudioCapture"])
            self.assertEqual("unavailable", summary["cleanBestMatch"])
            self.assertEqual("unavailable", summary["stagedBestMatch"])
            self.assertFalse(summary["stagedReplacementPreferredInDecodeWindow"])
            self.assertEqual("decode-window unavailable inside raw audio capture", artifact["diagnosticConclusion"])
            self.assertEqual(2, artifact["skippedRowCounts"]["cleanBaseline"])
            self.assertEqual(2, artifact["skippedRowCounts"]["stagedPositive"])
            self.assertEqual(2, artifact["skippedRowCounts"]["cleanBaselineTotal"])
            self.assertEqual(2, artifact["skippedRowCounts"]["stagedPositiveTotal"])

    def test_rejects_output_under_source_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-decode-window-") as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["allowed_output_root"] = paths["source_root"] / "out"
            paths["allowed_output_root"].mkdir()
            with self.assertRaises(diagnostic.DecodeWindowCorrelationError):
                diagnostic.build_diagnostic(
                    clean_audio=paths["clean_audio"],
                    staged_audio=paths["staged_audio"],
                    clean_timeline=paths["clean_timeline"],
                    staged_timeline=paths["staged_timeline"],
                    source_root=paths["source_root"],
                    allowed_output_root=paths["allowed_output_root"],
                    output=paths["allowed_output_root"] / "decode-window-correlation.json",
                    runner_invoker=lambda *args, **kwargs: subprocess.CompletedProcess([], 0),
                )

    def test_self_test_runs(self) -> None:
        diagnostic.self_test()


if __name__ == "__main__":
    unittest.main()
