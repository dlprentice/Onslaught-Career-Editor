#!/usr/bin/env python3
"""Tests for the music capture-to-source correlation builder."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_music_capture_source_correlation_builder as builder
import winui_safe_copy_music_capture_source_correlation_check as checker
from winui_safe_copy_music_audible_output_materializer_test import sha256_file, write_audio_json


class MusicCaptureSourceCorrelationBuilderTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> dict[str, Path]:
        clean_audio = write_audio_json(
            root / "clean" / "audio.json",
            start="2026-06-22T00:00:00Z",
            end="2026-06-22T00:00:03Z",
            non_silent=True,
        )
        staged_audio = write_audio_json(
            root / "staged" / "audio.json",
            start="2026-06-22T00:00:00Z",
            end="2026-06-22T00:00:03Z",
            non_silent=True,
        )
        return {
            "clean_audio": clean_audio,
            "staged_audio": staged_audio,
            "source_root": root / "source-game",
            "allowed_output_root": root / "out",
            "output": root / "out" / "capture-source-correlation.json",
        }

    def test_builds_checker_accepted_adapter_from_bounded_vectors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["allowed_output_root"].mkdir(parents=True)
            paths["source_root"].mkdir(parents=True)

            artifact = builder.build_adapter_from_vectors(
                clean_audio=paths["clean_audio"],
                staged_audio=paths["staged_audio"],
                output=paths["output"],
                allowed_output_root=paths["allowed_output_root"],
                source_root=paths["source_root"],
                source_target_vector=[1.0, 0.0, 0.0, 0.0],
                source_replacement_vector=[0.0, 1.0, 0.0, 0.0],
                clean_capture_vector=[0.95, 0.05, 0.0, 0.0],
                staged_capture_vector=[0.05, 0.95, 0.0, 0.0],
            )

            summary = checker.validate_artifact(artifact)
            self.assertEqual("BEA_04(Master).ogg", summary["cleanBaselineBestMatch"])
            self.assertEqual("BEA_02(Master).ogg", summary["stagedPositiveBestMatch"])
            self.assertFalse(summary["runtimeAudibleOutputProof"])
            self.assertEqual(sha256_file(paths["clean_audio"]), summary["inputBindings"]["cleanAudioJsonSha256"])
            self.assertEqual(sha256_file(Path(json.loads(paths["clean_audio"].read_text())["outputWav"])), summary["inputBindings"]["cleanAudioWavSha256"])
            self.assertTrue(paths["output"].is_file())
            rendered = json.dumps(artifact)
            self.assertNotIn(str(paths["source_root"]), rendered)
            self.assertNotIn("outputWav", rendered)
            self.assertNotIn("samples", rendered)

    def test_rejects_swapped_capture_preference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["allowed_output_root"].mkdir(parents=True)
            paths["source_root"].mkdir(parents=True)

            with self.assertRaises(builder.CaptureSourceCorrelationBuilderError):
                builder.build_adapter_from_vectors(
                    clean_audio=paths["clean_audio"],
                    staged_audio=paths["staged_audio"],
                    output=paths["output"],
                    allowed_output_root=paths["allowed_output_root"],
                    source_root=paths["source_root"],
                    source_target_vector=[1.0, 0.0, 0.0, 0.0],
                    source_replacement_vector=[0.0, 1.0, 0.0, 0.0],
                    clean_capture_vector=[0.05, 0.95, 0.0, 0.0],
                    staged_capture_vector=[0.95, 0.05, 0.0, 0.0],
                )

    def test_rejects_weak_margin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["allowed_output_root"].mkdir(parents=True)
            paths["source_root"].mkdir(parents=True)

            with self.assertRaises(builder.CaptureSourceCorrelationBuilderError):
                builder.build_adapter_from_vectors(
                    clean_audio=paths["clean_audio"],
                    staged_audio=paths["staged_audio"],
                    output=paths["output"],
                    allowed_output_root=paths["allowed_output_root"],
                    source_root=paths["source_root"],
                    source_target_vector=[1.0, 0.0, 0.0, 0.0],
                    source_replacement_vector=[0.0, 1.0, 0.0, 0.0],
                    clean_capture_vector=[0.53, 0.47, 0.0, 0.0],
                    staged_capture_vector=[0.47, 0.53, 0.0, 0.0],
                )

    def test_rejects_output_inside_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["allowed_output_root"] = paths["source_root"] / "out"
            paths["output"] = paths["allowed_output_root"] / "capture-source-correlation.json"
            paths["allowed_output_root"].mkdir(parents=True)

            with self.assertRaises(builder.CaptureSourceCorrelationBuilderError):
                builder.build_adapter_from_vectors(
                    clean_audio=paths["clean_audio"],
                    staged_audio=paths["staged_audio"],
                    output=paths["output"],
                    allowed_output_root=paths["allowed_output_root"],
                    source_root=paths["source_root"],
                    source_target_vector=[1.0, 0.0, 0.0, 0.0],
                    source_replacement_vector=[0.0, 1.0, 0.0, 0.0],
                    clean_capture_vector=[0.95, 0.05, 0.0, 0.0],
                    staged_capture_vector=[0.05, 0.95, 0.0, 0.0],
                )

    def test_path_mode_uses_temp_runner_without_leaking_intermediates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["allowed_output_root"].mkdir(parents=True)
            music_root = paths["source_root"] / "data" / "Music"
            music_root.mkdir(parents=True)
            (music_root / "BEA_04(Master).ogg").write_bytes(b"OggS-target")
            (music_root / "BEA_02(Master).ogg").write_bytes(b"OggS-replacement")

            def fake_runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                self.assertEqual(builder.RUNNER_TIMEOUT_SECONDS, kwargs["timeout"])
                child_env = kwargs["env"]
                self.assertIsInstance(child_env, dict)
                self.assertNotIn("OPENAI_API_KEY", child_env)
                vector_path = Path(command[command.index("--") + 1])
                vector_path.write_text(
                    json.dumps(
                        {
                            "sourceTargetVector": [1.0, 0.0, 0.0, 0.0],
                            "sourceReplacementVector": [0.0, 1.0, 0.0, 0.0],
                            "cleanCaptureVector": [0.95, 0.05, 0.0, 0.0],
                            "stagedCaptureVector": [0.05, 0.95, 0.0, 0.0],
                        }
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout=f"private {paths['source_root']}", stderr="")

            artifact = builder.build_adapter_from_paths(
                clean_audio=paths["clean_audio"],
                staged_audio=paths["staged_audio"],
                output=paths["output"],
                allowed_output_root=paths["allowed_output_root"],
                source_root=paths["source_root"],
                runner_invoker=fake_runner,
            )

            summary = checker.validate_artifact(artifact)
            self.assertEqual("BEA_04(Master).ogg", summary["cleanBaselineBestMatch"])
            self.assertTrue(paths["output"].is_file())
            self.assertFalse(any(paths["allowed_output_root"].glob("capture-source-correlation-runner*")))
            self.assertFalse((paths["allowed_output_root"] / "capture-source-correlation-vectors.json").exists())
            self.assertFalse((paths["allowed_output_root"] / "capture-source-correlation-runner-stdout.log").exists())
            rendered = json.dumps(artifact)
            self.assertNotIn(str(paths["source_root"]), rendered)

    def test_self_test_runs(self) -> None:
        builder.self_test()


if __name__ == "__main__":
    unittest.main()
